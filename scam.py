import requests
from bs4 import BeautifulSoup
#from selenium import webdriver
#driver = webdriver.Safari()

url = "https://www.lawinsider.com/tags?cursor=CkYKDAoFY291bnQSAwjODBIyahVzfmxhd2luc2lkZXJjb250cmFjdHNyGQsSA1RhZyIQbWFzdGVyLWFncmVlbWVudAwYACAB"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'}

#driver.get(url)
#html = driver.page_source
html = requests.get(url)
soup = BeautifulSoup(html.text)

contract_types_list = soup.find('div', {'class': 'list-group item-list with-letters row'})
contracts = contract_types_list.find_all('a', {'class':'dynamic-linkset list-group-item col-md-6'})

# for contract in contracts:
#     list_of_contracts.append()
with open("contr_types","a")as out:
    for c in contracts:
        out.write(str(c['href']+"\n"))