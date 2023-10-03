import re

text = "This is the code I've written. @@@ What is life, baby don't hurt me, don't hur me, no more. @@@"

def test_fn_1(chunk):
    print(f"test 1: {chunk}")

def test_fn_2(chunk):
    print(f"test 2: {chunk}")

fns = [test_fn_1, test_fn_2]

def start(text):

        text = text.split(" ")
        sentence = ""
        full_message = ""
        parsing = False
        
        try:
            for chunk in text:
                sentence += chunk
                full_message += chunk

                sentence_match = re.search(r'[\D]{2,}[!\.\?](?<!\!)', sentence)

                

                if chunk == "@@@":
                    if not parsing:
                        parsing = True

                    else:
                        parsing = False

                    continue

                if parsing:
                    for fn in fns:
                        fn(chunk)

                if sentence_match:
                    print(f"converted to voice and played: {sentence}")
                    sentence = ""
                    continue
            

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
                print(f"converted to voice and played: {sentence}")

            
        return full_message

start(text)

