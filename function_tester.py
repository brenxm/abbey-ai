from notes import Notes
import os
from dotenv import load_dotenv
import openai
import re
import json

load_dotenv()
notes = Notes()
notes.load()

openai.api_key = os.getenv("OPENAI_API_KEY")

pattern = r"((notes|note|plans|plan).+?(update|modify|add|create|make|write|read|open|delete|remove)|(update|modify|add|create|make|write|read|open|delete|remove).+?(notes|note|plans|plan))"

prompt = "write me a new note about building a pc, make a list of parts needed as the content"

match = re.search(pattern, prompt, re.IGNORECASE)

if match:
    print(match.group())

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}],
    functions=[
        {
            "name": "new_note",
            "description": "Create a new item in the notes\\plans",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Title of the note"},
                    "content": {
                        "type": "string",
                        "description": "content\\description\\body of the notes",
                    },
                },
                "required": ["title", "content"]
            },
        }
    ],
    function_call={"name": "new_note"},
)

fn_map = {"new_note": notes.new_note}

if response["choices"][0]["message"]["function_call"]:
    fn_name = response["choices"][0]["message"]["function_call"]["name"]
    fn = fn_map.get(fn_name)
    args = json.loads(response["choices"][0]["message"]["function_call"]["arguments"])
    print(args)
    fn(**args)  # Pass the updated args as parameters to the function
