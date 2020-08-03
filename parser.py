import requests

url = 'http://tululu.org/txt.php?id=32168'
response = requests.get(url)

filename = "id1.txt"
with open(filename, "w") as file:
    file.write(response.text )