# BookParser

## Описание проекта.

Этот проект позволяет парсить книги с [**сайта**](https://tululu.org/) . После чего просматривать их на [**html страничках**](https://herypank.github.io/BookParser/pages/index1.html).


## Подготовка к запуску MAC OS.

*Уставновить Python 3+.*

```
sudo apt-get install python3
```

*Установить, создать и активировать виртуальное окружение.*

```
pip3 install virtualenv
python3 -m venv env
source env/bin/activate
```

*Установить библиотеки командой.*

```
pip3 install -r requirements.txt
```

## Запуск кода.

*Парсинг данных*
```
python3 parser.py --start_page 1 --end_page 2
```
    
*Запуск сайта на своем компьютере*   

```
python3 render_website.py
```

# Аргументы

1. `start_page` - *обязательный аргумент* - страница с которой начнется парсинг книг.   
2. `end_page` - *обязательный аргумент* - страница с которой начнется парсинг книг.   
3. `dest_folder` — путь к каталогу с результатами парсинга: картинкам, книгам, JSON, путь обязательно указывать в кавычках пример "C:\Program Files".  
4. `skip_imgs` — не скачивать картинки, при этом аргументе about_books.json не создается.
5. `skip_txt` — не скачивать книги, при этом аргументе about_books.json не создается.   
    
**Запуск кода с аргументами**

```
python3 parser.py --start_page 10 --end_page 23 --dest_folder "C:\Program Files" --skip_imgs
```
