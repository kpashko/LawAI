"""Получаем html документ и сохраняем в новый файл асcоциативный массив вида: {файл:[подзаголовок, подзаголовок,...]}
"""
import json
import io
from parse_docx import Document, Subtitle, Paragraph, Title
import glob


doc = Document()

texts = glob.glob('Lawyer Test/*.txt')
slovar = dict()

for text in texts:
    name = text.rsplit('/')[-1].rstrip('.txt')
    doc.parseFile(text)
    # doc.writeToFile("output/{}.html".format(name))

    titleName = ""
    for elem in doc.elements:
        if type(elem) == Title:
            for sent in elem.sentences:
                titleName += sent.strip("\n\t\r")
            break
    if titleName == "":
        continue
    slovar[titleName] = dict()

    numElems = len(doc.elements)
    i = 0
    while i < numElems - 1:
        if type(doc.elements[i]) == Subtitle:

            subtitleName = ""
            for sentence in doc.elements[i].sentences:
                subtitleName += sentence.strip("\n\t\r")

            subtitleContent = ""
            j = i + 1
            while j < numElems and type(doc.elements[j]) != Subtitle:
                if type(doc.elements[j]) == Paragraph:
                    for sentence in doc.elements[j].sentences:
                        subtitleContent += sentence.strip("\n\t\r")
                j += 1

            if subtitleName != "" and subtitleContent != "":
                if subtitleName in slovar[titleName].keys():
                    slovar[titleName][subtitleName].append(subtitleContent)
                else:
                    slovar[titleName][subtitleName] = [subtitleContent]
        i += 1
    if len(slovar[titleName]) == 0:
        slovar.pop(titleName)

with io.open("output/allo.json", "w+", encoding='utf8') as db:
    json.dump(slovar, db, ensure_ascii=False, indent=4, sort_keys=True)
