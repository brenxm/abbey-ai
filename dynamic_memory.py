from datetime import datetime
import os
import json

class AIMemory():
    def __init__(self, chat_limit = 10):
        self.chat_history = []
        self.file_path = os.path.join(os.environ["LOCALAPPDATA"], "Summer AI", "data", "chat_history.json")
        self.chat_limit = chat_limit
        self._load_memory()
        
    def add_chat_history(self, name, message):
        
        now = datetime.now()
        date = now.strftime("%m/%d/%Y-%H:%M:%S")

        chat = f"({date}) {name}: {message}"
        
        self.chat_history.append(chat)
        
        if len(self.chat_history) > self.chat_limit:
            self.chat_history.pop(0)

        self._update_memory()
        
        
    def clear(self):
        self.chat_history = []
        print('succesfully deleted chat history.')
        self._update_memory()
        
        return "Chat or conversation cleared succesfull!"
    
    # update the memory file in data with every changes made
    def _update_memory(self):
        
        dm_obj = {
            "chat_history": self.chat_history
        }
        
        with open(self.file_path, "w") as f:
            json.dump(dm_obj, f, indent=4)
            
            
    def _load_memory(self):
        try:
            with open(self.file_path, "r") as f:
                data = json.load(f)
                
            self.chat_history = data["chat_history"]
        except:
            print("No existing memory. Starting from fresh")