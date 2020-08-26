import os
import argparse
import json
from urllib.parse import urljoin
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_redirect(response):
    if response.status_code == 200:
        return True
    return False


def parse_title_author(soup):
    header = soup.select_one("#content")
    title_tag = header.h1
    parsing_book = title_tag.text.split(' \xa0 :: \xa0 ')
    author, title = parsing_book
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
        return file.write(response.content)


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
        return file.write(response.text)


def parse_urls(start_page, end_page):
    book_links = []
    end_page += 1
    if start_page > end_page:
        end_page = start_page + 1
    for book_num in range(start_page, end_page):
        book_url = f'http://tululu.org/l55/{book_num}'
        response = requests.get(book_url, allow_redirects=False)
        print((response.status_code), book_url)
        if check_redirect(response):
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            link_parse = soup.select('table.d_book')
            for link in link_parse:
                link = link.select_one('a')['href']
                book_links.append(urljoin(book_url, link))
    return book_links


def parse_info(soup):
    id_book = get_id_book(book_url)
    author, title = parse_title_author(soup).split(' -- ')
    comments = parse_comments(soup)
    genres = parse_genres(soup)
    img_src = os.path.join('images', url_img.split('/')[-1])
    book_path = os.path.join(
        'books', f"{id_book}-я книга. {parse_title_author(soup)}.txt")
    book_info = {
        'title': author,
        "author": title,
        'img_src': img_src,
        'book_path': book_path,
        'comments': comments,
        "genres": genres
    }
    return book_info


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
    books_urls = parse_urls(args.start_page, args.end_page)
    books_info = []
    for book_url in books_urls:
        response = requests.get(book_url, allow_redirects=False)
        response.raise_for_status()
        if check_redirect(response):
            soup = BeautifulSoup(response.text, 'lxml')
            url_img = parse_image(soup, book_url)

            books_info.append(parse_info(soup))

            if not args.skip_txt:
                download_book(args.dest_folder)

            if not args.skip_imgs:
                download_img(url_img, args.dest_folder)

    json_path = os.getcwd()

    if args.dest_folder:
        json_path = args.dest_folder

    json_path = os.path.join(json_path, "about_books.json")
    with open(json_path, "w", encoding='utf-8') as my_file:
        json.dump(books_info, my_file, indent=4, ensure_ascii=False)
