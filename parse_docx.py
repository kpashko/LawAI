import nltk.tokenize
import re

listEnumerator = r"([a-zA-Z]|\d+|•)"

listTypesArray =\
    [
        r"\(?" + listEnumerator + r"\)",
        listEnumerator + r"\.?"
    ]

listTypesReg = ""
for listType in listTypesArray:
    if listTypesReg != "":
        listTypesReg += "|"
    listTypesReg += "(" + listType + ")"
listStart = r"^[ \t]*"
listEnd = r"[ \t]+\w"
listRegex = re.compile(listStart + "(" + listTypesReg + ")" + listEnd)


with open("text.txt", encoding="utf-8") as file:
    raw = file.read()
    tokens = nltk.sent_tokenize(raw)
    for token in tokens:
        if re.search(listRegex, token) != None:
            print(token)
