import nltk.tokenize
from enum import Enum
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

def SentenceIsList(sentence):
    return re.match(listRegex, sentence) != None

def RemoveListPrefix(sentence):
    matchResult = re.match(listRegex, sentence)
    if matchResult:
        start, end = matchResult.span()
        return sentence[end-1:]
    else:
        return sentence

######################################################################################

class SentenceType(Enum):
    Invalid = 1 #for internal usage
    Simple = 2
    ListElem = 3
    EndOfParagraph = 4

def ClassifySentence(sentenceString):
    if SentenceIsList(sentenceString):
        return SentenceType.ListElem
    elif sentenceString.rstrip(" \t\r").endswith("\n"):
        return SentenceType.EndOfParagraph
    else:
        return SentenceType.Simple

######################################################################################

def EscapeHTML(string):
    return string.replace("\n", "<br/>").replace("\r", "")

class Paragraph():
    def __init__(self):
        self.sentences = []

    def addSentence(self, sentence):
        self.sentences.append(sentence)

    def writeToFile(self, file):
        file.write("<p>\n")
        for sentence in self.sentences:
            file.write(EscapeHTML(sentence))
        file.write("</p>\n")

class BulletList():
    def __init__(self):
        self.sentences = []

    def addSentence(self, sentence):
        self.sentences.append(RemoveListPrefix(sentence))

    def writeToFile(self, file):
        file.write("<ul>\n")
        for sentence in self.sentences:
            file.write("<li>")
            file.write(EscapeHTML(sentence))
            file.write("</li>\n")
        file.write("</ul>\n")

class Document:
    def __init__(self):
        self.elements = []

    def parseFile(self, pathToFile):
        with open(pathToFile, encoding="utf-8") as file:
            raw = file.read()
            tokens = nltk.sent_tokenize(raw)

            if len(tokens) == 0:
                return

            self.elements.clear()
            currType = SentenceType.Invalid
            for token in tokens:
                tokenType = ClassifySentence(token)

                if tokenType != currType or tokenType == SentenceType.EndOfParagraph:
                    if tokenType == SentenceType.ListElem:
                        self.elements.append(BulletList())
                    else:
                        self.elements.append(Paragraph())

                self.elements[-1].addSentence(token)
                currType = tokenType

    def writeToFile(self, pathToFile):
        with open(pathToFile, mode="wt", encoding="utf-8") as file:
            file.write("<!DOCTYPE HTML PUBLIC \" -//W3C//DTD HTML 4.01//EN\"\n\"http://www.w3.org/TR/html4/strict.dtd\">\n<HTML>\n<HEAD>\n<META charset=\"utf-8\">\n<TITLE>Parsed document</TITLE>\n</HEAD>\n<BODY>\n")
            for element in self.elements:
                element.writeToFile(file)
            file.write("</BODY>\n</HTML>")

######################################################################################

doc = Document()
doc.parseFile("text.txt")
doc.writeToFile("text_out.html")
