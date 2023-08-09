from datetime import datetime
import os
import json

class AIMemory():
    def __init__(self, chat_limit = 5):
        self.chat_history = []
        self.path_file = os.path.join("data", "dynamic_memory", "ai_dynamic_memory.json")
        self.chat_limit = chat_limit
        self._load_memory()
        
    def add_chat_history(self, name, message):
        
        self.chat_limit = 5 # limit to keep includes user and assistant
        
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
        
        with open(self.path_file, "w") as f:
            json.dump(dm_obj, f, indent=4)
            
            
    def _load_memory(self):
        try:
            with open(self.path_file, "r") as f:
                data = json.load(f)
                
            self.chat_history = data["chat_history"]
        except:
            print("No existing memory. Starting from fresh")
            
    