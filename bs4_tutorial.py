import requests
from bs4 import BeautifulSoup

url = 'https://www.franksonnenbergonline.com/blog/are-you-grateful/'
response = requests.get(url)
response.raise_for_status()
soup = BeautifulSoup(response.text, 'lxml')
title_tag = soup.find('main').find('header').find('h1')
img_src = soup.find('img', class_='attachment-post-image')['src'] # поиск через классы
post_body = soup.find('div', class_='entry-content') # поиск через классы

print(title_tag.text + '\n' + img_src + '\n' + post_body.text)