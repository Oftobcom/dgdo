# C++ MatchingService
docker build -t dgdo-matching -f docker/matching_service.Dockerfile .

Perfect, your image is built as `dgdo-matching`. Here’s how to run it:

---

### **1. Basic detached run**

```bash
docker run -d --name dgdo-matching -p 50051:50051 dgdo-matching
```

**Explanation:**

* `-d` → run in background
* `--name dgdo-matching` → easy reference for `docker stop/start/logs`
* `-p 50051:50051` → expose gRPC port from container to host

You can check it’s running:

```bash
docker ps
```

---

### **2. Attach logs**

To see real-time logs:

```bash
docker logs -f dgdo-matching
```

You should see:

```
MatchingService listening on 0.0.0.0:50051
```

---

### **3. Stop / restart container**

```bash
docker stop dgdo-matching
docker start dgdo-matching
```

---

### **4. Test gRPC endpoint**


# Here’s how to run `test_matching.py`:

---

### **1. Make sure the MatchingService container is running**

```bash
docker ps
```

You should see your `dgdo-matching` container listening on port `50051`. If not, run it:

```bash
docker run -d -p 50051:50051 --name dgdo-matching dgdo-matching
```

---

### **2. Make sure the Python environment has dependencies**

You need **grpcio** and **grpcio-tools** installed:

```bash
python3 -m pip install grpcio grpcio-tools
```

---

### **3. Verify generated Python modules are in the path**

* The `sys.path.append` in your script should point to the folder containing the **generated Python gRPC files** from `matching.proto`.
* Example folder: `dgdo/generated/python`

---

### **4. Run the test script**

From the directory where `test_matching.py` is located:

```bash
python3 test_matching.py
```

---

### **5. Expected output**

You should see:

```
[2025-12-21 12:00:00] TripRequest ID: trip_req_123
Simulated Matching Candidates (deterministic):
Driver ID: driver_2, Probability: 0.33, Location: (39.61, 67.81)
Driver ID: driver_5, Probability: 0.33, Location: (39.64, 67.84)
Driver ID: driver_1, Probability: 0.33, Location: (39.6, 67.8)

[From gRPC server] Matching Response:
Driver ID: driver_1, Probability: 0.33
Driver ID: driver_2, Probability: 0.33
Driver ID: driver_3, Probability: 0.33
```

* The first block is **simulated deterministic candidates**.
* The second block is the **actual gRPC server response**.

---

### **Tip for debugging**

* If `ModuleNotFoundError` → check your `sys.path.append` to ensure Python can import the generated files.
* If connection fails → make sure the gRPC port `50051` is mapped and MatchingService is running.
* If proto mismatch → regenerate Python gRPC code:

```bash
python -m grpc_tools.protoc -I=proto/ --python_out=generated/python --grpc_python_out=generated/python proto/matching.proto
```

---

If you want, I can **write a full local end-to-end Python test** that also simulates **TripRequest creation, driver status updates, matching, and Trip FSM transitions** for DG Do.

Do you want me to do that?
