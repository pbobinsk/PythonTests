from jsonrpcserver import Success, method, serve, Result, Error
import logging

@method
def ping():
    return Success("pong")

@method
def hello(name: str) -> Result:
    if (name=='dupa'):
        logging.error('Bład')
        return Error(-1,'Bardzo brzydko')
    return Success({'ans':"Hello " + name})

if __name__ == "__main__":
    try:
        serve()
    except KeyboardInterrupt:
        print('Server termnated')