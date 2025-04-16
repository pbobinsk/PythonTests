import grpc
import sys

import helloworld_pb2
import helloworld_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = helloworld_pb2_grpc.GreeterStub(channel)
        name = "świat"
        if len(sys.argv) > 1:
            name = sys.argv[1]
        request = helloworld_pb2.HelloRequest(name=name)
        response = stub.SayHello(request)
    print("Powitanie otrzymane od serwera:", response.message)

if __name__ == '__main__':
    run()