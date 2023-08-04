class Interface():
    def __init__(self):
        self.queue = []
        
    def add_item(self, item):
        print(f"item added {item}")
        self.queue.append(item)
    
    @property  
    def extract(self):
        return self.queue.pop()
    
    @property
    def audio_count(self):
        return len(self.queue)
    
    def debugger(self):
        print(self.queue)