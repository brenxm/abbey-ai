from main import handle_prompt

def test_prompt():
    assert handle_prompt("Who is Thanos? I'm scared of him") == True