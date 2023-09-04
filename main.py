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

input_type = "press_to_speak"  # press to speak or voice activated
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
keyword_parser.add_object(
        {
        "keywords": re.compile(r'(?i)(display|show|present|reveal|exhibit|demonstrate|bring\s+up|put\s+up|project|illustrate|highlight|flash|render|visualize).*?blackboard'),
        "type": "function_call",
        "prior_fn_args": {
            "role": "system",
            "content": "Format your response to !!!blackboard-start!!!<content>!!!blackboard-end!!! to display it on blackboard where the content is the string to be displayed. e.g. !!!blackboard-start!!!200 / 2 = 100!!!blackboard-end!!!, the content is 200 / 2 = 100."
        },
        "prior_function": request.add_message,
    }
)

keyword_parser.add_object(
    {
        "keywords": ["clear our chat history", "clear the chat history"],
        "type": "function_call",
        "prior_fn_args": {
            "role": "system",
            "content": "Send confirmation to the user that you just deleted the Chat history"
        },
        "prior_function": request.add_message,
        "post_function": memory.clear
    }
)


abbey.set_personality("You are my AI assistant named Abbey. You respond with direct to the point, elaborated but straight to point answer.")

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
    
    request.clear_message()
     # Add tone to system prompt
    laconic_prompt = {
        "role": "system",
        "content": "You are an assistant. You answer with brief, laconic, succint and concise responses. Explain by conversation, not by list of items. Few subject at a time."}
    
    # Get memory data and include to new prompt
    memory_data = '\n'.join(memory.chat_history)
    memory_data_str = {
        "role": "system",
        "content": f"Recent chat history: \n{memory_data}"
        }
    
    request.add_message(laconic_prompt),
    request.add_message(memory_data_str)
    
    
    response_obj = keyword_parser.parse(prompt_input)
    
    
    
    
    memory.add_chat_history("user", response_obj["prompt_input"])
    
    # Sends the request and response is received
    response = request.prompt(response_obj["prompt_input"])
    
    
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
    
    print(response_obj)
    # Execute post response functions
    while len(response_obj["functions"]) > 0:
        fn = response_obj["functions"].pop(0)
        if response_obj["args"]:
            fn(response_obj["args"])
        else:
            fn()
    

def handle_prompt(prompt_input):
    
    # Result 1 or 2
    route_code = abbey.prompt_router(prompt_input)

    if route_code == '1':
        result_obj = abbey.general_prompt(prompt_input)
        
    elif route_code == '2':
        window = get_active_window_title()
        if "visual studio code" in window:
            fn_interface.load('vscode')
            
        result_obj = abbey.function_prompt(prompt_input, fn_interface.functions)
        print(result_obj)
        
    else:
        print(route_code)
        print('hallucinated response')
        return

    if result_obj["stream"]:
        # Start convertion of the text generated from openai, arg is an audio player function
        
        print(result_obj)
        # Add to user's prompt to chat history
        
        abbey.memory.add_chat_history("user", prompt_input)
        
        # Full response message is returned after all chunks are read
        full_message = abbey.stream_result(result_obj["content"], tts.convert, audio_player.listen)
        
        # Add openai full response to chat history
        abbey.memory.add_chat_history("assistant", full_message)
        
        
    else:
        print("didn't get an object")
    return True
        

voice_input.init(handle_prompt_test)