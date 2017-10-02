import nltk.tokenize

print("neherovo")

with open("text.txt") as file:
    raw = file.read()
    tokens = nltk.sent_tokenize(raw)
    print(tokens)
    for t in tokens:
        if t[0]>='0' and t[0]<='9':
            print(t)