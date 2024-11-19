from jsonrpcclient import request, parse, Ok, Error
import logging
import requests


def call(jsonRequest):
    response = requests.post("http://localhost:5667/", json=jsonRequest)
    match parse(response.json()):
        case Ok(result, id):
            print(result)
        case Error(code, message, data, id):
            logging.error(message)

call(request("ping"))
call(request("hello",params={"name":"Piotr"}))
ans = call(request("doNLP",params={"file":"Piotr"}))
print(ans)
