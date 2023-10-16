from types import FunctionType, MethodType
import os
import sys
import importlib
import json
import re
import types

class KeywordParser():
    def __init__(self):
        self.keyword_objects = []
        self.prompt_input = ""
        self.modules = []
        
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
            
        print(f"THIS ARE THE KEYWORDS {' '.join(keywords)}")
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
                        parsed_obj = self.keyword_objects[index]
                        parsed_obj["keyword_used"] = keyword
                        keyword_objects.append(parsed_obj)
                    
                elif isinstance(obj["keywords"], re.Pattern):
                    match_keyword = re.search(obj["keywords"], keyword)
                    if match_keyword:
                        parsed_obj = self.keyword_objects[index]
                        parsed_obj["keyword_used"] = keyword
                        keyword_objects.append(parsed_obj)
                    
        print(f"THIS ARE THE KEYWORD OBJECTS:{len(keyword_objects)}")
        response = {
            "prompt_input": prompt_input,
            "function_objs": keyword_objects
        }
                        
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
        
        if isinstance(obj, dict):
            print(f"ADDED OBJ: {obj}")
            self.keyword_objects.append(obj)
            
        elif isinstance(obj, (list)):
            for item in obj:
                self.keyword_objects.append(item)
    

    def load_modules(self):
        module_dir = "./modules"
        os.chdir(module_dir)
        sys.path.append(os.getcwd())

        for filename in os.listdir():
            if filename.endswith('.py') and filename != '__init__.py':
                module_name = filename[:-3]
                module = importlib.import_module(module_name)

                # Get the modules attributes, omitting systems attributes
                attributes = [attribute for attribute in dir(module) if not attribute.endswith('__') and not attribute.startswith('__')]

                if len(attributes) > 1 or len(attributes) == 0:
                    pass
                    #TODO: go to next folder

                module_class = module[attributes[0]]
                


                

if __name__ == "__main__":
    parser = KeywordParser()
    parser.load_modules()