import urllib.request
from bs4 import BeautifulSoup

class WebCrawler:
    MAX_DEPTH = 0

    def __init__(self):
        MAX_DEPTH = 1

    def getPageHtml(self, url, depth):
        with urllib.request.urlopen(url) as response:
            html = response.read()

        soup = BeautifulSoup(html, 'html.parser')('a')
        for link in soup:
            link = link['href']
        

crawler = WebCrawler()

crawler.getPageHtml('https://runescape.com/')