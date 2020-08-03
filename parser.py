import requests


for id in range(1,11):
    url = f'http://tululu.org/txt.php?id={id}'
    response = requests.get(url)
    if response.ok:
        filename = f"id{id}.txt"
        with open(filename, "w") as file:
            file.write(response.text )
"""url = "http://bit.ly/18SuUzJ"
r = requests.get(url, allow_redirects=False)
r.status_code
r.headers['Location']"""