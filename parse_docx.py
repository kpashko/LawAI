import nltk.tokenize
import re

listHead = re.compile(r"^[ \t]*\(?([a-zA-Z]|\d+)(\)|\.)?[ \t]+\w")

with open("text.txt") as file:
    raw = file.read()
    tokens = nltk.sent_tokenize(raw)
    for token in tokens:
        if re.search(listHead, token) != None:
            print(token)
