import pipe_connection

def export():
    return[
        {
            "name": "vscode_get_code",
            "fn": pipe_connection.request,
            "description": "Get data from VS code",
            "parameters": {
                "request_type": {
                    "type": "string",
                    "enum": ["getFolder", "getActiveCode", "getHighlightedCode", "getItemPath"]
                },
            },
            "required_parameters": ["request_type"]
        }
    ]