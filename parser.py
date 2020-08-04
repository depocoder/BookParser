import os
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def parsing_page():
    url_book = f'http://tululu.org/b{id}/'
    response_book = requests.get(url_book, allow_redirects=False)
    soup = BeautifulSoup(response_book.text, 'lxml')
    title_tag = soup.find('h1')
    parse_book = (title_tag.text.strip())
    parse_book = parse_book.split(' \xa0 :: \xa0 ')
    title_book = sanitize_filename(parse_book[0])
    author = sanitize_filename(parse_book[1])

    return title_book + ' -- ' +  author


if __name__ == '__main__':
    PATCH = r"C:\Users\lysak.m\Documents\py\study_prog\Many_projects\BookParser\books"
    Path(PATCH).mkdir(parents=True, exist_ok=True)

    for id in range(1,11):
        url_download = f'http://tululu.org/txt.php?id={id}'
        response_download = requests.get(url_download, allow_redirects=False)
        if not response_download.status_code == 302:
            filename = f"{id}. {parsing_page()}.txt"
            folder = os.path.join(PATCH, filename)
            with open(folder, "w") as file:
                file.write(response_download.text)