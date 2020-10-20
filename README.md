# BookParser

## Описание проекта.

Этот проект позволяет парсить книги из открытого доступа. Все книги парсятся в папку **books**.

## Подготовка к запуску.

Уставновить Python 3+.

```
sudo apt-get install python3
```

Установить, создать и активировать виртуальное окружение.

```
pip3 install virtualenv
python3 -m venv env
source env/bin/activate
```

Установить библиотеки командой.

```
pip3 install -r requirements.txt
```

## Запуск кода.

```
python3 parser.py --start_page 1 --end_page 2
```

# Аргументы

`start_page` - *ОБЯЗАТЕЛЬНЫЙ АРГУМЕНТ* - страница с которой начнется парсинг книг.   
`end_page` - *ОБЯЗАТЕЛЬНЫЙ АРГУМЕНТ* - страница с которой начнется парсинг книг.   
`dest_folder` — путь к каталогу с результатами парсинга: картинкам, книгам, JSON, путь обязательно указывать в кавычках пример "C:\Program Files".  
`skip_imgs` — не скачивать картинки, при этом аргументе about_books.json не создается.
`skip_txt` — не скачивать книги, при этом аргументе about_books.json не создается.  
**Запуск кода с аргументами**

```
python3 parser.py --dest_folder "C:\Program Files" --skip_imgs
```
