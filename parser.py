import os
import requests
from pathlib import Path
from bs4 import BeautifulSoup

url = 'http://tululu.org/b1/'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')
title_tag = soup.find('h1')
f=(title_tag.text.strip())
print(f.split('\xa0 :: \xa0'))