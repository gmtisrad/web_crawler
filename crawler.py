import urllib
from bs4 import BeautifulSoup
import re

class WebCrawler(object):
    def __init__(self, url, maxDepth):
        self.MAX_DEPTH = maxDepth
        self.BASE_DEPTH = 0
        self.BASE_PAGE = -1
        self.BASE_URL = url
        self.linkIndex = -1
        print(self.MAX_DEPTH)
    
    def crawl(self, url, depth):
        page = WebPage(url, depth+1)
        linkIndexCopy = self.linkIndex.copy()
        for nestedLink in page.links:
            if nestedLink not in linkIndexCopy and nestedLink != url and page.depth < self.MAX_DEPTH:
                self.linkIndex.add(nestedLink)
                print('Link: %s Depth: %d'%(nestedLink, page.depth))                    
                self.crawl(nestedLink, page.depth)
    
    def startCrawl(self):
        self.BASE_PAGE = WebPage(self.BASE_URL, self.BASE_DEPTH)
        self.linkIndex = self.BASE_PAGE.links
        
        for link in self.BASE_PAGE.links:
            self.crawl(link, self.BASE_DEPTH)

        
        
class WebPage(object):
    def __init__(self, url, depth):
        self.depth = depth
        self.links = set()
        self.getPageLinks(url)

    def getPageLinks(self, url):
        try:
            response = urllib.request.urlopen(url)
        except urllib.error.HTTPError as err:
            print(err.code)
            return
        except urllib.error.URLError as err:
            print('URL Error encountered')
            return
        
        html = response.read()

        soup = BeautifulSoup(html, 'html.parser')('a')

        #Converts anchor tags to urls
        for i, link in enumerate(soup):
            soup[i] = re.findall('(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9]\.[^\s]{2,})', str(link['href']))

        for link in soup:
            if link != [] and link[0]:
                self.links.add(str(link[0]))

        return self.links

    


crawler = WebCrawler('https://Runescape.com', 2)

crawler.startCrawl()