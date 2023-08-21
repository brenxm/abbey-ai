1. Directory name must be same as module name. e.g., if the directory name is vscode, the module name should be vscode_module.py. Must be in a subdirectory in fn_module
2. Export point must be in file named with extension *_module.py e.g. vscode.module.py . Only one should have per module
3. Export file must contain a function named 'export' as the retrieval function, it must return a list/array of objs that follows this schema
name - (text) name of function 
fn - (function) actual fn
description -(text) description of the function
parameters - (object) name of param as key, has value of obj with two required properties 'type' enum[string/int/float] and 'description' as string
required_parameters - [(string)] optional, but must match the parameters if given
