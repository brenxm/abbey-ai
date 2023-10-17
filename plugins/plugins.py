import importlib
import sys
import os

class Plugins():
    def __init__(self):
        self.loaded_plugins = [] # Instances of plugins

    def load_plugins(self, paths):
        for path in paths:
            path_contents = [file for file in os.listdir(path) if not file.endswith('__') and not file.startswith('__')] # Removing systems directory

            for file in path_contents:
                temp_path = os.path.join(path, file)
                if os.path.isdir(temp_path):
                    self.load_plugin_from_dir(temp_path)

        print("All plugins are checked.")

    def load_plugin_from_dir(self, path):
        sys.path.append(path)

        for filename in os.listdir(path):
            if filename.endswith('_plugin.py'):
                plugin_name = filename[:-3]
                module = importlib.import_module(plugin_name)

                if hasattr(module, 'register'):
                    plugin_instance = module.register()
                    
                    # Check if the instance has a required property 'parser_id'
                    if not hasattr(plugin_instance, 'parser_id'):
                        print(f"Error loading plugin '{os.path.basename(path)}': Has a plugin file but instance has no 'parser_id' attribute/property.")
                        return
                  
                    self.loaded_plugins.append(plugin_instance)
                    print(f"Succesfully loaded '{os.path.basename(path)}' plugin.'")
                    return
                
                else:
                    print(f"Error loading plugin: A plugin file named '{plugin_name}' exist but has no 'register' function implemented.")
                    return
        
        print(f"Error loading plugin: A folder named '{os.path.basename(path)}' in plugins directory exist but has no plugin script")

# Used for testing, disregard
if __name__ == "__main__":
    instance = Plugins()
    instance.load_plugins(['./plugins/'])