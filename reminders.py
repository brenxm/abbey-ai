from dotenv import load_dotenv
import os
import json
import threading
import datetime
import time
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class Reminders():
    '''
    Schema and instructions for each reminder provided in the comments above.
    '''
    def __init__(self, openai = False):
        self.reminders = []
        self.load()
        self.init_check_thread()
        self.openai = openai

    def load(self):
        path = 'data/reminders.json'
        if not os.path.isfile(path):
            with open(path, 'w') as f:
                json.dump(self.reminders, f)
        else:
            with open(path, 'r') as f:
                self.reminders = json.load(f)

    def get_reminders(self):
        return str(self.reminders)

    def delete(self, title):
        self.reminders = [reminder for reminder in self.reminders if reminder['title'].lower() != title.lower()]
        self.save_reminders()

    def new_reminder(self, title, description, due_date, due_time):
        reminder = {
            "description": description,
            "title": title,
            "due_date": due_date,
            "due_time": due_time
        }
        self.reminders.append(reminder)
        self.save_reminders()

    def save_reminders(self):
        path = 'data/reminders.json'
        with open(path, 'w') as f:
            json.dump(self.reminders, f)

    def init_check_thread(self):
        thread = threading.Thread(target=self.check_reminders, daemon=True)
        thread.start()

    def check_reminders(self):
        while True:
            now = datetime.datetime.now()
            for reminder in self.reminders:
                due_date = datetime.datetime.strptime(reminder['due_date'], '%m-%d-%Y')
                if now >= due_date:
                    print(f'Due Reminder Detected with title: {reminder["description"]}')
            print('checking')
            time.sleep(5)

            # Sends to next prompt of AI
    def reminder_titles(self):
        titles = [reminder["title"] for reminder in self.reminders]
        print(", ".join(titles))
        return ", ".join(titles)

    def parser_obj(self):
        parser_obj = {
            "keywords": ["my reminders, my reminders"],
            "prior_functions": [
                {
                    "function": self.prior_fn,
                    "arg": {}
                }
            ]
        }

    def prior_fn(self, arg):

        keywords = {
            "create": ["create", "make"],
            "read": ["check", "read"],
            "update": ["update", "rewrite", "update"],
            "delete": ["remove", "delete"]
        }

        function_map = {
            "create": self.new_reminder,
            "read": self.get_reminders,
            "delete": self.delete
        }

        action = ""
        break_all = False
        prompt_list = arg["prompt"].split(" ")
        for prop in keywords:
            for word in prompt_list:
                if word in keywords[prop]:
                    action = prop
                    break_all = True
                    break
            if break_all:
                break

        if action == "create":
            response = self.openai_function_call(
                [
                    {
                        "role": "system", "content": f"Current date and time: {str(datetime.datetime.now())}"
                    },
                    {
                        "role": "user", "content": arg["prompt"]
                    }
                ], 
                {
                    "name": action,
                    "description": "Create a reminder",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "title of the reminder",
                            },
                            "description": {
                                "type": "string",
                                "description": "description of the reminder"
                            },
                            "due_date": {
                                "type": "string",
                                "description": "Due date of the reminder with format of %m-%d-%Y"
                            },
                            "due_time": {
                                "type": "string",
                                "description": "due time of the reminder with military time format e.g. 2300, 0700"
                            }
                        }
                    },
                    "required": ["title", "description", "due_time"]
                },
                action
            )

        elif action == "delete":
            response = self.openai_function_call(
                [
                    {
                        "role": "system", "content": f"available reminders: [{self.reminder_titles()}]"
                    },
                    {
                        "role": "user", "content": arg["prompt"]
                    }
                ],
                {
                    "name": action,
                    "description": "Delete a reminder",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "title of the reminder to be deleted",
                            },
                        }
                    },
                    "required": ["title"]
                },
                action
            )

        
        fn_name = response["choices"][0]["message"]["function_call"]["name"]
        fn = function_map.get(fn_name)
        args = json.loads(response["choices"][0]["message"]["function_call"]["arguments"])

        fn_response = fn(**args)

        print(response)

        

    
    def openai_function_call(self, messages, function_obj, function_call_str):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages = messages,
            functions = [
                function_obj
            ],
            function_call = {"name": function_call_str}
        )

        return response

        
reminder = Reminders()
arg = {
    "prompt": "in my reminders, create a reminder a grooming for my dog sainty on tomorrow at eleven in the morning"
}
reminder.prior_fn(arg)
        

        