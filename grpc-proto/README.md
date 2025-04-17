python -m grpc_tools.protoc -I=grpc-proto --python_out=grpc-proto mydata.proto

python -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. helloworld.proto