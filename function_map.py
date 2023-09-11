from fn_module.vscode.vscode_module import get_vscode, write_vscode


class FunctionMap():
    def __init__(self):
        self.functions = [
            {
                "name": 'get_vscode',
                'function': get_vscode
            },
            {
                "name": "write_vscode",
                "function": write_vscode
            }
        ]
        
    # get function
    def get_function(self, name):
        
        for fn in self.functions:
            if name == fn["name"]:
                return fn["function"]
            
        raise ValueError(f"{name} is NOT a function in <class FunctionMap> functions.")
    
    
    def add_function(self, obj):
            
        def validate_obj(obj):
            if 'name' not in obj:
                raise ValueError("Missing 'name' property.")
            
            if 'function' not in obj:
                raise ValueError('Missing "function" property.')
            
            
        if isinstance(obj, dict):
            validate_obj(obj)
            self.functions.append(obj)
            
        elif isinstance(obj, list):
            for new_fn in obj:
                validate_obj(new_fn)
                self.functions.append(new_fn)
                
        else:
            raise ValueError("new FunctionMap function must be type of 'list' or 'dict'.")