from fn_module.vscode.vscode_module import get_vscode, write_vscode
from types import FunctionType, MethodType
import re
import types


keyword_objects = [
     {
        "keywords": ['active code', 'current code', 'get active code'],
        "type": "keyword_replace",
        "prior_fn_args": {
            "get": "activeCode",
            "label": "code"
        },
        "prior_function": get_vscode,
    },
    {
        "keywords": ["highlighted code"],
        "type": "keyword_replace",
        "prior_fn_args": {
            "get_method": "highlightedCode",
            "label": "highlighted code"
        },
        "prior_function": get_vscode,
        "post_fn_args": {},
        "post_function": write_vscode
    },
    {
        "keywords": ["vscode folder path"],
        "type": "keyword_replace",
        "prior_fn_args": {
            "get_method": "folderPath",
            "label": "vscode folder path"
        },
        "prior_function": get_vscode,
    }
    ]

class KeywordParser():
    def __init__(self):
        self.keyword_objects = keyword_objects
        
    def parse(self, prompt_input):
        # Getting and setting up all available keywords
        keywords = []
        for obj in self.keyword_objects:
            if isinstance(obj["keywords"], re.Pattern):
                match_keyword = re.search(obj["keywords"], prompt_input)
                if match_keyword:
                    keywords.append(match_keyword.group(0))
            
            elif isinstance(obj["keywords"], list):
                keywords += obj["keywords"]
            

        print(f"these are the count of objects: {len(self.keyword_objects)} and these are the generated keywords {keywords}")
        
        # Match keywords with prompt input
        parsed_keywords = []
        for keyword in keywords:
            if keyword in prompt_input:
                parsed_keywords.append(keyword)
        
        # Get 'keyword object' for a match keyword
        keyword_objects = []        
        for index, obj in enumerate(self.keyword_objects):
            for keyword in parsed_keywords:
                if isinstance(obj["keywords"], list):
                    if keyword in obj["keywords"]:
                        keyword_objects.append(self.keyword_objects[index])
                
                elif isinstance(obj["keywords"], re.Pattern):
                    match_keyword = re.search(obj["keywords"], keyword)
                    if match_keyword:
                        keyword_objects.append(self.keyword_objects[index])
                    
                    
        
        response = {
            "prompt_input": prompt_input,
            "args": {},
            "functions": []
        }
                        
            # Execute prior request functions and append post request functions
        for index, obj in enumerate(keyword_objects):
            if obj["type"] == "keyword_replace":
                response_obj = obj["prior_function"](obj["prior_fn_args"])
                print(f"{prompt_input}")
                replace_input = prompt_input.replace(parsed_keywords[index], response_obj["prompt"])
                response["prompt_input"] = replace_input
                
                if response_obj["filePath"]:
                    response["args"]["file_path"] = response_obj["filePath"]
                
        
            elif obj["type"] == "function_call":
                obj["prior_function"](obj["prior_fn_args"])
                
            try:
                response["functions"].append(obj["post_function"])
                    
            except:
                pass
                
        print(response["args"])
        
        # Clean the keyword_objects
        return response
        
        
        
    def add_object(self, obj):
        if not isinstance(obj, (dict, list)):
            raise ValueError(f"Must be a 'keyword object' or a list a list of 'keyword object'")
        
        # Accept an object, validate if it conform to valid schema
        def validate_obj(obj):
            valid_properties = {
                "keywords": {
                    "data_types": [list, re.Pattern],
                    "required": True
                             },
                "type": {
                    "data_types": ["keyword_replace", "function_call"],
                    "required": True
                        },
                "prior_fn_args": {
                    "data_types": [dict, None, str],
                    "required": False
                        },
                "prior_function": {
                    "data_types": [FunctionType, MethodType],
                    "required": False,
                        },
                "post_fn_args": {
                   "data_types": [dict, None, str],
                   "required": False
                        },
                "post_function": {
                    "data_types": [FunctionType, MethodType],
                    "required": False
                        }
            }
            for property, valid_type in valid_properties.items():
                if valid_properties[property]["required"]:
                    if property not in obj:
                        raise ValueError(f"'{property}' not found in the object.")
                
                
                print(valid_type)
                valid_data_types = valid_type["data_types"]
                if isinstance(valid_data_types, list):  # Check against a list of allowed values/types
                    types_list = [t for t in valid_type["data_types"] if isinstance(t, type)]
                    values_list = [v for v in valid_type["data_types"] if not isinstance(v, type)]
                    
                    # Check if it matches any of the types
                    
                    # If property not existing and is not required -> continue
                    try:
                        if any(isinstance(obj[property], t) for t in types_list):
                            continue
                            
                        # Check if it matches any of the allowed values
                        if obj[property] in values_list:
                            continue
                        
                    except:
                        if not valid_properties[property]["required"]:
                            continue
                        
                    raise ValueError(f"'{property}' does not match the expected type or value.")
                else:  # Directly check against a type
                    if not isinstance(obj[property], valid_type["data_types"]):
                        raise ValueError(f"'{property}' does not match the expected type.")
        
        if isinstance(obj, (dict)):
            validate_obj(obj)
            self.keyword_objects.append(obj)
            
        elif isinstance(obj, (list)):
            for item in obj:
                validate_obj(item)
                self.keyword_objects.append(item) 