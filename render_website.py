import json
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server, shell
from more_itertools import chunked


def get_books():
    with open("about_books.json", "r", encoding='utf-8') as my_file:
        about_books = my_file.read()
    return json.loads(about_books)


def main():
    Path(os.getcwd(), 'pages').mkdir(parents=True, exist_ok=True)
    about_books = get_books()
    chunked_about_books = list(chunked(about_books, 10))
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')
    count_pages = len(chunked_about_books)
    for page, books in enumerate(chunked_about_books, 1):
        rendered_page = template.render(
            books=books,
            count_pages=count_pages,
            current_page=page,
        )

        with open(f'pages/index{page}.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)
    server = Server()
    server.watch('*.html', shell('make html'))
    server.serve(root='')


if __name__ == "__main__":
    main()
