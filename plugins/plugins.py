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
        sys.path.append(path)

        for filename in os.listdir(path):
            if filename.endswith('_plugin.py'):
                plugin_name = filename[:-3]
                module = importlib.import_module(plugin_name)

                if hasattr(module, 'register'):
                    plugin_instance = module.register()
                    self.loaded_plugins.append(plugin_instance)
                    return
                
                else:
                    print(f"A plugin file named '{plugin_name}' exist but has no 'register' function implemented.")
                    return
        
        print(f"A folder named '{os.path.basename(path)}' in plugins directory exist but has no plugin script")

# Used for testing, disregard
if __name__ == "__main__":
    instance = Plugins()
    instance.load_plugins(['./plugins/'])