# BookParser

Этот проект позволяет парсить книги с [**сайта tululu.org**](https://tululu.org/). После чего просматривать их на [**html страничках**](https://depocoder.github.io/BookParser/pages/index1.html).    

![](https://i.imgur.com/NLwEzvz.png)

## Запуск без интернета
Все html страницы находятся в папке pages. Если вы хотите открыть вашу библиотеку без интернета, вам нужно открыть любой файл в браузере из папки pages, дальше можете перемещаться по страницам в самом браузере.
Подробнее о том как открыть html файл - [инструкция с скриншотами и видео](https://urfix.ru/open-html-file/).   

## Подготовка к запуску Mac OS

Уставновить Python 3+

```
sudo apt-get install python3
```

Установить, создать и активировать виртуальное окружение

```
git clone https://github.com/herypank/BookParser
cd BookParser
pip3 install virtualenv
python3 -m venv env
source env/bin/activate
```

Установить библиотеки командой

```
pip3 install -r requirements.txt
```

## Запуск кода

Парсинг данных
```
python3 parser.py --start_page 1 --end_page 2
```
    
Запуск сайта на своем компьютере   

```
python3 render_website.py
```

Переходи по адресу [**http://127.0.0.1:5500/pages/index1.html**](http://127.0.0.1:5500/pages/index1.html)
# Аргументы парсера

1. `start_page` - *обязательный аргумент* - страница с которой начнется парсинг книг.   
2. `end_page` - *обязательный аргумент* - страница с которой начнется парсинг книг.   
3. `dest_folder` — путь к каталогу с результатами парсинга: картинкам, книгам, JSON, путь обязательно указывать в кавычках пример "C:\Program Files".  
4. `skip_imgs` — не скачивать картинки, при этом аргументе about_books.json не создается.
5. `skip_txt` — не скачивать книги, при этом аргументе about_books.json не создается.   
    
**Запуск парсера с аргументами**

```
python3 parser.py --start_page 10 --end_page 23 --dest_folder "C:\Program Files" --skip_imgs
```
