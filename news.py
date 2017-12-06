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
from PyQt5.QtWebEngineWidgets import QWebEngineView
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


class Render(QWebEngineView):
    """Render HTML with PyQt5 WebKit."""

    def __init__(self, html):
        self.html = None
        self.app = QApplication(sys.argv)
        QWebEngineView.__init__(self)
        self.loadFinished.connect(self._loadFinished)
        #self.mainFrame().setHtml(html)
        ##self.load(QUrl(url))
        self.setHtml(html)

        self.app.exec_()
        #while self.html is None:
            # self.app.processEvents(
            #     QEventLoop.ExcludeUserInputEvents |
            #     QEventLoop.ExcludeSocketNotifiers |
            #     QEventLoop.WaitForMoreEvents)
        #self.app.quit()

    def _loadFinished(self, result):
        self.page().toHtml(self._callable)
        #self.app.quit()

    def Callable(self, html_str):
        self.html = html_str
        #self.app.quit()


with open(links) as links:
    urls = links.readlines()
    for url in urls:
        r= requests.get("http://lawinsider.com"+url, headers=headers)
        #html = driver.page_source
        html = r.text
        rendered = Render(html).html
        #html = requests.get("http://lawinsider.com"+url, headers=headers)
        soup = BeautifulSoup(rendered, 'html.parser')
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
