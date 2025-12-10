from fastapi import FastAPI
import grpc
import proto.helloworld_pb2 as hello_pb2
import proto.helloworld_pb2_grpc as hello_pb2_grpc

app = FastAPI()

GRPC_TARGET = "greeter:50051"  # uses docker-compose service name

@app.get("/")
async def root():
    return {"status": "ok"}

@app.get("/sayhello/{name}")
async def say_hello(name: str):
    with grpc.insecure_channel(GRPC_TARGET) as channel:
        stub = hello_pb2_grpc.GreeterStub(channel)
        req = hello_pb2.HelloRequest(name=name)
        res = stub.SayHello(req, timeout=5)
        return {"message": res.message}
