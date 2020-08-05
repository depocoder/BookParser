import os
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
import json

def parsing_text(id,url_book):
    """Функция для парсинга названия книг с сайта http://tululu.org.

    Args:
        url_book (str): Cсылка на книгу которую парсим.
        parse_book (list): (0)Название книги, (1)Автор.

    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    response = requests.get(url_book)
    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find('h1')
    parse_book = title_tag.text.strip()
    parse_book = parse_book.split(' \xa0 :: \xa0 ')

    return sanitize_filename(parse_book[0]) + ' -- ' +  sanitize_filename(parse_book[1])

def parsing_comments(id,url_book):
    """Функция для парсинга комментариев книг с сайта http://tululu.org.

    Args:
        url_book (str): Cсылка на книгу которую парсим.
        parse_book (list): (0)Название книги, (1)Автор.

    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    response = requests.get(url_book)
    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find_all('div',class_='texts')
    comments = []
    if title_tag:
        for comment in title_tag:
            comments.append(comment.find('span').text)
    return comments

def parsing_genres(id,url_book):
    """Функция для парсинга комментариев книг с сайта http://tululu.org.

    Args:
        url_book (str): Cсылка на книгу которую парсим.
        parse_book (list): (0)Название книги, (1)Автор.

    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    response = requests.get(url_book)
    soup = BeautifulSoup(response.text, 'lxml')
    genres_p = soup.find('span', class_ = 'd_book').find_all('a')
    genres = []
    for genre in genres_p:
        genres.append(genre.text)
    return genres

def parsing_url():
    """Функция для парсинга ссылок на фантастику с сайта http://tululu.org.

    Args:
        url_book (str): Cсылка на книгу которую парсим.
        parse_book (list): (0)Название книги, (1)Автор.

    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    genre_links = []
    for id in range(1,5):
        url_book = f'http://tululu.org/l55/{id}'
        response = requests.get(url_book)
        soup = BeautifulSoup(response.text, 'lxml')
        link_parse = soup.find_all('table', class_= 'd_book')
        for link in link_parse:
            link = link.find('a')['href']
            genre_links.append(urljoin('http://tululu.org',link))
    return genre_links

def parsing_image(id,url_book):
    """Функция для парсинга картинок книг с сайта http://tululu.org.

    Args:
        url_book (str): Cсылка на книгу которую парсим.
        parse_book (list): (0)Название книги, (1)Автор.

    Returns:
        str: Путь до файла, куда сохранён текст.
    """
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
    urls = parsing_url()
    for id in range(100):
        url_download = f'http://tululu.org/txt.php?id={id}'
        print(len(parsing_url()),len(urls))
        url_book = urls[id]
        response = requests.get(url_download, allow_redirects=False)
        if not response.status_code == 302:
            url_img = parsing_image(id,url_book)
            download_img(PATCH_IMG,url_img)
            filename = f"{id}. {parsing_text(id,url_book)}.txt"
            folder = os.path.join(PATCH_BOOKS, filename)
            with open(folder, "w", encoding='utf-8') as file:
                file.write(response.text)