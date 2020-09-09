import os
from time import sleep
import argparse
import json
from urllib.parse import urljoin
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def parse_title_author(soup):
    header = soup.select_one("#content")
    title_tag = header.h1
    author, title = title_tag.text.split(' \xa0 :: \xa0 ')
    return f'{sanitize_filename(author)} -- {sanitize_filename(title)}'


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
    filename = f"{url_img.split('/')[-1]}"
    folder = os.path.join(dest_folder, 'images', filename)
    with open(folder, "wb") as file:
        return file.write(response.content), filename


def get_id_book(book_url):
    id_dowload = book_url[book_url.find('/b')+2:-1]
    return id_dowload


def download_book(dest_folder):
    id_dowload = get_id_book(book_url)
    url_download = f'http://tululu.org/txt.php?id={id_dowload}'
    response = requests.get(url_download)
    response.raise_for_status()
    filename = f"{id_dowload}-я книга. {parse_title_author(soup)}.txt"
    folder = os.path.join(dest_folder, 'books', filename)
    with open(folder, "w", encoding='utf-8') as file:
        return file.write(response.text), filename


def parse_urls(start_page, end_page):
    book_links = []
    end_page += 1
    if start_page > end_page:
        end_page = start_page + 1
    for book_num in range(start_page, end_page):
        while True:
            try:
                book_url = f'http://tululu.org/l55/{book_num}'
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
            except Exception as requestsHTTPError:
                print(f'Ошибка - HTTPError, пропуск номера книги - {book_num}')
                break
            break
    return book_links


def dump_book_details_to_dict(soup, filename_book, filename_img):
    author, title = filename_book.split(' -- ')
    comments = parse_comments(soup)
    genres = parse_genres(soup)
    if filename_book is None:
        book_path = None
    else:
        book_path = os.path.join('images', filename_book)
    if filename_img is None:
        img_src = None
    else:
        img_src = os.path.join('books', filename_img)
    book_info = {
        'title': author,
        "author": title,
        'img_src': img_src,
        'book_path': book_path,
        'comments': comments,
        "genres": genres
    }
    return book_info


def raise_if_redirect(response):
    if response.status_code == 302:
        return requestsHTTPError


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='''Этот проект позволяет парсить книги
        из открытого доступа.''')

    parser.add_argument(
        '--start_page', default=1,
        help='Страница с которой начинается парсинг.', type=int)

    parser.add_argument(
        '--end_page', default=1,
        help='Страница на которой закончится парсинг.', type=int)

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

    Path(args.dest_folder, 'images').mkdir(parents=True, exist_ok=True)
    Path(args.dest_folder, 'books').mkdir(parents=True, exist_ok=True)
    books_info = []
    books_urls = parse_urls(args.start_page, args.end_page)
    for book_url in books_urls:
        while True:
            try:
                response = requests.get(book_url, allow_redirects=False)
                raise_if_redirect(response)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'lxml')
                url_img = parse_image(soup, book_url)
                filename_img = None
                filename_book = None
                if not args.skip_txt:
                    filename_book = download_book(args.dest_folder)[1]

                if not args.skip_imgs:
                    filename_img = download_img(url_img, args.dest_folder)[1]
            except requests.exceptions.ConnectionError:
                print('Ошибка - ConnectionError.',
                      'Проверьте подключение с интернетом.',
                      'Запуск повторно через 30 секунд.')
                sleep(30)
                continue
            except Exception as requestsHTTPError:
                print(f'Ошибка - HTTPError, пропуск книги - {book_url}')
                break
            break
        books_info.append(dump_book_details_to_dict(
            soup, filename_book, filename_img))

    json_path = os.getcwd()
    if args.dest_folder:
        json_path = args.dest_folder

    json_path = os.path.join(json_path, "about_books.json")
    with open(json_path, "w", encoding='utf-8') as my_file:
        json.dump(books_info, my_file, indent=4, ensure_ascii=False)
