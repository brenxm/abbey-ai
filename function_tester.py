loaded_keys = {
    "memory": [],
    "ai_say": 'some_ai'
}

def load_shared_utilities(obj):
    for value, key in enumerate(obj):
        if key in loaded_keys:
            print(f'found conflicting key "{key}"')
        else:
            loaded_keys[key] = value
            print(f"succesfully loaded '{key}'")


load_shared_utilities({'ai_say': 2})
print(loaded_keys)
