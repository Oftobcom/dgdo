Below is a **clean, minimal, working FastAPI app** that tests your **C++ gRPC server** using the `hello.proto` you already have.

It includes:

✅ async gRPC client
✅ endpoint `/test` sending a request to C++ server
✅ full file list **in one folder**, no subfolders
✅ works inside Docker or locally

---

# 📁 **Folder structure (`fastapi-grpc-client/`)**

All files in *one folder*, as you asked:

```
fastapi-grpc-client/
│── hello.proto
│── hello_pb2.py
│── hello_pb2_grpc.py
│── main.py
│── requirements.txt
│── Dockerfile
```

---

# 1️⃣ **hello.proto**

(Use your existing file)

```proto
syntax = "proto3";

package hello;

service HelloService {
    rpc SayHello (HelloRequest) returns (HelloResponse);
}

message HelloRequest {
    string name = 1;
}

message HelloResponse {
    string message = 1;
}
```

---

# 2️⃣ **Generate Python gRPC files**

Run this inside the folder:

```bash
python3 -m pip install grpcio grpcio-tools
python3 -m grpc_tools.protoc -I=. \
    --python_out=. \
    --grpc_python_out=. \
    hello.proto
```

This generates:

```
hello_pb2.py
hello_pb2_grpc.py
```

---

# 3️⃣ **main.py (FastAPI test client)**

```python
import grpc
from fastapi import FastAPI
import hello_pb2
import hello_pb2_grpc

app = FastAPI()

@app.get("/test")
async def test():
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        stub = hello_pb2_grpc.HelloServiceStub(channel)
        request = hello_pb2.HelloRequest(name="Rahmatjon")
        response = await stub.SayHello(request)
        return {"grpc_response": response.message}
```

### 🔥 If your server runs inside Docker:

Replace `"localhost"` with `"host.docker.internal"`:

```python
async with grpc.aio.insecure_channel("host.docker.internal:50051") as channel:
```

---

# 4️⃣ **requirements.txt**

```
fastapi
uvicorn[standard]
grpcio
grpcio-tools
```

---

# 5️⃣ **Dockerfile**

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY hello.proto .
COPY main.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# generate python grpc code
RUN python3 -m grpc_tools.protoc -I=. \
    --python_out=. \
    --grpc_python_out=. \
    hello.proto

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

# ▶️ Run FastAPI client (Docker)

```bash
docker build -t fastapi-grpc-client .
docker run --rm -p 8000:8000 fastapi-grpc-client --reload
```

---

# ▶️ Test your C++ gRPC server

Just open in browser:

```
http://localhost:8000/test
```

Or with curl:

```bash
curl http://localhost:8000/test
```

Expected output:

```json
{
  "grpc_response": "Hello, Rahmatjon!"
}
```

---

# Want health-check endpoint, reflection, or async reconnect logic?

Say **"add healthcheck"**, **"add grpc reflection"**, or **"add reconnect logic"**.
