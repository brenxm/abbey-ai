from dotenv import load_dotenv
import json
import openai
import os

ENV_PATH = os.path.join(os.environ['LOCALAPPDATA'], 'Summer AI', '.env')

load_dotenv(dotenv_path=ENV_PATH)

openai.api_key = os.getenv("OPENAI_API_KEY")


class PromptRequest():
    def __init__(self, model):
        self.model=model,
        self.messages = []

    
    def prompt(self, prompt):

        if prompt:
            self.messages.append(
                {
                    "role": "user", 
                    "content": prompt
                }
            )
        
        response = openai.ChatCompletion.create(
            model='gpt-4',
            messages = self.messages,
            stream = True
        )

        print(self.messages)
        
        return response
    
    def add_message(self, prompt_msg_obj):
        system_prompt = {
            "role": prompt_msg_obj["role"],
            "content": prompt_msg_obj["content"]
        }
        
        self.messages.append(system_prompt)
        
        
        
    def clear_message(self):
        self.messages = []