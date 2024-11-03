def add(a, b):
    return a+b

def sub(a, b):
    return a-b

from rpc import RPCServer

server = RPCServer()

server.registerMethod(add)
server.registerMethod(sub)

class Mathematics:
    #dodano anotacje do metod - inaczej serwer ich nie widział
    #self jest konieczne
    @classmethod
    def mul(self,a, b):
        return a*b

    #dodano anotacje do metod - inacej serwer ich nie widział
    #self jest konieczne
    @classmethod
    def div(self,a, b):
        return a/b

server.registerInstance(Mathematics)

server.help()

server.run()