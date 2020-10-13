import os
import sys
import argparse
import json
from pathlib import Path
from urllib.parse import urljoin, urlparse
from time import sleep

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def parse_title_author(soup):
    header = soup.select_one("#content")
    title_tag = header.h1
    author, title = title_tag.text.split(' \xa0 :: \xa0 ')
    return sanitize_filename(author), sanitize_filename(title)


def parse_comments(soup):
    title_tag = soup.select("div.texts span.black")
    comments = [comment.text for comment in title_tag]
    return comments


def parse_genres(soup):
    genres_soup = soup.select('span.d_book a')
    genres = [genres.text for genres in genres_soup]
    return genres


def parse_image(soup, book_url):
    img_src = soup.select_one('div.bookimage img')['src']
    return urljoin(book_url, img_src)


def download_img(url_img, dest_folder):
    response = requests.get(url_img, allow_redirects=False)
    response.raise_for_status()
    disassembled_url = urlparse(url_img)
    filename, file_ext = os.path.splitext(os.path.basename(disassembled_url.path))
    image_path = os.path.join(dest_folder, 'images', filename + file_ext)
    with open(image_path, "wb") as file:
        file.write(response.content)
    return filename, file_ext


def get_id_book(book_url):
    id_download = book_url[book_url.find('/b')+2:-1]
    return id_download


def download_book(dest_folder, id_download):
    response = requests.get("https://tululu.org/txt.php", params={
        "id": id_download,})
    response.raise_for_status()
    filename = f"{id_download}-я книга. {book_title}.txt"
    book_path = os.path.join(dest_folder, 'books', filename)
    with open(book_path, "w", encoding='utf-8') as file:
        file.write(response.text)


def parse_urls(start_page, end_page):
    book_links = []
    for page_book in range(start_page, end_page + 1):
        while True:
            try:
                book_url = f'https://tululu.org/l55/{page_book}'
                response = requests.get(book_url, allow_redirects=False)
                raise_if_redirect(response)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'lxml')
                link_parse = soup.select('table.d_book')
                for link in link_parse:
                    link = link.select_one('a')['href']
                    book_links.append(urljoin(book_url, link))
            except requests.exceptions.ConnectionError:
                print('Ошибка - ConnectionError.',
                      'Проверьте подключение с интернетом.',
                      ' Запуск повторно через 30 секунд.')
                sleep(30)
                continue
            except requests.HTTPError:
                print(f'Ошибка - HTTPError, пропуск номера страницы - {page_book}')
                break
            break
    return book_links


def dump_book_details_to_dict(
    soup, book_title, author_book, img_filename, id_download):
    comments = parse_comments(soup)
    genres = parse_genres(soup)
    book_path = os.path.join('books', (f'{id_download}-я книга. {book_title}.txt'))
    img_src = os.path.join('images', img_filename + img_ext)
    book_info = {
        'title': book_title,
        "author": author_book,
        'img_src': img_src,
        'book_path': book_path,
        'comments': comments,
        "genres": genres
    }
    return book_info


def raise_if_redirect(response):
    if response.status_code == 302:
        raise requests.HTTPError


def get_book_soup(book_url):
    response = requests.get(book_url, allow_redirects=False)
    raise_if_redirect(response)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'lxml')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='''Этот проект позволяет парсить книги
        из открытого доступа.''')

    parser.add_argument(
        '--start_page',
        help='Страница с которой начинается парсинг.', required=True, type=int)

    parser.add_argument(
        '--end_page',
        help='Страница на которой закончится парсинг.', required=True, type=int)

    parser.add_argument(
        '--dest_folder', default=os.getcwd(),
        help='''путь к каталогу с результатами парсинга: картинкам,
        книгам, JSON, путь обязательно указывать в кавычках
        пример 'C:/Frogram Files' ''', type=str)

    parser.add_argument(
        '--skip_txt', action="store_true",
        help='не скачивать книги.')

    parser.add_argument(
        '--skip_imgs', action="store_true",
        help='не скачивать картинки.')

    args = parser.parse_args()
    end_page = args.end_page
    start_page = args.start_page
    if not (start_page < end_page and start_page > 0 and end_page > 0):
        sys.exit(
            'Не верный ввод start_page или end_page, '+
            'пример правильного ввода:'+
            '\n' + 'python3 parser.py --start_page 3 --end_page 10')

    Path(args.dest_folder, 'images').mkdir(parents=True, exist_ok=True)
    Path(args.dest_folder, 'books').mkdir(parents=True, exist_ok=True)
    books_info = []
    books_urls = parse_urls(start_page, end_page)
    for book_url in books_urls:
        while True:
            try:
                soup = get_book_soup(book_url)
                if not args.skip_txt:
                    book_title, author_book  = parse_title_author(soup)
                    id_download = get_id_book(book_url)
                    download_book(args.dest_folder, id_download)

                if not args.skip_imgs:
                    url_img = parse_image(soup, book_url)
                    img_filename, img_ext = download_img(url_img, args.dest_folder)
            except requests.exceptions.ConnectionError:
                print('Ошибка - ConnectionError.',
                      'Проверьте подключение с интернетом.',
                      'Запуск повторно через 30 секунд.')
                sleep(30)
                continue
            except requests.HTTPError:
                print(f'Ошибка - HTTPError, пропуск книги - {book_url}')
                break
            if not args.skip_txt and not args.skip_imgs:
                books_info.append(dump_book_details_to_dict(
                    soup, book_title, author_book, img_filename, id_download))
            break

    json_path = os.getcwd()
    if args.dest_folder:
        json_path = args.dest_folder
    if not args.skip_txt and not args.skip_imgs:
        json_path = os.path.join(json_path, "about_books.json")
        with open(json_path, "w", encoding='utf-8') as my_file:
            json.dump(books_info, my_file, indent=4, ensure_ascii=False)
