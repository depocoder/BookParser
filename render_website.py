from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
from livereload import Server, shell
from more_itertools import chunked


with open("about_books.json", "r") as my_file:
    about_books = my_file.read()
about_books = json.loads(about_books)
chunked_about_books = list(chunked(about_books, 2))

env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)

template = env.get_template('template.html')

rendered_page = template.render(
    chunked_about_books=chunked_about_books
)

with open('index.html', 'w', encoding="utf8") as file:
    file.write(rendered_page)


server = Server()
server.watch('*.html', shell('make html'))
server.serve(root='')
