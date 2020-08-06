import os
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
import json
import argparse

def parsing_text(soup):
    header = soup.select_one("#content")
    title_tag = header.h1
    parse_book = (title_tag).text.split(' \xa0 :: \xa0 ')
    author,title = parse_book
    return sanitize_filename(author) + ' -- ' +  sanitize_filename(title)

def parsing_comments(soup):
    title_tag = soup.select("div.texts span.black")
    comments = []
    for comment in title_tag:
        comments.append(comment.text)
    return comments

def parsing_genres(soup):
    genres_p = soup.select('span.d_book a')
    genres = []
    for genre in genres_p:
        genres.append(genre.text)
    return genres

def parsing_image(soup):
    img_src = soup.select_one('div.bookimage img')['src']
    return urljoin('http://tululu.org', img_src)

def download_img(url_img):
    response = requests.get(url_img, allow_redirects=False)
    filename = f"{url_img.split('/')[-1]}"
    folder = os.path.join(dest_folder,'images', filename)
    with open(folder, "wb") as file:
        return file.write(response.content)

def download_book(url_book,id):    
    id_download = url_book[url_book.find('/b')+2:-1]
    url_download = f'http://tululu.org/txt.php?id={id_download}'
    response = requests.get(url_download, allow_redirects=False)
    filename = f"{id+1}-я книга. {parsing_text(soup)}.txt"
    folder = os.path.join(dest_folder,'books', filename)
    with open(folder, "w", encoding='utf-8') as file:
        return file.write(response.text)

def parsing_url(start_page,end_page):
    genre_links = []
    end_page += 1
    if start_page>end_page:
        end_page = start_page + 1
    for id in range(start_page,end_page):
        url_book = f'http://tululu.org/l55/{id}'
        response = requests.get(url_book)
        soup = BeautifulSoup(response.text, 'lxml')
        link_parse = soup.select('table.d_book')
        for link in link_parse:
            link = link.select_one('a')['href']
            genre_links.append(urljoin('http://tululu.org',link))
    return genre_links

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Этот проект позволяет парсить книги из открытого доступа.')
    parser.add_argument('--start_page',default=1, help='Страница с которой начинается парсинг', type=int)
    parser.add_argument('--end_page', default=1, help='Страница на которой закончится парсинг', type=int)
    parser.add_argument('--json_path', default='', help='указать свой путь к *.json файлу с результатами ', type=str)
    parser.add_argument('--dest_folder', default='', help='путь к каталогу с результатами парсинга: картинкам, книгам, JSON. ', type=str)
    parser.add_argument('--skip_txt', default=False, help='не скачивать книги, указать "False"  ', type = bool)
    parser.add_argument('--skip_imgs', default=False, help='не скачивать картинки, указать "False"   ', type = bool)
    args = parser.parse_args()
    start_page = args.start_page
    end_page = args.end_page
    skip_imgs = args.skip_imgs
    skip_txt = args.skip_txt
    json_path = args.json_path
    dest_folder = args.dest_folder

    Path(dest_folder,'images').mkdir(parents=True, exist_ok=True)
    Path(dest_folder,'books').mkdir(parents=True, exist_ok=True)
    urls = parsing_url(start_page,end_page)
    books_info = []
    for id in range(len(urls)):
        url_book = urls[id]
        print(url_book)
        response = requests.get(url_book)
        soup = BeautifulSoup(response.text, 'lxml')

        url_img = parsing_image(soup)
        book_info = parsing_text(soup).split(' -- ')
        comments = parsing_comments(soup)
        genres = parsing_genres(soup)
        url_src = os.path.join(dest_folder,'images',url_img.split('/')[-1])
        book_path = os.path.join(dest_folder,'books',book_info[0] + '.txt')
        book_info = {
            'title':book_info[0],
            "author": book_info[1],
            'img_src':url_src,
            'book_path':book_path,
            'comments':comments,
            "genres": genres
        }
        books_info.append(book_info)

        if not skip_txt:
            download_book(url_book,id)

        if not skip_imgs:
            download_img(url_img)

    json_paath = ''

    if dest_folder:
        json_paatch = dest_folder
    
    if json_path:
        json_paatch = json_path

    json_paatch = os.path.join(json_paatch, "about_books.json")
    with open(json_paatch, "w", encoding='utf-8') as my_file:
        json.dump(books_info,my_file, indent=4 ,ensure_ascii=False)