import re

text = "make a note for me just take a note of the current time in the current date"
regex = r"((notes|note|plans|plan).+?(check|update|modify|add|create|make|write|read|open|delete|remove)|(update|modify|add|create|make|write|read|open|check|delete|remove).+?(notes|note|plans|plan))"

match = re.search(regex, text)
if match:
    print(match)