import os
import requests
from pathlib import Path

PATCH = r"C:\Users\lysak.m\Documents\py\study_prog\Many_projects\Bitly-CMD\books"

Path(PATCH).mkdir(parents=True, exist_ok=True)
for id in range(1,11):
    url = f'http://tululu.org/txt.php?id={id}'
    response = requests.get(url)
    if response.ok:
        filename = f"id{id}.txt"
        with open(f"{PATCH}/{filename}", "w") as file:
            file.write(response.text)