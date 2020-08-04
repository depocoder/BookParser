import os
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def parsing_text(id):
    """Функция для парсинга названия книг с сайта http://tululu.org.

    Args:
        url_book (str): Cсылка на книгу которую парсим.
        parse_book (list): (0)Название книги, (1)Автор.

    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    url_book = f'http://tululu.org/b{id}/'
    response_book = requests.get(url_book)
    soup = BeautifulSoup(response_book.text, 'lxml')
    title_tag = soup.find('h1')
    parse_book = (title_tag.text.strip())
    parse_book = parse_book.split(' \xa0 :: \xa0 ')

    return parse_book[0] + ' -- ' +  parse_book[1]

def parse_image(id):
    """Функция для парсинга картинок книг с сайта http://tululu.org.

    Args:
        url_book (str): Cсылка на книгу которую парсим.
        parse_book (list): (0)Название книги, (1)Автор.

    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    url_book = f'http://tululu.org/b{id}/'
    response_book = requests.get(url_book)
    soup = BeautifulSoup(response_book.text, 'lxml')
    img_src = soup.find('div', class_ = 'bookimage').find('img')['src']
    return 'http://tululu.org'+ img_src

if __name__ == '__main__':
    PATCH = r"C:\Users\lysak.m\Documents\py\study_prog\Many_projects\BookParser\books"
    Path(PATCH).mkdir(parents=True, exist_ok=True)

    for id in range(1,11):
        url_download = f'http://tululu.org/txt.php?id={id}'
        
        response_download = requests.get(url_download, allow_redirects=False)
        if not response_download.status_code == 302:
            print(parse_image(id))
            filename = f"{id}. {parsing_text(id)}.txt"
            folder = os.path.join(PATCH, filename)
            with open(folder, "w") as file:
                file.write(response_download.text)