from function_interface import FunctionsInterface
from abbey import AbbeyAI
from tts import TextToSpeech
from stt import VoiceInput
from audioplayer import AudioPlayer
from threading import Lock
from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QApplication
import subprocess
from dynamic_memory import AIMemory
import pygetwindow as gw
import pyautogui
from test import PromptRequest
from keyword_parser import KeywordParser
from fn_module.vscode.vscode_module import get_vscode, write_vscode
import re
import datetime

# Handle logic flow data schema
prompt_mem = {
    "prompt": "",
    "functions": []
}
queue_lock = Lock()
audio_queue = []
tts_queue = []


def display_blackboard(response):
    pattern = r'!!!blackboard-start!!!.+!!!blackboard-end!!!'
    match = re.search(pattern, response, re.DOTALL)
    
    if match:
        #print(f"displayed to blackboard: {match.group()}")
        pass
    

memory = AIMemory()
audio_player = AudioPlayer(tts_queue)
tts = TextToSpeech(tts_queue, audio_player)
voice_input = VoiceInput(audio_player)
abbey = AbbeyAI(tts_queue, None, audio_player, tts)
fn_interface = FunctionsInterface()
request = PromptRequest("gpt-4")
keyword_parser = KeywordParser()


abbey.set_personality("You are my AI assistant named Abbey. You respond with direct to the point, elaborated but straight to point answer. Address me as 'boss' or 'sir' without comma ',' similar to Tony Stark's personal AI named Jarvis.")

abbey.set_name("Abbey")

blackboard_open = False

def get_active_window_title():
    window = gw.getWindowsWithTitle(pyautogui.getActiveWindow().title)
    
    if window:
        return window[0].title.lower()
    return None


def write_message_to_pipe(message):
    if message:
        with open("gui/message_transfer.txt", "w") as f:
            f.write(message)
            

def handle_prompt_test(prompt_input):
    
    date = datetime.datetime.now()
    
    prompt_mem["prompt"] = prompt_input
    
    request.clear_message()
    
    request.add_message({
        "role": "system",
        "content": f"Current time and date: {date.strftime('%I:%M %p, %m-%d-%Y')}"
    })
    
     # Add tone to system prompt
    laconic_prompt = {
        "role": "system",
        "content": "You are an assistant named Summer. You answer with brief, laconic, succint and concise responses. Address me as 'boss' or 'sir' similar to Tony Stark's personal AI named Jarvis."}
    
    # Get memory data and include to new prompt
    memory_data = '\n'.join(memory.chat_history)
    memory_data_str = {
        "role": "system",
        "content": f"Recent chat history: \n{memory_data}"
        }
    
    request.add_message(laconic_prompt),
    request.add_message(memory_data_str)
    
    response_obj = keyword_parser.parse(prompt_input)
    
    
    
    # Call all prior_functions in response_obj
    for k_obj in response_obj["function_objs"]:
        if 'prior_function' in k_obj:
            while len(k_obj['prior_function']) > 0:
                fn_ar = k_obj['prior_function'].pop(0)
                fn = fn_ar["function"]
                arg = fn_ar["arg"]
                arg["prompt"] = prompt_input
                arg["keyword_obj"] = k_obj
                fn_response = fn(arg)
                
                try:
                    response_obj['prompt_input'] = fn_response["prompt"]
                except:
                    pass
            
    # Sends OPENAI API request and result is assigned to response
    print(response_obj['prompt_input'])
    response = request.prompt(response_obj["prompt_input"])
    
    memory.add_chat_history("user", response_obj["prompt_input"])
    
    
    sentence_pattern = r'[\D]{2,}[!\.\?](?<!\!)'
    blackboard_pattern = {
        "opening_tag": r'!!!blackboard-start!!!',
        "closing_tag": r'!!!blackboard-end!!!'
    }
    
    full_message = ""
    sentence = ""
    stream_function = False
    blackboard_data = ""
    
    for chunk in response:
        try:
            chunk = chunk['choices'][0]['delta']['content']
            #print(chunk)
            sentence += chunk
            full_message += chunk
            
            sentence_match = re.search(sentence_pattern, sentence)
            blackboard_match = re.search(blackboard_pattern["opening_tag"], sentence)
            
            if stream_function:
                blackboard_data += chunk
                sentence = ""
                closing_tag_match = re.search(blackboard_pattern["closing_tag"], blackboard_data, re.DOTALL)
                
                print(blackboard_data)
                if closing_tag_match:
                    stream_function = False
                    split_string = blackboard_data.split("!!!blackboard-end!!!")
                    
                    sentence += split_string[1]
                    
                    continue
                
            
            elif blackboard_match:
               stream_function = True
               unsliced_string = blackboard_match.group(0)
               
               # index 0 will be sent to the converter, and 1 will be sent to blackboard data if not empty
               string_list = unsliced_string.split("!!!blackboard-start!!!")
               sentence = sentence.replace("!!!blackboard-start!!!", "")
               sentence += string_list[0]
               
               tts.convert(sentence, audio_player.listen)
               sentence = ""
               blackboard_data += string_list[1]
               
            elif sentence_match:
                tts.convert(sentence, audio_player.listen)
                sentence = ""
           
        except:
            
            if sentence:
                tts.convert(sentence, audio_player.listen)
                sentence = ""
    
    # Stream and return full message
    #full_message = abbey.stream_result(response, tts.convert, audio_player.listen)
    
    # Add response of assistant to memory
    memory.add_chat_history('assistant', full_message)
    
    # Execute post response functions
    for fn_obj in response_obj["function_objs"]:
        if 'post_function' in fn_obj:
            while len(fn_obj['post_function']) > 0:
                
                fn_ar = fn_obj['post_function'].pop(0)
                
                fn = fn_ar["function"]
                
                if 'keyword_obj' not in arg:
                    arg["keyword_obj"] = fn_obj
            
                if 'arg' in fn_ar:
                    arg = fn_ar["arg"]
                    fn(arg)
                    
                else:
                    fn()
            
