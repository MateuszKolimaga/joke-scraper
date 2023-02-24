import multiprocessing
import requests
from bs4 import BeautifulSoup
import re

class Scraper :
    def __init__(self, urls_source_path = None):
        self.path = urls_source_path #optional path to file with urls
        self.urls = [] if self.path is None else self._load_urls()
        self.pattern = r'[\[(][a-zA-Z]*[\s]*laugh[a-z]*[\])]' #audience reaction
        self.verbose = 1
        self.sentences_num = 2 #desired length of joke
        self.jokes = []

    def scrap_urls(self):
        page = requests.get('https://scrapsfromtheloft.com/stand-up-comedy-scripts/')
        soup = BeautifulSoup(page.content, 'html.parser')
        results = soup.findAll('a', href=True)

        for i, link in enumerate(results[67 :]) :
            self.urls.append(link['href'])
            if link['href'] == 'https://scrapsfromtheloft.com/2016/11/10/george-carlin-its-bad-for-ya/' :
                break

    def filter_urls(self): #filter transcripts without the pattern in it
        if self.urls is []:
            self.scrap_urls()
        pool = multiprocessing.Pool(multiprocessing.cpu_count( ))
        self.urls = pool.map(self.__filter__, self.urls)
        self.urls = list(filter(lambda a : a is not None, self.urls))

    def set_filter_pattern(self, pattern):
        self.pattern = pattern

    def save_urls(self, path):
        if self.urls:
            f = open(path, 'w')
            f.writelines(self.urls)
            f.close()
        else :
            print("No urls that can be saved")

    def look_for_jokes(self, sentences_num = 2, verbose = 1) :
        self.sentences_num = sentences_num
        self.verbose = verbose
        if self.urls is [] :
            self.scrap_urls( )
        pool = multiprocessing.Pool(multiprocessing.cpu_count( ))
        self.jokes = pool.map(self._finder, self.urls)
        self.jokes = list(filter(lambda a : a is not None, self.jokes))

    def save_jokes(self,path):
        if self.jokes:
            jokes = []
            for joke_set in self.jokes:
                jokes.extend(joke_set)

            f = open(path, 'w', encoding='windows-1250')
            for joke in jokes:
                try:
                    f.write(joke + '\n')
                except UnicodeDecodeError:
                    pass
            f.close()
        else:
            print("No jokes that can be saved")

    def _load_urls(self):
        f = open(self.path, 'r')
        urls = f.read( ).splitlines( )
        return urls

    def _finder(self, url):
        try :
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')

            results = soup.findAll('p', attrs={'style' : 'text-align: justify;'}, recursive=True)

            full_transcript = []
            for result in results :
                full_transcript.append(result.findAllNext(text=True))

            full_transcript[0] = list(
                filter(lambda a : a not in ['\n', '\n     (adsbygoogle = window.adsbygoogle || []).push({});\n'],
                       full_transcript[0]))

            max_index = full_transcript[0].index(' AI CONTENT END 1 ')

            text = ' '.join(full_transcript[0][0 :max_index])

            pattern = r''
            for i in range(self.sentences_num):
                pattern += r'[.?!][,“\w\s\d”]+'
            pattern += r'[.?!][\w\s\d”]*(?=[\[(][a-zA-Z]*[\s]*laugh[a-z]*[\])])'

            jokes = re.findall(pattern, text, re.IGNORECASE)
            jokes = list(map(lambda a: a.lstrip('.?!”'), jokes))

            #print(f'Jokes founded in {url}: {len(punchlines)} , (context = {self.sentences_num-1} sentence(s)): ')
            if self.verbose :
                for punchline in jokes :
                    print(punchline)
            return jokes
        except (ValueError, IndexError, requests.exceptions.MissingSchema, UnicodeEncodeError) as e :
            pass

    def _filter(self, url):
        try :
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')
            results = soup.findAll('p', attrs={'style' : 'text-align: justify;'}, recursive=True)

            full_transcript = []
            for result in results :
                full_transcript.append(result.findAllNext(text=True))

            full_transcript[0] = list(
                filter(lambda a : a not in ['\n', '\n     (adsbygoogle = window.adsbygoogle || []).push({});\n'],
                       full_transcript[0]))

            max_index = full_transcript[0].index(' AI CONTENT END 1 ')

            text = ' '.join(full_transcript[0][0 :max_index])
            
            if re.search(self.pattern, text, re.IGNORECASE) :
                print(f'[V] Pattern found in {url}')
                return url + '\n'
            else :
                print(f'[X] Pattern not found in {url}')
        except (ValueError, IndexError, requests.exceptions.MissingSchema) as e :
            pass

if __name__ == '__main__' :
    scraper = Scraper(urls_source_path='transcript_urls.txt')
    scraper.look_for_jokes(sentences_num=2)
    scraper.save_jokes('jokes.txt')
