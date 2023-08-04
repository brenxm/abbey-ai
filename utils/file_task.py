import os

def read_file(path_file):
    print(path_file)
    # if has no extension
    file_name = os.path.basename(path_file)
    if "." not in file_name:
        file_with_extension = get_file_extension(path_file)
        
        if not file_with_extension or type(file_with_extension).__name__ == "list":
            return file_with_extension
        
        path_file = path_file.replace(file_name, file_with_extension)
   
    with open(path_file, "r") as f:
        content = f.read()
        return content

    
def get_file_names(directory):
    """Returns a list of files in the given directory"""
    try: 
        list = os.listdr(directory)
        return ", ".join(list)
    
    except FileNotFoundError as e:
        print(e)
        return "Invalid directory"
        
        
def get_file_extension(file_path):
    """Returns the file name with it's extension of the given file path.
    If one match is found, it will return the name plus extension. (String)
    If two names was found, it will return a list
    If none, it will return None
    """
    file_name = os.path.basename(file_path)
    directory = file_path[:-len(file_name)]
    
    existing_files = os.listdir(directory)
    names = []
    for name in existing_files:
        if file_name in name:
            names.append(name)
    
    name_counts = len(names)
    if name_counts == 1:
        return names[0]
    
    elif name_counts > 1:
        return names
    
    else:
        return None
    

    