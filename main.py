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
import re
from notes import Notes
import datetime
from function_map import FunctionMap
from response_streamer import ResponseStreamer
from reminders import Reminders
from plugins.plugins import Plugins

queue_lock = Lock()
audio_queue = []
tts_queue = []

# Initialize dependencies
keyword_parser = KeywordParser()
memory = AIMemory()
notes = Notes(memory)
audio_player = AudioPlayer(tts_queue)
tts = TextToSpeech(tts_queue, audio_player)
voice_input = VoiceInput(audio_player)
abbey = AbbeyAI(tts_queue, None, audio_player, tts)
fn_interface = FunctionsInterface()
request = PromptRequest("gpt-4")
plugins = Plugins()

# Load shared utilities to be used to all plugins
plugins.load_shared_utilities({'chat_history': memory.chat_history})

plugins.load_shared_utilities({'ai_say': tts.convert})

# Load all plugin instances
plugins.load_plugins(['./plugins/'])

# Register all loaded plugins to keyword_parser
keyword_parser.register_plugins(plugins.loaded_plugins)

function_map = FunctionMap()
function_map.add_function([
        {
            "name": "request.add_message",
            "function": request.add_message
        },
        {
            "name": "memory.clear",
            "function": memory.clear
        }
    ])

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
    

    enclose_prompt = {
        "role": "system",
        "content": "Ensure to wrap/enclose the part of your response with '@@' if your response has code snppet, items or list, instructions or etc. e.g. @@<code snippet>@@, @@<list of instruction/items>@@, the lesser and greater symbol are placeholder"
    }
    
    request.add_message(laconic_prompt),
    request.add_message(memory_data_str)
    
    response_obj = keyword_parser.parse(prompt_input)
    
    
    # Call all prior_functions in response_obj
    for index, k_obj in enumerate(response_obj["function_objs"]):
        if 'prior_function' in k_obj:
            for prior_fn in k_obj["prior_function"]:
                if "name" not in prior_fn:
                    fn = prior_fn["function"]

                else:    
                    fn_name = prior_fn["name"]
                    fn = function_map.get_function(fn_name)

                arg = prior_fn["arg"]
                arg["prompt"] = prompt_input
                arg["keyword_obj"] = k_obj
                fn_response = fn(arg)
                
                try:
                    response_obj['prompt_input'] = fn_response["prompt"]
                except:
                    pass

                try:
                    if fn_response["delete_prompt"] == True:
                        response_obj["prompt_input"] = ""
                except:
                    pass

                try:
                    for sys_obj in fn_response["messages"]:
                        request.add_message(sys_obj)
                except:
                    pass
                
                
                try:
                    if "wrapper_functions" in response_obj:
                        response_obj["wrapper_functions"] += fn_response["wrapper_functions"]
                        
                    else:
                        response_obj["wrapper_functions"] = fn_response["wrapper_functions"]
                except:
                    pass

                try:
                    response_obj["histories"] = fn_response["histories"]
                except:
                    pass
                    
                
                # Call additional prior function using the property 'fn_call'
                try:
                    if 'fn_call' in fn_response:
                        fn_name = fn_response["fn_call"]["name"]
                        
                        for fn_obj in function_map.functions:
                            if fn_name == fn_obj["name"]:
                                fn = fn_obj["function"]
                                arg = fn_response["fn_call"]["arg"]
                                
                                fn(arg)
                                print("SUCCESFULLY ADDED ANOTHER SYSTEM PROMPT")
                except:
                    pass
                            
                # Add additional post function with property 'post_functions'
                try:
                    if 'post_functions' in fn_response:
                        if 'post_function' not in response_obj["function_objs"][index]:
                            response_obj["function_objs"][index]["post_function"] = []
                            
                        response_obj["function_objs"][index]["post_function"] += fn_response["post_functions"]
                except Exception as e:
                    print(e)


    
    # Active parsing using @@ if has wrapper_functions
    try:
        if len(response_obj["wrapper_functions"]) > 0:
            request.add_message(enclose_prompt)
            print('added enclose prompt')
    except:
        print('error occured while adding eclose prompt')
        pass
                    
            
    # Sends OPENAI API request and result is assigned to response
    response = request.prompt(response_obj["prompt_input"])
    
    if response_obj["prompt_input"]:
        memory.add_chat_history("user", response_obj["prompt_input"])

    try:
        for history in response_obj["histories"]:
            memory.add_chat_history(history["role"], history["content"])
    except:
        pass
    
    # Add wrapper parser
    wrapper_parsers = response_obj["wrapper_functions"] if "wrapper_functions" in response_obj else []
    
    
    streamer = ResponseStreamer(wrapper_parsers, response, tts, audio_player)
    
    full_message = streamer.start()
    
    
    memory.add_chat_history('assistant', full_message)
    
    # Execute post response functions
    for fn_obj in response_obj["function_objs"]:
        if 'post_function' in fn_obj:
            for p_fn in fn_obj["post_function"]:
                if type(p_fn["name"]) == str:
                    fn_name = p_fn["name"]
                    fn = function_map.get_function(fn_name)
                else:
                    fn = p_fn["name"]
                
                try:
                    print('called function')
                    arg = p_fn["arg"]
                    arg["prompt"] = full_message
                    fn(arg)
                    
                except Exception as e:
                    print(f"ERROR FOUND: {e}")
                    try:
                        fn()
                    except:
                        pass
                
    
# keyword_object initiation:
keyword_parser.add_object([
    {
        "keywords": re.compile(r'(?i)(display|show|present|reveal|exhibit|demonstrate|bring\s+up|put\s+up|project|illustrate|highlight|flash|render|visualize).*?blackboard'),
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
        "keywords": re.compile(r'\b(clear|delete)\b(?:\s*\bour\b)?\s*\bchat history\b', re.IGNORECASE),
        "prior_function": [
            {
                "name": "request.add_message",
                "function": request.add_message,
                "arg": {
                    "role": "system",
                    "content": "Send confirmation to the user that you just deleted the Chat history"
                }
            }
        ],
        "post_function": [{
            "name": 'memory.clear',
            "function": memory.clear,
            }]
    }
]
)

keyword_parser.add_object(notes.parser_obj)
    
voice_input.init(handle_prompt_test)