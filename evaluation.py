import argparse
import ast
import csv
import logging
import pandas as pd
import time
import yaml

from src.helper_llm import HelperLLM, HelperLLMViaAPI
from src.prompting.sandbox_prompts import API_DOCS, CHAT_API_EXAMPLES
from src.sandbox_handler import SandboxHandler



def parse_args():

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default="config.yaml", help="Path to the configuration file")
    parser.add_argument('--in_path', type=str, required=True, help="Path to the input TSV file")
    parser.add_argument('--out_path', type=str, required=True, help="Path to the output TSV file")

    args = parser.parse_args()
    return args


def load_llms_and_handlers(config: dict[str, dict[str, object]]) -> tuple[HelperLLM, SandboxHandler]:

    ### Create object that communicates with sandbox
    sandbox_handler = SandboxHandler.from_ifc(config['sandbox']['ifcPath'])
    logging.info("Sandbox Handler created")

    ### Create object that handles LLM for code generation and verbalization
    model_name = config['helperLLM']['model']
    openai_api_helper_url = config['helperLLM']['apiUrl']
    openai_api_key = config['helperLLM']['apiKey']
    helper_llm = HelperLLMViaAPI(
        model_name=model_name,
        openai_api_base_url=openai_api_helper_url, 
        openai_api_key=openai_api_key,
        enable_thinking=config['helperLLM']['enableThinking']
    )

    logging.info("Helper LLM client created")

    return helper_llm, sandbox_handler



def processing(input_text: str, helper_llm: HelperLLM, sandbox_handler: SandboxHandler) -> str:

    start_time = time.time()

    logging.info(f"INPUT QUERY: {input_text}")
    input_data = {
        "query": input_text,
        "api_documentation": API_DOCS,
        "api_examples": CHAT_API_EXAMPLES
    }

    python_code = helper_llm(input_data=input_data, instruction_type="sandbox_api")
    python_code_time = time.time()
    
    logging.info(f"PYTHON CODE:\n{python_code.strip()}")

    python_outcome = sandbox_handler(code=python_code)
    python_exec_time = time.time()


    input_data = {
        "query": input_text,
        # "python_code": python_code,
        "outcome": python_outcome,
    }

    final_output = helper_llm(input_data=input_data, instruction_type="sandbox_verbalization")    
    logging.info(f"OUTPUT QUERY: {final_output}")

    sandbox_handler.sandbox.text_to_speech(final_output)
    end_time = time.time()

    # logging.debug(f"TIMES: P. code {python_code_time-start_time:.2f}s - P. exec {python_exec_time-python_code_time:.2f}s - Verb. {end_time-python_exec_time:.2f}s")

    times = {
        "code_gen": f"{python_code_time-start_time:.3f}", 
        "code_exec": f"{python_exec_time-python_code_time:.3f}",
        "feedback_gen": f"{end_time-python_exec_time:.3f}"
    }
    
    return python_code.strip(), final_output, end_time - start_time, times
    
def toSemicolonCsv(in_path: str) -> str:
    path_chars = list(in_path)
    path_chars[-3] = 'c'
    out_path = ''.join(path_chars)

    with open(in_path, "r", encoding="utf-8") as f:
        hasSemicolon =  any(";" in line for line in f)
    
    if not hasSemicolon:
        df = pd.read_csv(in_path, sep='\t', encoding='utf-8')
        df.to_csv(out_path, sep=";", encoding="utf-8", index=False)
    else:
        out_path = in_path

    return out_path

