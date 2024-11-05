import requests

url = 'http://localhost:5000'
myobj = {"jsonrpc": "2.0", "method": "ping","id":1}

x = requests.post(url, json = myobj)

print(x.text)

myobj = {"jsonrpc": "2.0", "method": "hello", "params": ['joł'],"id":1}

x = requests.post(url, json = myobj)

print(x.text)

from jsonrpcclient import request, parse, Ok, Error
import logging
import requests

response = requests.post("http://localhost:5000/", json=request("ping"))

parsed = parse(response.json())
if isinstance(parsed, Ok):
    print(parsed.result)
else:
    logging.error(parsed.message)

response = requests.post("http://localhost:5000/", json=request("hello",params={"name":"Piotr"}))
print(response.json())
match parse(response.json()):
    case Ok(result, id):
        print(result)
    case Error(code, message, data, id):
        logging.error(message)

response = requests.post("http://localhost:5000/", json=request("hello",params={"name":"dupa"}))
print(response.json())
match parse(response.json()):
    case Ok(result, id):
        print(result)
    case Error(code, message, data, id):
        logging.error(message)