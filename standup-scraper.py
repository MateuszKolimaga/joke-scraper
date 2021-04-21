import requests
from bs4 import BeautifulSoup
#import requests

#r=requests.get("https://scrapsfromtheloft.com/")
#print(r.status_code)

URLS = [
'https://scrapsfromtheloft.com/2018/12/19/pete-holmes-dirty-clean-transcript/',
'https://scrapsfromtheloft.com/2020/11/05/john-mulaney-snl-monologue-2020-transcript/',
'https://scrapsfromtheloft.com/2020/11/12/sam-morril-i-got-this-2020-transcript/'
]

page = requests.get(URLS[0])

soup = BeautifulSoup(page.content, 'html.parser')

results = soup.findAll('p', attrs = {'style':'text-align: justify;'}, recursive=True)

full_transcript = []
for result in results:
    full_transcript.append(result.findAllNext(text = True))

full_transcript[0] = list(filter(lambda a: a not in ['\n', '\n     (adsbygoogle = window.adsbygoogle || []).push({});\n'], full_transcript[0]))

max_index = full_transcript[0].index(' AI CONTENT END 1 ')

print(' '.join(full_transcript[0][0:max_index]))