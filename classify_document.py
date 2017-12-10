import json
import io
from parse_docx import Document, Subtitle, Paragraph, Title
import glob
import pandas as ps
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

def ReadData(paths):
    slovar = dict()

    doc = Document()

    for text in paths:
        name = text.rsplit('/')[-1].rstrip('.txt')
        doc.parseFile(text)

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

    return slovar

def TrainClassifiers(data):
    classifiers = dict()
    for className, classFeatures in data.items():
        X, Y = [], []
        for subtitle, content in classFeatures.items():
            X.append(subtitle)
            Y.append(0)
            for contentText in content:
                X.append(contentText)
                Y.append(1)

        data = ps.DataFrame({'Text': X, 'Flag': Y})
        data.Text = data.Text.apply(lambda x: x.lower())
        data.Text = data.Text.apply(lambda x: x.replace('\n', ' '))

        classifiers[className] = Pipeline([('vect', CountVectorizer()),
                                           ('tfidf', TfidfTransformer()),
                                           ('mnb-clf', MultinomialNB())])
        classifiers[className] = classifiers[className].fit(data.Text, data.Flag)
    return classifiers

def Classify(classes, test):
    maxWeight = -999999.0
    resultClass = []

    X, Y = [], []

    for className, classFeatures in test.items():
        for subtitle, content in classFeatures.items():
            X.append(subtitle)
            Y.append(0)
            for contentText in content:
                X.append(contentText)
                Y.append(1)

    data = ps.DataFrame({'Text': X, 'Flag': Y})
    data.Text = data.Text.apply(lambda x: x.lower())
    data.Text = data.Text.apply(lambda x: x.replace('\n', ' '))

    for className, classifier in classes.items():
        classWeight = classifier.score(data.Text, data.Flag)
        print(className, classWeight)
        if classWeight > maxWeight:
            maxWeight = classWeight
            resultClass = []
            resultClass.append(className)
        elif classWeight == maxWeight:
            resultClass.append(className)
    return resultClass

if __name__ == '__main__':
    trainData = ReadData(glob.glob('Lawyer Test/*.txt'))
    with io.open("output/ontology.json", "w+", encoding='utf8') as db:
        json.dump(trainData, db, ensure_ascii=False, indent=4, sort_keys=True)

    classes = TrainClassifiers(trainData)

    print('\nResult: ', Classify(classes, ReadData(["test1_LOAN_AGREEMENT.txt"])), '\n')
    print('\nResult: ', Classify(classes, ReadData(["test2_CREDIT_AGREEMENT.txt"])), '\n')
    print('\nResult: ', Classify(classes, ReadData(["test3_PURCHASE_CONTRACT.txt"])), '\n')
