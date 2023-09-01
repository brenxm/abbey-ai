from fn_module.vscode.vscode_module import get_vscode
from types import FunctionType, MethodType
import re
import types


keyword_objects = [
    {
        "keywords": ['active code', 'current code', 'get active code'],
        "type": "keyword_replace",
        "args": {
            "function_method": "getActiveCode",
            "label": "code"
        },
        "function": get_vscode,
        "response_fn": []
    },
    {
        "keywords": ["highlighted code"],
        "type": "keyword_replace",
        "args": {
            "function_method": "getHighlightedCode",
            "label": "code"
        },
        "function": get_vscode,
        "response_fn": []
    },
    {
        "keywords": ["vscode folder path"],
        "type": "keyword_replace",
        "args": {
            "function_method": "getFolder",
            "label": "vscode folder path"
        },
        "function": get_vscode,
        "response_fn": []
    },
    ]


# Schema of keyword object
schema_example = {
    "keywords": [], # list of keywords (strings)
    "type": "keyword_replace", # Enum("keyword_replace", "function_call")
    "label": "code", # label used for keyword_replace,
    "function_method": "getActiveCode", # Argument to a replacer type keyword object, created function must conform to a single argument input function or none
    "function": None # Actual function of needed to be called
}


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
            "functions": []
        }
                        
            # Execute prior request functions and append post request functions
        for index, obj in enumerate(keyword_objects):
            if obj["type"] == "keyword_replace":
                replaced_input = prompt_input.replace(parsed_keywords[index], obj["function"](obj["args"]))
                response["prompt_input"] = replaced_input
        
            elif obj["type"] == "function_call":
                obj["function"](obj["args"])
                
            try:
                response["functions"] += obj["response_fn"]
                print("Appended blackboard function to response object")
            except:
                pass
                
        print(f"this is the response: {response}")

        # Clean the keyword_objects
        return response
        
        
        
    def add_object(self, obj):
        if not isinstance(obj, (dict, list)):
            raise ValueError(f"Must be a 'keyword object' or a list a list of 'keyword object'")
        
        # Accept an object, validate if it conform to valid schema
        def validate_obj(obj):
            valid_properties = {
                "keywords": [list, re.Pattern],
                "type": ["keyword_replace", "function_call"],
                "args": [dict, None, str],
                "function": [FunctionType, MethodType],
                "response_fn": list
            }
             
            for property, valid_type in valid_properties.items():
                if property not in obj:
                    raise ValueError(f"'{property}' not found in the object.")
                        
                if isinstance(valid_type, list):  # Check against a list of allowed values/types
                    types_list = [t for t in valid_type if isinstance(t, type)]
                    values_list = [v for v in valid_type if not isinstance(v, type)]
                    
                    # Check if it matches any of the types
                    if any(isinstance(obj[property], t) for t in types_list):
                        continue
                        
                    # Check if it matches any of the allowed values
                    if obj[property] in values_list:
                        continue
                        
                    raise ValueError(f"'{property}' does not match the expected type or value.")
                else:  # Directly check against a type
                    if not isinstance(obj[property], valid_type):
                        raise ValueError(f"'{property}' does not match the expected type.")
        
        if isinstance(obj, (dict)):
            validate_obj(obj)
            self.keyword_objects.append(obj)
            
        elif isinstance(obj, (list)):
            for item in obj:
                validate_obj(item)
                self.keyword_objects.append(item)

"""                
parser = KeywordParser()
parser.add_object(keyword_objects)
parser.parse("With this vscode folder path, add a new item called python.exe")
"""