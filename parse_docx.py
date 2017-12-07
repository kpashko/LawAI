import nltk.tokenize
from enum import Enum
import re

listCharEnum = r"[a-zA-Z]"
listSpecialEnum = r"(\d{1,2}|•)"
listAnyEnum = r"(" + listCharEnum + r"|" + listSpecialEnum + r")"

listTypesArray =\
    [
        r"\(?" + listAnyEnum + r"\)",
        listSpecialEnum + r"\.?",
        listCharEnum + r"\."
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


def SentenceIsSubtitle(sentence):
    return len(sentence) <= 40 and sentence[-1] == '\n'


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
    Title = 5
    Subtitle = 6


def ClassifySentence(sentenceString):
    if SentenceIsList(sentenceString):
        return SentenceType.ListElem
    elif SentenceIsSubtitle(sentenceString):
        return SentenceType.Subtitle
    elif sentenceString.rstrip(" \t\r").endswith("\n"):
        return SentenceType.EndOfParagraph
    else:
        return SentenceType.Simple

######################################################################################


def EscapeHTML(string):
    return string.replace("\n", "<br/>").replace("\r", "")


class Title:
    def __init__(self):
        self.sentences = []

    def addSentence(self, sentence):
        self.sentences.append(sentence)

    def writeToFile(self, file):
        file.write("<h1>\n")
        for sentence in self.sentences:
            file.write(EscapeHTML(sentence))
        file.write("</h1>\n")

nonWordRegex = re.compile(r"[^a-zA-Z\n\s]")
wordCharsRegex = re.compile(r"[[:alpha:]]")
wordNumsRegex = re.compile(r"\d+")

class Subtitle:
    def __init__(self):
        self.sentences = []

    def addSentence(self, sentence):
        str = re.sub(nonWordRegex, "", sentence.lower()).strip("  ")
        if len(str) > 3:
            if str[0].isalpha() and (str[1] == ' ' or str[1] == ' '):
                str = str[1:].strip("  ")
            elif str[-2].isalpha() and (str[-3] == ' ' or str[-3] == ' '):
                str = str[:-3] + str[-1]
                str = str.strip("  ")
        self.sentences.append(str)

    def writeToFile(self, file):
        file.write("<h3>\n")
        for sentence in self.sentences:
            file.write(EscapeHTML(sentence))
        file.write("</h3>\n")

    def isValidSubtitle(self):
        if len(self.sentences) == 1:
            stripped = self.sentences[0][:-1].rstrip("  ")
            if len(stripped) < 3:
                return False
            match = re.match(wordNumsRegex, stripped)
            if match != None:
                start, end = match.span()
                if end - start == len(stripped):
                    return False
            return True
        for i in range(len(self.sentences) - 1):
            if self.sentences[i][-1] == "\n" or re.match(wordCharsRegex, self.sentences[i]) == None:
                return False
        return True


class Paragraph:
    def __init__(self):
        self.sentences = []

    def addSentence(self, sentence):
        self.sentences.append(sentence)

    def writeToFile(self, file):
        file.write("<p>\n")
        for sentence in self.sentences:
            file.write(EscapeHTML(sentence))
        file.write("</p>\n")


class BulletList:
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

    def splitSentence(self, sentence):
        splitted = []
        sentence = sentence.replace("\r", "")
        sentence = re.sub(r"\n+", r"\n", sentence)
        preSplitted = sentence.split("\n")
        for sent in preSplitted:
            sent = sent.strip()
            if sent != "":
                if len(preSplitted) > 1:
                    sent += "\n"
                splitted.append(sent)
        if sentence[-1].rstrip(" \t" + chr(160)) != "\n":
            splitted[-1] = splitted[-1][:-1]
        return splitted

    def tokensToSentences(self, tokens, raw):
        sentences = []
        prevLookPos = 0
        numTokens = len(tokens)
        for i in range(numTokens):
            tokenEndPos = raw.find(tokens[i], prevLookPos) + len(tokens[i])
            nextTokenPos = 0
            if i == numTokens - 1:
                nextTokenPos = len(raw)
            else:
                nextTokenPos = raw.find(tokens[i+1], tokenEndPos)

            sentence = tokens[i] + raw[tokenEndPos : nextTokenPos]
            #sentence now also contains characters, missed between tokens
            sentences.extend(self.splitSentence(sentence))
            prevLookPos = tokenEndPos
        return sentences

    def parseFile(self, pathToFile):
        with open(pathToFile, encoding="utf-8") as file:
            raw = file.read()
            tokens = nltk.sent_tokenize(raw)
            sentences = self.tokensToSentences(tokens, raw)

            if len(sentences) == 0:
                return

            self.elements.clear()
            prevType = SentenceType.Invalid
            for sentence in range(len(sentences)):
                tokenType = ClassifySentence(sentences[sentence])

                if tokenType != prevType or prevType == SentenceType.EndOfParagraph:
                    if tokenType == SentenceType.Subtitle:
                        self.elements.append(Subtitle())
                    elif tokenType == SentenceType.ListElem:
                        self.elements.append(BulletList())
                    elif tokenType == SentenceType.Simple:
                        self.elements.append(Paragraph())
                    elif tokenType == SentenceType.EndOfParagraph:
                        if prevType != SentenceType.Simple:
                            self.elements.append(Paragraph())

                self.elements[-1].addSentence(sentences[sentence])
                prevType = tokenType

            for i in range(len(self.elements)):
                if type(self.elements[i]) == Subtitle:
                    title = Title()
                    for sent in self.elements[i].sentences:
                        title.addSentence(sent)
                    self.elements[i] = title
                    break

            for i in range(len(self.elements)):
                if type(self.elements[i]) == Subtitle and not self.elements[i].isValidSubtitle():
                    newElement = Paragraph()
                    for sent in self.elements[i].sentences:
                        newElement.addSentence(sent)
                    self.elements[i] = newElement

    def writeToFile(self, pathToFile):
        with open(pathToFile, mode="w+", encoding="utf-8") as file:
            file.write("<!DOCTYPE HTML PUBLIC \" -//W3C//DTD HTML 4.01//EN\"\n\"http://www.w3.org/TR/html4/strict.dtd\">\n<HTML>\n<HEAD>\n<META charset=\"utf-8\">\n<TITLE>Parsed document</TITLE>\n</HEAD>\n<BODY>\n")
            for element in self.elements:
                element.writeToFile(file)
            file.write("</BODY>\n</HTML>")
