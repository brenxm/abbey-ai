from importlib import import_module
import sys
import os

def test_function(text):
    print('test function')


class FunctionsInterface():
    def __init__(self):
        self._functions = []
                    
    def load(self, module_name):
        # module_name refers to the name of the directory in fn_module
        
        # If not existing, raise an error
        path = os.path.join("fn_module", module_name)
        
        items = os.listdir(path)
        
        file_names = [item for item in items if item.endswith("_module.py")]
        
        sys.path.append(path)
        
        # Validate of duplicated or no module.py is found
        if len(file_names) > 1 or len(file_names) <= 0:
            raise FileNotFoundError("no _module.py in vscode module")
        
        module_path = f"fn_module.{module_name}.{file_names[0][:-3]}"
        module = import_module(module_path)
        functions = module.export()
        
        self._functions += functions
        
        sys.path.remove(path)
        
    @property
    def functions(self):
        
        functions = []
        reference_fn = {}
        
        for fn in self._functions:
            # Available functions
            reference_fn[fn["name"]] = fn["fn"]
            
            # Functions
            functions.append(
                {
                    "name": fn["name"],
                    "description": fn["description"],
                    "parameters": {
                        "type": "object",
                        "properties": fn["parameters"]
                    },
                    "required": fn["required_parameters"]
                }
            )
            
        return {
            "functions": functions,
            "reference_fn": reference_fn
        }
        
        