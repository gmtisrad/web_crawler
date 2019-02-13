import urllib
from bs4 import BeautifulSoup
import re
import argparse
from threading import Thread
import time

parser = argparse.ArgumentParser(description='Recursively crawl the web.')
parser.add_argument('url', metavar='U', type=str, nargs=(1), help='The base url for the web crawler to start from (eg. \'https://www.google.com/\')')
parser.add_argument('depth', metavar='D', type=int, nargs=(1), help='The maximum link depth for the web crawler to crawl.')
parser.add_argument('assets', metavar='A', type=int, nargs=(1), help='1 if page assets will be parsed, 0 if not.')
args = parser.parse_args()

class WebCrawler(object):
    def __init__(self, url, maxDepth):
        self.MAX_DEPTH = maxDepth
        self.BASE_DEPTH = 0
        self.BASE_PAGE = WebPage(url, self.BASE_DEPTH, self.MAX_DEPTH)
        self.BASE_URL = url
        self.linkIndex = set()
    
    def crawl(self, url, depth):
        page = WebPage(url, depth+1, self.MAX_DEPTH)
        newLinks = page.links - self.linkIndex

        for nestedLink in newLinks:
            if nestedLink != url:
                self.linkIndex.add(nestedLink)                
                self.crawl(nestedLink, page.depth)
    
    def startCrawl(self):
        self.linkIndex = self.BASE_PAGE.links
        startTime = time.time()
        linkIndexCopy = self.BASE_PAGE.links.copy()

        threads = [Thread(target = self.crawl, args = (link, self.BASE_DEPTH,)) for link in linkIndexCopy]

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        for link in self.linkIndex:
            print(link)

        print ('Crawl completed after %ds' %(time.time() - startTime))


        
        
class WebPage(object):
    def __init__(self, url, depth, maxDepth):
        self.ASSET_FLAG = args.assets[0]
        self.MAX_DEPTH = maxDepth
        self.depth = depth
        self.links = set()
        self.getPageLinks(url)
        self.size = None

    def getPageLinks(self, url):
        pattern = '(?:(?:https?|ftp):\/\/|\b(?:[a-z\d]+\.))(?:(?:[^\s()<>]+|\((?:[^\s()<>]+|(?:\([^\s()<>]+\)))?\))+(?:\((?:[^\s()<>]+|(?:\(?:[^\s()<>]+\)))?\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))?'
        try:
            response = urllib.request.urlopen(url)
        except urllib.error.HTTPError as err:
            print('Error %d: %s' %(err.code, err.reason))
            return
        except urllib.error.URLError as err:
            print('URL Error encountered')
            return
        
        html = response.read()
        self.size = len(html)

        soup = BeautifulSoup(html, 'html.parser')

        #If ASSET_FLAG false, only parse urls within an anchor tag
        if 0 == self.ASSET_FLAG and self.depth < self.MAX_DEPTH:
            linkSoup = soup('a', href=True)

            #Converts anchor tags to urls
            linkSoup = re.findall(pattern, str(linkSoup))

            for link in linkSoup:
                #Adds propper formatting for urllib to work
                if -1 == link.find('http') and link:
                    self.links.add(str('http://' + link))
                elif link:
                    self.links.add(link)
        
        #If ASSET_FLAG true, parse all links
        elif 1 == self.ASSET_FLAG and self.depth < self.MAX_DEPTH:
            linkSoup = re.findall(pattern, str(soup))
            for link in linkSoup:
                self.links.add(link)

        print('\nLink: %s \nDepth: %d \nSize: %d\n'%(url, self.depth, len(html)))

        return self.links

if __name__ == '__main__':
    crawler = WebCrawler(str(args.url[0]), args.depth[0])
    crawler.startCrawl()