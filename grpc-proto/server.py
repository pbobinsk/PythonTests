import grpc
from concurrent import futures
import time
import logging

import helloworld_pb2
import helloworld_pb2_grpc

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GreeterServicer(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        logging.info(f"Otrzymano żądanie SayHello od: {request.name}")
        response = helloworld_pb2.HelloReply(message=f"Witaj, {request.name}!")
        logging.info(f"Wysłano odpowiedź: {response.message}")
        return response

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(GreeterServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logging.info("Serwer gRPC nasłuchuje na porcie 50051...")
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        logging.info("Zatrzymywanie serwera...")
        server.stop(0)

if __name__ == '__main__':
    _ONE_DAY_IN_SECONDS = 60 * 60 * 24
    serve()