def main():
    
    args = parse_args()
    logging.basicConfig(level=logging.INFO)
    with open(args.config, "r") as f:
        config = yaml.safe_load(f)
    
    helper_llm, sandbox_handler = load_llms_and_handlers(config)
    ifc_filename = config['sandbox']['ifcPath']

    in_path = toSemicolonCsv(args.in_path)

    with open(in_path, newline='', encoding='utf-8') as entrada:
        tsv_reader = csv.DictReader(entrada, delimiter=';')
        datos_salida = list(tsv_reader) 
        fieldnames = tsv_reader.fieldnames
        
        colExtras = ['Generated Code', 'Output query', 'Total time', 'Detailed time', 'Label', 'Label feedback']
        for col in colExtras:
            if col not in fieldnames:
                fieldnames.append(col)

        try:
            for row in datos_salida:
                # Check if it is already annotated
                if row.get('Label') is not None and row['Label'].strip() != '':
                    logging.info(f"Skipping row {row['ID']} as it is already labeled.")
                    continue
                
                print("\n" + "=" * 70 + "\n")
                
                # Reset the sandbox
                logging.info("Resetting the sandbox...")
                if row.get('Building') == "School":
                    ifc_filename = "data/ifc/Technical_school-current_m.ifc"
                sandbox_handler.reset_ifc(ifc_filename)
                
                logging.info(f"Processing row with ID {row['ID']}...")

                # Set the correct context for the query if it is provided
                code = row.get('Prior state')
                if code != "-":
                    logging.info("Executing prior state code...")
                    code = code.encode('ascii').decode('unicode-escape')
                    sandbox_handler(code)

                # Move the camera to the position specified
                x,y,z = ast.literal_eval(row['Position'])
                logging.info(f"Moving to position: {x}, {y}, {z}")
                sandbox_handler.sandbox.move_to(x, y, z)

                # Move the camera to the rotation specified
                pitch, yaw, roll = ast.literal_eval(row['Rotation'])
                logging.info(f"Rotating to: {pitch}, {yaw}, {roll}")
                sandbox_handler.sandbox.rotate_to(pitch, yaw, roll)
        
                # Show the query and wait for user confirmation
                print(f"\nQuery to execute: {row['Query']}")
                input("Press ENTER to execute the query...")

                # Set the camera position and rotation again before executing the query
                sandbox_handler.sandbox.move_to(x, y, z)
                sandbox_handler.sandbox.rotate_to(pitch, yaw, roll)
            
                # Execute the query
                input_text = row['Query']
                logging.info(f"Executing query...\n")
                python_code, final_output, exec_time, times = processing(input_text=input_text, helper_llm=helper_llm, sandbox_handler=sandbox_handler)

                # Evaluation
                isCorrect = None
                label = None
                while isCorrect not in ['y', 'n']:
                    isCorrect = input("\nIs the outcome correct? ([Y]es/[N]o): ").strip().lower()
                if isCorrect == 'y':
                    label = 0
                else:
                    while label not in ['1', '2', '3', '4']:
                        print("==== Types of error:  ====")
                        print(" 1. It made no changes at all.")
                        print(" 2. It changed just the specified object(s) incorrectly or some of them.")
                        print(" 3. It changed the specified object(s) plus collateral ones.")
                        print(" 4. It changed other objects, but not the specified one(s).")
                        label = input("Choose one type of error: ").strip()        

                isFeedbackAligned = None
                labelFeedback = None
                while isFeedbackAligned not in ['y', 'n']:
                    isFeedbackAligned = input("\nIs the model's feedback aligned with what happend? ([Y]es/[N]o): ").strip().lower()
                
                if isFeedbackAligned == 'y':
                    labelFeedback = 'Aligned'
                else:
                    labelFeedback = 'Not aligned'
                
                row['Generated Code'] = python_code.replace('\n', '\\n').strip()
                row['Output query'] = final_output
                row['Total time'] = str(exec_time)
                row['Detailed time'] = str(times)
                row['Label'] = str(label)
                row['Label feedback'] = labelFeedback
                
                input("\n\nPress ENTER to continue to the next row, OR Ctrl+C to save and exit...")

        except KeyboardInterrupt:
            print("\nProcess interrupted. Saving progress...")

        with open(args.out_path, "w", newline='', encoding='utf-8') as salida:
            tsv_writer = csv.DictWriter(salida, fieldnames=fieldnames, delimiter=';')
            tsv_writer.writeheader()
            tsv_writer.writerows(datos_salida)

if __name__ == "__main__":
    main()