# keyword_object initiation:
keyword_parser.add_object([
    {
        "keywords": re.compile(r'(?i)(display|show|present|reveal|exhibit|demonstrate|bring\s+up|put\s+up|project|illustrate|highlight|flash|render|visualize).*?blackboard'),
        "type": "function_call",
        "prior_function": [
            {
                "function": request.add_message,
                "arg": {
                    "role": "system",
                    "content": "Format your response to !!!blackboard-start!!!<content>!!!blackboard-end!!! to display it on blackboard where the content is the string to be displayed. e.g. !!!blackboard-start!!!200 / 2 = 100!!!blackboard-end!!!, the content is 200 / 2 = 100."
                }
            }
        ]
    },
    {
        "keywords": ['active code', 'current code', 'get active code'],
        "type": "keyword_replace",
        "prior_function": [
            {
                "function": get_vscode,
                "arg": {
                        "get_method": "activeCode",
                        "label": "code",
                        "prompt": prompt_mem["prompt"]
                    }
            }
        ]
    },
    {
        "keywords": ["highlighted code"],
        "type": "keyword_replace",
        "prior_function": [
            {
                "function": get_vscode,
                "arg": {
                    "get_method": "highlightedCode",
                    "label": "highlighted code",
                    "prompt": prompt_mem["prompt"]
                }
            }
        ],
        "post_function": []
    },
    {
        "keywords": ["vscode folder path", "VS Code folder path"],
        "type": "keyword_replace",
        "prior_function": [
            {
                "function": get_vscode,
                "arg": {
                    "get_method": "folderPath",
                    "label": "vscode folder path",
                    "prompt": prompt_mem["prompt"]

                }
            }
        ]
    },
    {
        "keywords": re.compile(r'\b(clear|delete)\b(?:\s*\bour\b)?\s*\bchat history\b', re.IGNORECASE),
        "type": "function_call",
        "prior_function": [
            {
                "function": request.add_message,
                "arg": {
                    "role": "system",
                    "content": "Send confirmation to the user that you just deleted the Chat history"
                }
            }
        ],
        "post_function": [{"function": memory.clear}]
    }
]
)
    
voice_input.init(handle_prompt_test)