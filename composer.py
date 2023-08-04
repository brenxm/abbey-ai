import openai
import os
import json
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_action_node(prompt, token_used = 0):
#prompt = "Make me a python script that has example of recursion in it, save it to home directory and display it on blackboard"

    system_prompt = {
        """
        Analyze the user prompt and generate an Action Prompt Node.
        An Action Prompt Node is an object that has properties of
        'description': shorten the prompt to a readable label e.g. Delete file <name> in <directory>
        'sequence': a list of function node in order to satisfy the prompt. Format: [<fn node1> -> <fn node2>] e.g. [get_path(prompt) -> read_file(get_path) -> bboard_display(read_file)]
        
        Sequence must include only the steps necessary to comeplete the give task.
        Avoid unnecessary actions (e.g. saving a file when not explicitly stated)
        Be explicit and include only the necessary function nodes
        Use only the given nodes below. Don't come up with own
        Don't close the blackboard unless explicitly asked
        Always open the blackboard when accessing it
        
        Function node and it's description
        get_path(): Retrieve the file path mentioned in the prompt. prompt as parameter required
        read_file(): Read or analyze the content for errors of a file or code at a give file path.
        delete_file(): Delete a file at the specified path.
        generate_text(): Write code, terminal inputs, files in any file format. Prompt as parameter required
        save_file(): Save a file to the specified directory. 2 Params required: Content (string) and path(directory)
        terminal_invoke(): Execute the given string in the terminal.
        bboard_init(): Open the blackboard window.
        bboard_close(): Close the blackboard window only when asked.
        bboard_display(): Display the given content on the blackboard. Param content (string) 
        bboard_get(): Retrieve the content from the blackboard.
        bboard_clear(): Clear the displayed content on the blackboard. Only when asked in prompt
        vscode_get(): Get the content in VS code. Max of one required param:['highlighted': portion of a script or code, 'script': entire script is requested, 'directory': current directory of VS code user's working on]
        
        Examples of Sequence Node:
        1. Prompt: "Make me a python code that has an example on how to use a loop and save it to my home directory."
        Response: 
        {
            "description": "Example of py code saved in home",
            "sequence": ['generate_text()', 'get_path(prompt)', 'save_file(generate_text, get_path)']
        }
        (Explanation: Generate the script, retrieve the home directory path, then save the file)
        
        2.Prompt: "Delete the file in the downloads directory"
        Response: 
        {
            "description": "Delete file in downloads",
            "sequence": ['get_path(prompt)', 'delete_file(get_path)']
        }
        (Explanation: Get the path to the downloads directory and then delete the specified file.)
        
        3. Prompt: "Run the git push for me on my current directory"
        Response:
        {
            "description: "Git push on <directory>"
            "sequence": ['vscode_get('directory'), generate_text(vscode_get), terminal_invoke(generate_text)]
        }
        
        4. Prompt: "Write a recursion code and save it to my home directory, then display it on blackboard"
        Response:
        {
            "description": "Recursion code saved in home directory and displayed on blackboard",
            "sequence": ['generate_text(prompt)', 'get_path(prompt)', 'save_file(generate_text, get_path)', 'bboard_init()', bboard_display(generate_text)]
        }
        (Explanation: You wrote a code using generate_text based on prompt, then you took the path using get_prompt based on prompt, you saved the file using save_file with those two first functions executed, you opened the blackboard, and displayed the content of generate_text on blackboard)
        
        5. Prompt: "Analyze the highlighted code for errors and add appropriate comments and display it on blackboard"
        Response: 
        {
            "description": "Analyze and comment highlighted code, display on blackboard",
            "sequence": ['vscode_get('highlighted')', 'read_file(vscode_get)', 'generate_text(read_file)', 'bboard_init()', 'bboard_display(generate_text)']
        }
        (Explanation: The sequence starts by getting the highlighted code from VS Code using vscode_get('highlighted'). It then reads and analyzes the content for errors using read_file(vscode_get). Next, it generates the text with the appropriate comments using generate_text(read_file). Finally, it initializes the blackboard with bboard_init() and displays the commented code on the blackboard using bboard_display(generate_text))
        
        prompt: """
        + prompt
        
        }


    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=[
            {
                "role": "system", "content": f"{system_prompt}"
            },
        ]
    )

    action_node = json.loads(response["choices"][0]["message"]["content"])
    action_node["prompt"] = prompt
    action_node["total_token_used"] = token_used + response["usage"]["total_tokens"]
    json_string = json.dumps(action_node, indent=4)
    return json_string
