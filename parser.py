import os
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin


def parsing_text(id):
    """Функция для парсинга названия книг с сайта http://tululu.org.

    Args:
        url_book (str): Cсылка на книгу которую парсим.
        parse_book (list): (0)Название книги, (1)Автор.

    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    url_book = f'http://tululu.org/b{id}/'
    response = requests.get(url_book)
    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find('h1')
    parse_book = (title_tag.text.strip())
    parse_book = parse_book.split(' \xa0 :: \xa0 ')

    return parse_book[0] + ' -- ' +  parse_book[1]

def parsing_comments(id):
    """Функция для парсинга комментариев книг с сайта http://tululu.org.

    Args:
        url_book (str): Cсылка на книгу которую парсим.
        parse_book (list): (0)Название книги, (1)Автор.

    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    url_book = f'http://tululu.org/b{id}/'
    response = requests.get(url_book)
    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find_all('span',class_='red')
    print(title_tag)
    #parse_book = (title_tag.text)

    return title_tag

def parsing_image(id):
    """Функция для парсинга картинок книг с сайта http://tululu.org.

    Args:
        url_book (str): Cсылка на книгу которую парсим.
        parse_book (list): (0)Название книги, (1)Автор.

    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    url_book = f'http://tululu.org/b{id}/'
    response = requests.get(url_book)
    soup = BeautifulSoup(response.text, 'lxml')
    img_src = soup.find('div', class_ = 'bookimage').find('img')['src']
    return urljoin('http://tululu.org', img_src)

def download_img(PATCH_IMG,url_img):

    response = requests.get(url_img, allow_redirects=False)
    filename = f"{url_img.split('/')[-1]}"
    folder = os.path.join(PATCH_IMG, filename)
    with open(folder, "wb") as file:
        return file.write(response.content)

if __name__ == '__main__':
    PATCH_BOOKS = r"C:\Users\lysak.m\Documents\py\study_prog\Many_projects\BookParser\books"
    Path(PATCH_BOOKS).mkdir(parents=True, exist_ok=True)
    PATCH_IMG = r"C:\Users\lysak.m\Documents\py\study_prog\Many_projects\BookParser\images"
    Path(PATCH_IMG).mkdir(parents=True, exist_ok=True)
    for id in range(5,7):
        url_download = f'http://tululu.org/txt.php?id={id}'
        
        response = requests.get(url_download, allow_redirects=False)
        if not response.status_code == 302:
            parsing_comments(id)
            url_img = parsing_image(id)
            download_img(PATCH_IMG,url_img)
            filename = f"{id}. {parsing_text(id)}.txt"
            folder = os.path.join(PATCH_BOOKS, filename)
            with open(folder, "w") as file:
                file.write(response.text)