"""Получаем html документ и сохраняем в новый файл асcоциативный массив вида: {файл:[подзаголовок, подзаголовок,...]}
"""
import re
import json
import io

h3 = r"<h3>((.|\n)*?)<\/h3>"
h3re = re.compile(h3)
name = "founders-agreement-template"
slovar = dict()

with open("{}.html".format(name)) as file:
    text = file.read()
    subtitles = re.findall(h3re, text)
    for subtitle in subtitles:
        if name in slovar.keys():
            slovar[name].append(subtitle[0].lstrip("\n\t\r").rstrip('<br/>'))
        else:
            slovar[name] = [subtitle[0].lstrip("\n\t\r").rstrip('<br/>')]

# добавить обработку подзаголовков без точки. Пока - Miscellaneous Provisions<br/>Assignment.

with io.open("literally_dump.txt", "w", encoding='utf8') as db:
    json.dump(slovar, db, ensure_ascii=False)


