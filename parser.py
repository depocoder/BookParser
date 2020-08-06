import os
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
import json

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

def download_img(PATCH_IMG,url_img):
    response = requests.get(url_img, allow_redirects=False)
    filename = f"{url_img.split('/')[-1]}"
    folder = os.path.join(PATCH_IMG, filename)
    with open(folder, "wb") as file:
        return file.write(response.content)

def download_book(url_book,id):    
    id_download = url_book[url_book.find('/b')+2:-1] #так как для закачки книги ссылка совсем другая нужен id
    url_download = f'http://tululu.org/txt.php?id={id_download}'
    response = requests.get(url_download, allow_redirects=False)
    filename = f"{id+1}-я книга. {parsing_text(soup)}.txt"
    folder = os.path.join(PATCH_BOOKS, filename)
    with open(folder, "w", encoding='utf-8') as file:
        return file.write(response.text)

def parsing_url():
    genre_links = []
    for id in range(1,5):
        url_book = f'http://tululu.org/l55/{id}'
        response = requests.get(url_book)
        soup = BeautifulSoup(response.text, 'lxml')
        link_parse = soup.select('table.d_book')
        for link in link_parse:
            link = link.select_one('a')['href']
            genre_links.append(urljoin('http://tululu.org',link))
    return genre_links

if __name__ == '__main__':
    PATCH_BOOKS = r"C:\Users\lysak.m\Documents\py\study_prog\Many_projects\BookParser\books"
    Path(PATCH_BOOKS).mkdir(parents=True, exist_ok=True)
    PATCH_IMG = r"C:\Users\lysak.m\Documents\py\study_prog\Many_projects\BookParser\images"
    Path(PATCH_IMG).mkdir(parents=True, exist_ok=True)
    urls = parsing_url()
    books_info = []
    for id in range(10):
        url_book = urls[id]
        response = requests.get(url_book)
        soup = BeautifulSoup(response.text, 'lxml')

        url_img = parsing_image(soup)
        book_info = parsing_text(soup).split(' -- ')
        comments = parsing_comments(soup)
        genres = parsing_genres(soup)
        url_src = os.path.join('images',url_img.split('/')[-1])
        book_path = os.path.join('books',book_info[0] + '.txt')
        book_info = {
            'title':book_info[0],
            "author": book_info[1],
            'img_src':url_src,
            'book_path':book_path,
            'comments':comments,
            "genres": genres
        }
        books_info.append(book_info)

        download_img(PATCH_IMG,url_img)
        download_book(url_book,id)

    with open("about_books.json", "w", encoding='utf-8') as my_file:
        json.dump(books_info,my_file, indent=4 ,ensure_ascii=False)

