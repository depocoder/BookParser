import os
import requests
from pathlib import Path
from bs4 import BeautifulSoup

url = 'http://tululu.org/b1/'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')
title_tag = soup.find('h1')
f=(title_tag.text.strip())
book = f.split(' \xa0 :: \xa0 ')
print('Название книги:', book[0])
print('Автор книги:', book[1])