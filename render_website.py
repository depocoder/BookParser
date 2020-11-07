from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
from livereload import Server, shell


with open("about_books.json", "r") as my_file:
    about_books = my_file.read()
about_books = json.loads(about_books)

env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)

template = env.get_template('template.html')

rendered_page = template.render(
    about_books=about_books
)

with open('index.html', 'w', encoding="utf8") as file:
    file.write(rendered_page)


server = Server()
server.watch('*.html', shell('make html'))
server.serve(root='')
