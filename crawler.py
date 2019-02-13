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
        self.BASE_URL = url
        self.linkIndex = set()
        self.BASE_PAGE = WebPage(url, self.BASE_DEPTH, self.MAX_DEPTH, self.linkIndex)
    
    def crawl(self, url, depth):
        page = WebPage(url, depth, self.MAX_DEPTH, self.linkIndex)

        for nestedLink in page.links:
            if nestedLink != url and nestedLink not in self.linkIndex:
                self.linkIndex.add(nestedLink)       
                self.crawl(nestedLink, page.depth+1)
    
    def startCrawl(self):
        self.linkIndex = self.BASE_PAGE.links
        startTime = time.time()

        threads = []
        for link in self.BASE_PAGE.links:
            threads.append(Thread(target = self.crawl, args = (link, self.BASE_DEPTH + 1,)))

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        print ('Crawl completed after %ds' %(time.time() - startTime))

class WebPage(object):
    def __init__(self, url, depth, maxDepth, linkIndex):
        self.ASSET_FLAG = args.assets[0]
        self.MAX_DEPTH = maxDepth
        self.depth = depth
        self.links = set()
        self.size = None
        self.linkIndex = linkIndex
        self.getPageLinks(url)

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
        if 0 == self.ASSET_FLAG:
            if self.depth < self.MAX_DEPTH:
                linkSoup = soup('a')

                #Converts anchor tags to urls
                linkSoup = re.findall(pattern, str(linkSoup))

                for link in linkSoup:
                    #Adds propper formatting for urllib to work
                    if link not in self.linkIndex:
                        if -1 == link.find('http') and link and link != url:
                            self.links.add(str('http://' + link))
                        elif link and link != url:
                            self.links.add(link)
        
        #If ASSET_FLAG true, parse all links
        elif 1 == self.ASSET_FLAG and self.depth < self.MAX_DEPTH:
            linkSoup = re.findall(pattern, str(soup))
            for link in linkSoup:
                if link not in self.linkIndex:
                    self.links.add(link)

        print('\nLink: %s \nDepth: %d \nSize: %d\n'%(url, self.depth, len(html)))

        return (self.links)

if __name__ == '__main__':
    crawler = WebCrawler(str(args.url[0]), args.depth[0])
    crawler.startCrawl()