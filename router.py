import openai
import os
from composer import generate_action_node
from dotenv import load_dotenv

load_dotenv()
openai.api_key=os.getenv("OPENAI_API_KEY")

# Determine prompt if type of general query or file accessing

prompt = "in developer path main.py, read the content and tell me what's wrong with them. Display your explanation on blackboard"

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-0613",
    messages=[
        {
            "role": "system",
            "content": f"""
            You evaluate the given prompt to categorize it into one of two distinct types:
            General query: This category encompasses prompts that don't require access to files. It includes:
                General Questions: Questions or inquiries on various subjects.
                Tutorials and Teachings: Guidance on topics like coding, mathematics, etc.
                Continuation of Conversation: If the prompt pertains to a follow-up or continuation of a previously established dialogue or discussion.
                
            File access: If the prompt necessitates interacting with files within the system, it falls into this category. Examples include tasks related to creating, modifying, reading, or deleting files; managing personal data like notes, phonebooks, or reminders; interacting with the blackboard; and accessing specific code elements within VS code. Terminal interaction such as installing, updating, using git in terminal
            
            Response must be 'General query' and 'File access' only.
            
            prompt: {prompt}
            """
        }
    ]
)

prompt_type = response["choices"][0]["message"]["content"]
total_token = response["usage"]["total_tokens"]


if prompt_type == "General query":
    print("hehe answer here")
    print(total_token)
    # call General query
    
elif prompt_type == "File access":
    print(generate_action_node(prompt, token_used=total_token))
    # file access
    
else:
    print(f"error, printed {prompt_type}. 'General query' and 'File access' are values allowed")