from bs4 import BeautifulSoup as soup
from urllib2 import urlopen as uReq

import re

def flipkart(d):
    print(d)
    url= 'http://scandid.in/search?q='+d+'&type=products'
    print(url)

    #uClient = uReq(url)
    uClient = uReq(url)
    page_html = uClient.read()
    uClient.close()

    page_soup = soup(page_html, "html.parser")
    print("start flipkart")
    containers = page_soup.findAll("a", {"class": "ellipsis multiline"})[0:10]
    print("found result")
    l=[]
    for i in containers:
        print(i['href'])
    print("END")
    return l


d='asus'
print(flipkart(d))