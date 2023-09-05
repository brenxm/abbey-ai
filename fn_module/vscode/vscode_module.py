from dotenv import load_dotenv
from fn_module.vscode.pipe_connection import request
import json
import openai
import os
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_vscode(content_obj):

    data = json.loads(request("getData"))
    
    new_string = f"{content_obj['label']}:{data[content_obj['get_method']]}"
    keyword_used = content_obj["keyword_obj"]["keyword_used"]
    new_prompt = content_obj["prompt"].replace(keyword_used, new_string)
    
    print(data)
    result_obj = {
        "filePath": data["filePath"],
        "prompt": new_prompt
    }
    
    return result_obj

def write_vscode(obj):
    print(f"I reedited the code now using this code to this path: {obj['file_path']}")
    pass