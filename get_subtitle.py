"""Получаем html документ и сохраняем в новый файл асcоциативный массив вида: {файл:[подзаголовок, подзаголовок,...]}
"""
import json
import io
from parse_docx import Document
from parse_docx import Subtitle
from parse_docx import Paragraph
from parse_docx import Title

doc = Document()
name = "text"
doc.parseFile("{}.txt".format(name))
doc.writeToFile("{}.html".format(name+"kek"))

#write json
slovar = dict()
titleName = ""
for elem in doc.elements:
    if type(elem) == Title:
        for sent in elem.sentences:
            titleName += sent.lstrip("\n\t\r").rstrip("\n\r\t")
        break
slovar[titleName] = dict()

numElems = len(doc.elements)
i = 0
while i < numElems - 1:
    if type(doc.elements[i]) == Subtitle:

        subtitleName = ""
        for sentence in doc.elements[i].sentences:
            subtitleName += sentence.lstrip("\n\t\r").rstrip("\n\r\t")

        subtitleContent = ""
        j = i + 1
        while j < numElems and type(doc.elements[j]) != Subtitle:
            if type(doc.elements[j]) == Paragraph:
                for sentence in doc.elements[j].sentences:
                    subtitleContent += sentence.lstrip("\n\t\r").rstrip("\n\r\t")
            j += 1

        if subtitleName != "" and subtitleContent != "":
            if subtitleName in slovar[titleName].keys():
                slovar[titleName][subtitleName].append(subtitleContent)
            else:
                slovar[titleName][subtitleName] = [subtitleContent]
    i += 1

with io.open("{}.json".format(name), "w", encoding='utf8') as db:
    json.dump(slovar, db, ensure_ascii=False)
