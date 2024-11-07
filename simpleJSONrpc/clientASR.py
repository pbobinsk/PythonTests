from jsonrpcclient import request, parse, Ok, Error
import logging
import requests

def call(jsonRequest):
    response = requests.post("http://localhost:5666/", json=jsonRequest)
    match parse(response.json()):
        case Ok(result, id):
            print(result)
        case Error(code, message, data, id):
            logging.error(message)

call(request("ping"))
call(request("hello",params={"name":"Piotr"}))
call(request("uploadFile",params={"path":r"C:\Users\DELL\venvTests\source\test1.wav"}))
call(request("uploadFile",params={"path":r"C:\Users\DELL\venvTests\source\test1_doctor.wav"}))
call(request("doASR",params={"file":"test1.wav","file_doctor":"test1_doctor.wav"}))

