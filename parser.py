import os
import requests
from pathlib import Path
from bs4 import BeautifulSoup

url = 'http://tululu.org/b1/'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')
title_tag = soup.find('h1')
print('Название книги: ' + title_tag.text[:title_tag.text.find(':')]+'\n' + 'Автор:' + title_tag.text[4 + title_tag.text.find(':'):])

