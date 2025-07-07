import argparse
import asyncio
import json
import logging
import time
import yaml

from src.helper_llm import HelperLLM, HelperLLMViaAPI
from src.prompting.sandbox_prompts import API_DOCS, CHAT_API_EXAMPLES
from src.sandbox_handler import SandboxHandler
from src.voice_layer import record_audio, asr_from_file


def parse_args():

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default="config.yaml", help="Path to the configuration file")
    
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
        openai_api_key=openai_api_key
    )

    logging.info("Helper LLM client created")

    return helper_llm, sandbox_handler



def processing(input_text: str, helper_llm: HelperLLM, sandbox_handler: SandboxHandler) -> str:

    start_time = time.time()

    # sandbox_handler.sandbox.text_to_speech(input_text)

    logging.info(f"INPUT QUERY: {input_text}")
    input_data = {
        "query": input_text,
        "api_documentation": API_DOCS,
        "api_examples": CHAT_API_EXAMPLES
    }

    python_code = helper_llm(input_data=input_data, instruction_type="sandbox_api")
    python_code_time = time.time()

    python_outcome = sandbox_handler(code=python_code)
    python_exec_time = time.time()

    logging.info(f"PYTHON CODE:\n{python_code.strip()}")

    input_data = {
        "query": input_text,
        # "python_code": python_code,
        "outcome": python_outcome,
    }

    final_output = helper_llm(input_data=input_data, instruction_type="sandbox_verbalization")    
    logging.info(f"OUTPUT QUERY: {final_output}")

    sandbox_handler.sandbox.text_to_speech(final_output)
    end_time = time.time()

    logging.debug(f"TIMES: P. code {python_code_time-start_time:.2f}s - P. exec {python_exec_time-python_code_time:.2f}s - Verb. {end_time-python_exec_time:.2f}s")
    
    return final_output


def main():

    args = parse_args()
    logging.basicConfig(level=logging.INFO)
    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    helper_llm, sandbox_handler = load_llms_and_handlers(config)
    
    while True:
        input_text = input("Type input query: ").strip()
        start_time = time.time()
        if input_text.lower() == "q":
            break
        elif input_text == "": # Record audio if empty string
            logging.info("Starting to record for 5 seconds...")
            audio_file = record_audio(seconds=5)
            logging.info("Recording stopped.")
            start_time = time.time() # Don't include recording
            with open(audio_file, "rb") as f:
                response = asyncio.get_event_loop().run_until_complete(
                    asr_from_file(f)
                )
            json_data = json.loads(response.body)
            if json_data['status'] == 'success':
                input_text = json_data['transcript']
                logging.info(f"Input text: {input_text}")
            else:
                logging.error("STT failed, please retry your query.")
                continue
        
        _ = processing(input_text=input_text, helper_llm=helper_llm, sandbox_handler=sandbox_handler)
        end_time = time.time()
        logging.info(f"Execution time: {end_time-start_time:.2f}s")



if __name__ == "__main__":
    main()