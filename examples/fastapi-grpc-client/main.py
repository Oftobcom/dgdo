import grpc
from fastapi import FastAPI

import hello_pb2
import hello_pb2_grpc

app = FastAPI()

@app.get("/hello")
async def say_hello(name: str = "Rahmatjon"):
    # If running via docker-compose -> use container name of the server:
    # channel = grpc.aio.insecure_channel("cpp-grpc-server:50051")
    channel = grpc.aio.insecure_channel("localhost:50051")

    async with channel:
        stub = hello_pb2_grpc.GreeterStub(channel)
        request = hello_pb2.HelloRequest(name=name)
        response = await stub.SayHello(request)

        return {"message": response.message}
