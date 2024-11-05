from jsonrpcclient import request, parse, Ok, Error
import logging
import requests

response = requests.post("http://localhost:5666/", json=request("ping"))
match parse(response.json()):
    case Ok(result, id):
        print(result)
    case Error(code, message, data, id):
        logging.error(message)

response = requests.post("http://localhost:5666/", json=request("hello",params={"name":"Piotr"}))
print(response.json())
match parse(response.json()):
    case Ok(result, id):
        print(result)
    case Error(code, message, data, id):
        logging.error(message)

response = requests.post("http://localhost:5666/", json=request("hello",params={"name":"dupa"}))
print(response.json())
match parse(response.json()):
    case Ok(result, id):
        print(result)
    case Error(code, message, data, id):
        logging.error(message)