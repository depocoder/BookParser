import os
import argparse
import json
from urllib.parse import urljoin
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def parse_text(soup):
    header = soup.select_one("#content")
    title_tag = header.h1
    parse_book = (title_tag).text.split(' \xa0 :: \xa0 ')
    author, title = parse_book
    return sanitize_filename(author) + ' -- ' + sanitize_filename(title)


def parse_comments(soup):
    title_tag = soup.select("div.texts span.black")
    comments = []
    for comment in title_tag:
        comments.append(comment.text)
    return comments


def parse_genres(soup):
    genres_p = soup.select('span.d_book a')
    genres = []
    for genre in genres_p:
        genres.append(genre.text)
    return genres


def parse_image(soup):
    img_src = soup.select_one('div.bookimage img')['src']
    return urljoin('http://tululu.org', img_src)


def download_img(url_img, dest_folder):
    response = requests.get(url_img, allow_redirects=False)
    filename = f"{url_img.split('/')[-1]}"
    folder = os.path.join(dest_folder, 'images', filename)
    with open(folder, "wb") as file:
        return file.write(response.content)


def download_book(book_url, book_num, dest_folder):
    link_download = book_url[book_url.find('/b')+2:-1]
    url_download = f'http://tululu.org/txt.php?id={link_download}'
    response = requests.get(url_download, allow_redirects=False)
    filename = f"{book_num+1}-я книга. {parse_text(soup)}.txt"
    folder = os.path.join(dest_folder, 'books', filename)
    with open(folder, "w", encoding='utf-8') as file:
        return file.write(response.text)


def parse_urls(start_page, end_page):
    genre_links = []
    end_page += 1
    if start_page > end_page:
        end_page = start_page + 1
    for book_num in range(start_page, end_page):
        book_url = f'http://tululu.org/l55/{book_num}'
        response = requests.get(book_url)
        soup = BeautifulSoup(response.text, 'lxml')
        link_parse = soup.select('table.d_book')
        for link in link_parse:
            link = link.select_one('a')['href']
            genre_links.append(urljoin('http://tululu.org', link))
    return genre_links



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
        '--json_path', default='',
        help='указать свой путь к *.json файлу с результатами.', type=str)

    parser.add_argument(
        '--dest_folder', default=os.getcwd(),
        help='''путь к каталогу с результатами парсинга:
        картинкам, книгам, JSON. ''',
        type=str)

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
    for book_num,book_url in enumerate(books_urls):
        print(book_url)
        response = requests.get(book_url)
        soup = BeautifulSoup(response.text, 'lxml')

        url_img = parse_image(soup)
        book_info = parse_text(soup).split(' -- ')
        comments = parse_comments(soup)
        genres = parse_genres(soup)
        url_src = os.path.join(args.dest_folder,
                               'images', url_img.split('/')[-1])
        book_path = os.path.join(args.dest_folder,
                                 'books', book_info[0] + '.txt')
        book_info = {
            'title': book_info[0],
            "author": book_info[1],
            'img_src': url_src,
            'book_path': book_path,
            'comments': comments,
            "genres": genres
        }
        books_info.append(book_info)

        if not args.skip_txt:
            download_book(book_url, book_num, args.dest_folder)

        if not args.skip_imgs:
            download_img(url_img, args.dest_folder)

    json_path = os.getcwd()

    if args.dest_folder:
        json_path = args.dest_folder

    if args.json_path:
        json_path = args.json_path

    json_path = os.path.join(json_path, "about_books.json")
    with open(json_path, "w", encoding='utf-8') as my_file:
        json.dump(books_info, my_file, indent=4, ensure_ascii=False)
