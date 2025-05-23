from openai import OpenAI
import os
import logging
import time


class LLMCall:
    def __init__(self,API_key,model_name) -> None:
        super().__init__()
        self.API_key = API_key
        self.model_name = model_name
        if self.model_name == 'qwen':
            API_base = ''
        elif self.model_name.startswith("qwen"):
            API_base = ''
        elif self.model_name.startswith("llama3"):
            API_base = ''
        elif self.model_name.startswith("mistral"):
            API_base = ''
        elif self.model_name=='gpt':
            API_base=""
        self.API_key=""
        self.client = OpenAI(api_key=self.API_key, base_url=API_base)

    def call(self, messages,seed=0):
        response = None
        while response is None:
            try:
                if self.model_name.startswith("llama3"):
                    response = self.client.chat.completions.create(
                        model="",
                        messages = messages,
                        seed=seed   
                    )
                elif self.model_name.startswith("mistral"):
                    response = self.client.chat.completions.create(
                        model="",
                        messages = messages,
                        seed=seed
                    )
                elif self.model_name=="qwen":
                    response = self.client.chat.completions.create(
                        model="",
                        messages = messages,
                        seed=seed,
                    )
                elif self.model_name=='gpt':
                    response = self.client.chat.completions.create(
                        model='',
                        messages=messages,
                    )
                else:
                    pass
            except Exception as e:
                logging.warning(e)
                return 'Unable to reach the response due to some reasons.'
        return response.choices[0].message.content

