import os
import sys
import argparse
import json
from pathlib import Path
from urllib.parse import urljoin, urlparse, quote
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
    response = requests.get(url_img, allow_redirects=False, verify=False)
    response.raise_for_status()
    raise_if_redirect(response)
    disassembled_url = urlparse(url_img)
    filename, file_ext = os.path.splitext(
        os.path.basename(disassembled_url.path))
    rel_img_path = os.path.join('images', filename + file_ext)
    image_path = os.path.join(dest_folder, rel_img_path)
    with open(image_path, "wb") as file:
        file.write(response.content)
    return rel_img_path


def request_book_download(download_id):
    response = requests.get("https://tululu.org/txt.php", params={
        "id": download_id, }, verify=False)
    response.raise_for_status()
    raise_if_redirect(response)
    return response.text


def download_book(dest_folder, book_url, book_title):
    download_id = book_url[book_url.find('/b')+2:-1]
    html = request_book_download(download_id)
    filename = f"{download_id}-я книга. {book_title}.txt"
    rel_book_path = os.path.join('books', filename)
    book_path = os.path.join(dest_folder, rel_book_path)
    with open(book_path, "w", encoding='utf-8') as file:
        file.write(html)
    return rel_book_path


def request_book_page_html(page, book_url):
    response = requests.get(book_url, allow_redirects=False, verify=False)
    raise_if_redirect(response)
    response.raise_for_status()
    return response.text


def parse_book_urls(html, book_catalog_link):
    book_urls = []
    soup = BeautifulSoup(html, 'lxml')
    blocks_html = soup.select('table.d_book')
    for block_html in blocks_html:
        url = block_html.select_one('a')['href']
        book_urls.append(urljoin(book_catalog_link, url))
    return book_urls


def parse_urls(start_page, end_page):
    book_urls = []
    for page in range(start_page, end_page + 1):
        while True:
            try:
                book_catalog_link = f'https://tululu.org/l55/{page}'
                html = request_book_page_html(page, book_catalog_link)
                book_urls += parse_book_urls(html, book_catalog_link)
                break
            except requests.exceptions.ConnectionError:
                print('Ошибка - ConnectionError.',
                      'Проверьте подключение с интернетом.',
                      ' Запуск повторно через 30 секунд.')
                sleep(30)
            except requests.HTTPError:
                print('Страница не найдена, был пойман редирект. Пропуск -',
                      page)
                break
    return book_urls


def dump_book_details_to_dict(
        soup, book_title, book_author, rel_book_path,
        rel_img_path, skip_imgs, skip_txt):
    comments = parse_comments(soup)
    genres = parse_genres(soup)

    book_info = {
        'title': book_title,
        "author": book_author,
        'img_src': quote(rel_img_path, safe=''),
        'book_path': quote(rel_book_path, safe=''),
        'comments': comments,
        "genres": genres
    }
    return book_info


def raise_if_redirect(response):
    if response.status_code == 302:
        raise requests.HTTPError


def get_book_soup(book_url):
    response = requests.get(book_url, allow_redirects=False, verify=False)
    raise_if_redirect(response)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'lxml')


def create_argparse():
    parser = argparse.ArgumentParser(
        description='''Этот проект позволяет парсить книги
        из открытого доступа.''')

    parser.add_argument(
        '--start_page',
        help='Страница с которой начинается парсинг.', required=True, type=int)

    parser.add_argument(
        '--end_page',
        help='Страница на которой закончится парсинг.',
        required=True, type=int)

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

    if not (args.start_page < args.end_page and args.start_page > 0
            and args.end_page > 0):
        sys.exit(
            'Не верный ввод start_page или end_page, ' +
            'пример правильного ввода:' +
            '\n' + 'python3 parser.py --start_page 3 --end_page 10')

    return parser


def main():
    parser = create_argparse()
    args = parser.parse_args()

    Path(args.dest_folder, 'images').mkdir(parents=True, exist_ok=True)
    Path(args.dest_folder, 'books').mkdir(parents=True, exist_ok=True)
    books = []
    books_urls = parse_urls(args.start_page, args.end_page)
    for book_url in books_urls:
        while True:
            try:
                soup = get_book_soup(book_url)
                book_title, book_author = parse_title_author(soup)
                rel_book_path = None
                if not args.skip_txt:
                    rel_book_path = download_book(
                        args.dest_folder, book_url, book_title)

                rel_img_path = None
                if not args.skip_imgs:
                    url_img = parse_image(soup, book_url)
                    rel_img_path = download_img(
                        url_img, args.dest_folder)

                books.append(dump_book_details_to_dict(
                    soup, book_title, book_author, rel_book_path,
                    rel_img_path,
                    args.skip_imgs, args.skip_txt))
                break
            except requests.exceptions.ConnectionError:
                print('Ошибка - ConnectionError.',
                      'Проверьте подключение с интернетом.',
                      'Запуск повторно через 30 секунд.')
                sleep(30)
            except requests.HTTPError:
                print('Страница не найдена, был пойман редирект. Пропуск -',
                      book_url)
                break

    json_path = os.path.join(args.dest_folder, "about_books.json")
    with open(json_path, "w", encoding='utf-8') as my_file:
        json.dump(books, my_file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()
