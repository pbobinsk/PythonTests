def add(a, b):
    return a+b

def sub(a, b):
    return a-b

from rpc import RPCServer

server = RPCServer()

server.registerMethod(add)
server.registerMethod(sub)

class Mathematics:
    @classmethod
    def mul(self,a, b):
        return a*b

    @classmethod
    def div(a, b):
        return a/b

server.registerInstance(Mathematics)

server.help()

server.run()