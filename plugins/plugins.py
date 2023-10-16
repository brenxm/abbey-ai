import importlib
import sys
import os

class Plugins():
    def __init__(self):
        self.loaded_plugins = [] # Instances of modules

    def load_plugins(self, paths):
        for path in paths:

            for file in os.listdir(path):
                temp_path = os.path.join(path, file)

                if os.path.isdir(temp_path):
                    for filename in os.listdir(temp_path):  
                        if filename.endswith('_module.py'):
                            module_name = filename[:-3]
                            sys.path.append(temp_path)
                            module = importlib.import_module(module_name)

                            if hasattr(module, 'register'):
                                module_instance = module.register()
                                self.loaded_plugins.append(module_instance)


if __name__ == "__main__":
    instance = Plugins()
    instance.load_plugins(['./plugins/'])