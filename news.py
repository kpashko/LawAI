import requests
from bs4 import BeautifulSoup
#from selenium import webdriver
import re
import pickle
import numpy as np
import time
import sys
#from pyvirtualdisplay import Display
#from PyQt5.QtWebKitWidgets import QWebPage
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl
from PyQt5.QtCore import QEventLoop



#driver = webdriver.Safari()
#driver.maximize_window()

ctr = r'(/contracts/tagged/(.*))'
rectr = re.compile(ctr)

links = "contr_types"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'}

ontology = {}


class Client(QWebEnginePage):
    def __init__(self, url):
        self.app = QApplication(sys.argv)
        QWebEnginePage.__init__(self)
        self.html = ''
        self.loadFinished.connect(self._on_load_finished)
        self.load(QUrl(url))  # Ignote mainFrame from PyQt4
        self.app.exec_()

    def _on_load_finished(self):
        self.html = self.toHtml(self.Callable)
        print('Load finished')

    def Callable(self, html_str):
        self.html = html_str
        self.app.quit()


with open(links) as links:
    urls = links.readlines()
    for url in urls:
        #r= requests.get("http://lawinsider.com"+url, headers=headers)
        client_response = Client("http://lawinsider.com"+url)
        source = client_response.html
        soup = BeautifulSoup(source, 'lxml')
        #html = driver.page_source
        ##html = r.text
        ##rendered = Render(html).html
        #html = requests.get("http://lawinsider.com"+url, headers=headers)
        ##soup = BeautifulSoup(rendered, 'html.parser')
        sidebar = soup.find('ul', {'id':'sidebar-related-clauses-by-tag'})
        clauses = sidebar.find_all('li', {'class':'list-group-item'})
        match = re.match(rectr, url)
        for clause in clauses:
            if url in ontology.keys():
                ontology[match.group(2)].append(clause.contents)
            else:
                ontology[match.group(2)] = clause.contents
        time.sleep(3)
    np.save("ONTOLOGIYA", ontology)
        #with open("ONTOLOGIYA.pkl",'w') as onto:
        #    pickle.dump(ontology,ontology,pickle.HIGHEST_PROTOCOL)
