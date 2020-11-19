import json
import os
from pathlib import Path
from functools import partial
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def get_books():
    with open("about_books.json", "r", encoding='utf-8') as my_file:
        about_books = my_file.read()
    return json.loads(about_books)


def delete_extra_files(created_pages_paths):
    actual_pages_paths = (set((Path('.').glob('./pages/*.html'))))
    extra_files_paths = actual_pages_paths - created_pages_paths
    for exta_file_path in extra_files_paths:
        full_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), exta_file_path)
        os.remove(full_path)


def rebuild_html(chunked_about_books):
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    pages_count = len(chunked_about_books)
    template = env.get_template('template.html')
    created_pages_paths = set()
    for page, books in enumerate(chunked_about_books, 1):
        rendered_page = template.render(
            books=books,
            pages_count=pages_count,
            current_page=page,
        )
        created_pages_paths.add(Path(f"pages/index{page}.html"))
        with open(f'pages/index{page}.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)
    delete_extra_files(created_pages_paths)


def main():
    Path(os.getcwd(), 'pages').mkdir(parents=True, exist_ok=True)
    about_books = get_books()
    chunked_about_books = list(chunked(about_books, 10))
    rebuild_html_with_argument = partial(
        rebuild_html, chunked_about_books=chunked_about_books)
    rebuild_html_with_argument()
    server = Server()
    server.watch('template.html', rebuild_html_with_argument)
    server.serve(root='')


if __name__ == "__main__":
    main()
