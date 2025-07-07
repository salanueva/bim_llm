from abc import ABC, abstractmethod
from openai import OpenAI

from src.prompting.sandbox_prompts import SANDBOX_PROMPT, SANDBOX_VERBALIZATION_PROMPT


class HelperLLM(ABC):

    def __init__(self, model_name: str, instruction_templates: dict[str] = None, enable_thinking: bool = False):
        
        self.model_name = model_name
        
        self.model_generate_parameters = {
            "best_of": 1, 
            "top_p": 1, 
            "top_k": 1, 
            "use_beam_search": True,
            "temperature": 0.0, 
            "max_new_tokens": 4096
            # "do_sample": True,
            # "pad_token_id": self.tokenizer.eos_token_id,
        }

        if "Qwen3" in model_name:
            self.model_generate_parameters["enable_thinking"] = enable_thinking

        self.is_google = False
 
        if instruction_templates is not None:
            self.instructions = instruction_templates
        else:
            self.instructions = {
                "sandbox_verbalization": SANDBOX_VERBALIZATION_PROMPT,
                "sandbox_api": SANDBOX_PROMPT
            }
 

    @abstractmethod
    def __call__(self, input_data: dict[str, str], instruction_type: str) -> str:
        return


    def _preprocess_input_chat(self, input_data: dict[str, str], instruction_type: str) -> list[dict]:
        if instruction_type == "sandbox_api":
            content = self.instructions[instruction_type].format(
                api_documentation=input_data['api_documentation'],
            )
            chat = [
                {
                    "role": "user",
                    "content": content,
                },
                {
                    "role": "assistant",
                    "content": "Alright, from now on I will answer just by writing Python code."
                }
            ] + input_data['api_examples'] + [
                {
                    "role": "user",
                    "content": input_data["query"]
                }
            ]
        elif instruction_type == "sandbox_verbalization":
            content = self.instructions[instruction_type].format(
                query=input_data['query'], outcome=input_data['outcome'] # python_code=input_data['python_code'],
            )
            chat = [
                {
                    "role": "user", 
                    "content": content 
                }  
            ]
        elif instruction_type == "cypher_verbalization":
            content = self.instructions[instruction_type].format(
                query=input_data['query'], metadata=input_data['metadata']
            )
            chat = [
                {
                    "role": "user", 
                    "content": content 
                }  
            ]
        return chat


    """
    # This is the version for Qwen3 models, which have a different format for the chat messages.
    def _postprocess_output_python(self, output_python: str) -> str:
        # Remove any explanation. E.g.  a = 2...\n\n**Explanation:**\n\n -> a = 2...
        # Remove python indicator. E.g.```python\na = 2...``` --> a = 2...
        # Note: Possible to have both:
        #   E.g. ```cypher\a = 2...```\n\n**Explanation:**\n\n --> a = 2...
        output_python = re.sub(r"<think>.*?</think>", "", output_python, flags=re.DOTALL)
        output_python = output_python.strip()
        if output_python.startswith("```python"):
            output_python = output_python[len("```python"):].strip()
        if output_python.startswith("```"):
            output_python = output_python[len("```"):].strip()
        output_python = output_python.split("```")[0].strip()
        output_python = output_python.split("**Explanation:**")[0].strip()
        return output_python
    """

    def _postprocess_output_python(self, output_python: str) -> str:
        # Remove any explanation. E.g.  a = 2...\n\n**Explanation:**\n\n -> a = 2...
        # Remove python indicator. E.g.```python\na = 2...``` --> a = 2...
        # Note: Possible to have both:
        #   E.g. ```cypher\a = 2...```\n\n**Explanation:**\n\n --> a = 2...
        partition_by = "**Explanation:**"
        output_python, _, _ = output_python.partition(partition_by)
        output_python = output_python.strip("`\n")
        output_python = output_python.lstrip("python\n")
        output_python = output_python.strip("`\n ")
        output_python = output_python.replace("\t", "    ")
        return output_python


class HelperLLMViaAPI(HelperLLM):
    """
    This variant calls an endpoint containing the model. The endpoint is defined by calling `vllm serve [model_name]`.
    """

    def __init__(self, model_name: str, instruction_templates: dict[str, str] = None, openai_api_base_url: str = "http://localhost:8000/v1", openai_api_key: str = "EMPTY", enable_thinking: bool = False):

        super().__init__(model_name, instruction_templates)

        self.openai_api_key = openai_api_key
        self.open_api_base = openai_api_base_url
        self.model_generate_parameters["do_sample"] = True

        self.client = OpenAI(api_key=openai_api_key, base_url=openai_api_base_url)

    def __call__(self, input_data: dict[str, str], instruction_type: str) -> str:

        chat_response = self.client.chat.completions.create(
            model=self.model_name,
            messages=self._preprocess_input_chat(input_data, instruction_type),
            temperature=self.model_generate_parameters['temperature'],
            top_p=self.model_generate_parameters['top_p'],
        )

        if instruction_type == "sandbox_api":
            return self._postprocess_output_python(chat_response.choices[0].message.content)
        else:
            return chat_response.choices[0].message.content
