import pipe_connection

def vscode_printer(text):
    print(text)


def export():
    return[
        {
            "name": "vscode get code",
            "fn": pipe_connection.request,
            "description": "Get data from VS code",
            "parameters": {
                "requestType": {
                    "type": "string",
                    "enum": ["getFolder, getActiveCode, getHighlightedCode, getItemPath"]
                }
            },
            "required_parameters": ["requestType"]
        }
    ]