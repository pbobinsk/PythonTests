import requests
import json

r = requests.get('https://jsonplaceholder.typicode.com/posts')

print(r)

print (r.status_code)

print (r.headers['content-type'])
print(r.text)
print(r.json())
lista = json.loads(r.text)

print(lista[3])

url = 'https://www.w3schools.com/python/demopage.php'
myobj = {'somekey': 'somevalue'}

x = requests.post(url, json = myobj)

print(x)
