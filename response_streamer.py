import traceback
import re

class ResponseStreamer():
    def __init__(self, wrapper_parser, response, tts, audio_player, sentence_pattern):
        self.wrapper_parser = wrapper_parser
        self.response = response
        self.wrapper_parsing = False
        self.parsing_fn = None
        self.tts = tts
        self.audio_player = audio_player
        self.sentence_pattern = sentence_pattern
        self.parsing_tag = False
        self.parsing_openai_tag = False
        
    def start(self):
        try:
            opening_tags, closing_tags, fns, args = zip(*[(obj["opening_tag"], obj["closing_tag"], obj["function"], obj["arg"]) for obj in self.wrapper_parser])
        except:
            opening_tags = closing_tags = fns = args = []

        sentence = ""
        full_message = ""
        arg = None
        insert_line_pos = None
        tag_str = ""
        
        openai_code_snippet_format_tag = ""    
        
        try:
            for chunk in self.response:
                chunk = chunk["choices"][0]["delta"]["content"]
                sentence += chunk
                full_message += chunk
                # Check if parsing
                if self.parsing_tag:
                   tag_str += chunk
                   for tag in closing_tags:
                        print(f" this is the tag_str: {tag_str} and this is the tag: {tag}")
                        if tag == tag_str.strip():
                            self.parsing_tag = False
                            self.wrapper_parsing = False
                            sentence = ""
                            
                elif self.parsing_openai_tag:
                        openai_code_snippet_format_tag += chunk
                        print(f'parsed first tag: {openai_code_snippet_format_tag}')
                        sentence = ""
                        if chunk == "\n":
                            self.parsing_openai_tag = False
                            
                        continue
                           
                
                elif self.wrapper_parsing:
                    if chunk == "!!!":
                        self.parsing_tag = True
                        tag_str += chunk
                        continue
                    
                    clean_chunk = chunk.strip()
                    if clean_chunk == "```":
                        print('found a tag')
                        self.parsing_openai_tag = True
                        openai_code_snippet_format_tag += chunk
                        sentence = ""
                        continue
                   
                                            
                    arg["chunk"] = chunk
                    arg["start_line"] = insert_line_pos
                    self.parsing_fn(arg)
                    insert_line_pos = arg["start_line"] + len(chunk)
                    sentence = ""
                    continue
                
                else:
                    for tag in opening_tags:
                        if tag in sentence:
                            # Toggle parsing
                            self.wrapper_parsing = True
                            
                            # Get callback function and arg
                            index = opening_tags.index(tag)
                            self.parsing_fn = fns[index]
                            arg = args[index]
                            insert_line_pos = arg["start_line"]
                            
                            # Get word prior to tag if any
                            no_tag = sentence.replace(tag, "")
                            if len(no_tag) > 0:
                                if no_tag[0]:
                                    self.tts.convert(no_tag[0], self.audio_player.listen)
                                
                            sentence = ""
                            continue
                        
                    sentence_match = re.search(self.sentence_pattern, sentence)
                    if sentence_match:
                        self.tts.convert(sentence, self.audio_player.listen)
                        sentence = ""
            

        except Exception as e:
            '''
            print(f"ERROR DUDE: {e}")
            print(f"ERROR TYPE: {type(e).__name__}")
            print("ERROR TRACEBACK:")
            traceback.print_tb(e.__traceback__)
            print(f"ERROR ARGS: {e.args}")
            '''
            print(f"SENTENCES ENDING {sentence}")
            if sentence:
                self.tts.convert(sentence, self.audio_player.listen)

            
            
        return full_message