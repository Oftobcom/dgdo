import grpc
from fastapi import FastAPI

import hello_pb2
import hello_pb2_grpc

app = FastAPI()

@app.get("/test")
async def test():
    async with grpc.aio.insecure_channel("host.docker.internal:50051") as channel:
        stub = hello_pb2_grpc.GreeterStub(channel)
        
        request = hello_pb2.HelloRequest(name="Rahmatjon Hakimov")
        response = await stub.SayHello(request)
        
        return {"grpc_response": response.message}
