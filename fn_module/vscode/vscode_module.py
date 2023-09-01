from dotenv import load_dotenv
from fn_module.vscode.pipe_connection import request
import json
import openai
import os
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_vscode(content_obj):
    code = json.loads(request(content_obj["function_method"]))
    return f"{content_obj['label']}:\n{code}\n"