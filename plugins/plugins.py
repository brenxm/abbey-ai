import importlib
import sys
import os

class Plugins():
    def __init__(self):
        self.loaded_plugins = [] # Instances of modules

    def load_plugins(self, paths):
        for path in paths:
            path_contents = [file for file in os.listdir(path) if not file.endswith('__') and not file.startswith('__')] # Removing systems directory
            
            for file in path_contents:
                temp_path = os.path.join(path, file)
                
                if os.path.isdir(temp_path):
                    self.load_plugin_from_dir(temp_path)

        print("All plugins are checked.")


    def load_plugin_from_dir(self, path):
        for filename in os.path.listdir(path):
            if filename.endswitch('_module.py'):
                module_name = filename[:-3]
                sys.path.append(path)
                module = importlib.import_module(module_name)

                if hasattr(module, 'register'):
                    module_instance = module.register()
                    self.loaded_plugins.append(module_instance)
                    return
                
                else:
                    print('A module exist but has no "register" attribute/method implemented.')
                    return
        
        print(f"A directory exist but has no module script")

                                


if __name__ == "__main__":
    instance = Plugins()
    instance.load_plugins(['./plugins/'])