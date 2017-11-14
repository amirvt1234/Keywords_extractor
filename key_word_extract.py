from __future__ import division, print_function

from collections import defaultdict
import nltk
from bs4 import BeautifulSoup
import html2text

try: # Python 3
    import http.cookiejar as cookielib
except: # Python 2
    import cookielib

try: # Python 3
    import urllib.request as urllib
except: # Python 2
    import urllib2 as urllib
#Fix me
#Make sure all the nltk packages used here are alreay downloaded
#Rather than downloading all packages I can just the necessary packages
try:
    _ = nltk.tokenize.sent_tokenize('string')
    _ = nltk.tokenize.word_tokenize('string')
    _ = nltk.corpus.stopwords.words('english')
    _ = nltk.tokenize.RegexpTokenizer(r'\w+')
except Exception:
    nltk.download('all')


class KeyWord(object):

    def __init__(self, url, language='english', html_header=None):
        self.language = language
        self.url = url
        self.headers = html_header
        if self.headers is None:
            self.headers = {'User-agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64)'    + 
                'AppleWebKit/537.36 (KHTML, like Gecko)' + 
                'Chrome/37.0.2062.120 Safari/537.36'}

    def stop_words(self):
        """Use nltk default stopwords..."""
        stopwords = set(nltk.corpus.stopwords.words('english'))
        stopwords.add('amp')
        return stopwords

    def acceptable_words(self, w):
        """Check the lenght of the word and if it is in not an stopword"""
        return (2 <= len(w) <= 40) and w.lower() not in self.stop_words()

    def get_soup(self):
        req = urllib.Request(self.url, headers=self.headers)
        cj = cookielib.CookieJar() # to make sure that it will work with webpages that need to install cookie
        opener = urllib.build_opener(urllib.HTTPCookieProcessor(cj))
        response = opener.open(req)
        html = response.read().decode('utf8', errors='ignore')
        response.close()
        soup = BeautifulSoup(html, 'lxml')
        return soup
    
    def get_html(self):
        htmltext = self.get_soup().encode('utf-8').decode('utf-8','ignore')
        return htmltext

    def html_2_text(self):
        """Clean html and store it as a string"""
        h = html2text.HTML2Text()
        h.ignore_links = True
        h.ignore_images = True
        return h.handle (self.get_html())

    def get_title(self):
        """Extract the title of the html"""
        title = []
        soup = self.get_soup()
        if soup.find('title'):
            for words in soup.find('title').text.strip().split():
                if self.acceptable_words(words):
                    title.append(words)
        return title

    def get_keywords(self):
        """Check if there is any keyword defined already"""
        desc = []
        soup = self.get_soup()
        if soup.find("meta",attrs={"name":"keywords"}):
            desc.append(soup.find("meta",attrs={"name":"keywords"}).get("content"))
        return desc

    def get_top_words(self):
        """Get the list of the words that are repeated the most"""
        worddict = defaultdict(lambda:0)
        sent_tokenize_list = nltk.tokenize.sent_tokenize(self.html_2_text())
        tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
        for sent in sent_tokenize_list:
            words = tokenizer.tokenize(sent)
            for word in words:
                wl = word
                if word[1:]==word[1:].lower():
                    wl = word.lower() 
                if self.acceptable_words(word):
                    worddict[wl] += 1
        sortedw = sorted((worddict[i],i) for i in worddict)[::-1][:10]
        return [x[1] for x in sortedw]

if __name__ == '__main__':
    urls = ['http://www.cnn.com/2013/06/10/politics/edward-snowden-profile/',
           'http://blog.rei.com/camp/how-to-introduce-your-indoorsy-friend-to-the-outdoors/',
           'https://www.amazon.com/Cuisinart-CPT-122-Compact-2-Slice-Toaster/dp/B009GQ034C/ref=sr_1_1?s=kitchen&ie=UTF8&qid=1431620315&sr=1-1&keywords=toaster']
    results = []
    for url in urls:
        tresult = []
        kwclass    = KeyWord(url)
        topwords   = kwclass.get_top_words()
        titlewords = kwclass.get_title()
        ifkeywords = kwclass.get_keywords()

        results.append(topwords+titlewords+ifkeywords)

    # Here I will print the keywords pool that 
    # we need to use for extracting key phrases...
    print('Extracted keywords for CNN:\n')
    print(results[0])
    print('\n\n')
    print('Extracted keywords for hiking blog:\n')
    print(results[1])
    print('\n\n')
    print('Extracted keywords for Amazon:\n')
    print(results[2])
    print('\n\n')

