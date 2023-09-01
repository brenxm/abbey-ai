from fn_module.vscode.vscode_module import get_vscode
from dotenv import load_dotenv
import json
import openai
import os

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


class PromptRequest():
    def __init__(self, model):
        self.model=model,
        self.messages = []
    
    def prompt(self, prompt):
        
        print(f"requests messages: {len(self.messages)} ")
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
        
        print(response)
        return response
    
    def add_message(self, prompt_msg_obj):
        print('displayed')
        self.messages.append(prompt_msg_obj)
        
    def clear_message(self):
        self.messages = []