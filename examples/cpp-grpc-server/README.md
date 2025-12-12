# ✅ **Build & Run in Ubuntu 22.04 (WSL2)**

### **Step 1 — Install Docker Desktop**

Enable WSL integration.

### **Step 2 — Navigate to your folder**

```bash
cd cpp-grpc-server
```

### **Step 3 — Build the Docker image**

```bash
docker build -t cpp-grpc-server .
```

### **Step 4 — Run the container**

```bash
docker run --rm -p 50051:50051 cpp-grpc-server
```

You should see:

```
Server listening on 0.0.0.0:50051
```

---

# ✅ **Test the Server (Optional)**

You can test with **grpcurl** from Linux:

Install:

```bash
sudo snap install grpcurl
```

Or:

```bash
sudo snap install --edge grpcurl
```

Test:

```bash
grpcurl -plaintext -d '{"name": "Rahmatjon"}' localhost:50051 helloworld.Greeter/SayHello
```

Expected output:

```json
{
  "message": "Hello Rahmatjon"
}
```

---

# ✅ **Test the Server (Optional)**

# ⚡ ALTERNATIVE : Use Python test client (zero dependencies)

Create file `test_client.py`:

```python
import grpc
import hello_pb2
import hello_pb2_grpc

channel = grpc.insecure_channel("localhost:50051")
stub = hello_pb2_grpc.GreeterStub(channel)
response = stub.SayHello(hello_pb2.HelloRequest(name="Rahmatjon"))
print(response.message)
```

Run:

```bash
python3 test_client.py
```
