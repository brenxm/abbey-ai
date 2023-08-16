from main import handle_prompt

def test_prompt():
    assert handle_prompt("Testing only, say 'yes'") == True