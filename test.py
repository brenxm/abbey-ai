from main import handle_prompt

def test_prompt():
    assert handle_prompt("How are you? I know you're only an AI but I still care for you, you paved my way to my success so I thank you so much.") == True