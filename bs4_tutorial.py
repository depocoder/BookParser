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

"""PATCH = r"C:\Users\lysak.m\Documents\py\study_prog\Many_projects\Bitly-CMD\books"

Path(PATCH).mkdir(parents=True, exist_ok=True)
for id in range(1,11):
    url = f'http://tululu.org/txt.php?id={id}'
    response = requests.get(url)
    if response.ok:
        filename = f"id{id}.txt"
        with open(f"{PATCH}/{filename}", "w") as file:
            file.write(response.text)"""