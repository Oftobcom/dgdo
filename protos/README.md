# dgdo

# DG Do — Open Source Ride-Hailing Platform

# **Domain laws**:

  * Trip cannot exist without driver
  * Matching is probabilistic
  * Only TripService creates Trip

👉 This is governance, not documentation.

---

### Generate code (C++ + Python)

You must **compile reality**, not trust humans.

**Python**

```bash
python3 -m grpc_tools.protoc \
  -I protos \
  --python_out=generated/python \
  --grpc_python_out=generated/python \
  protos/*.proto
```

**C++**

```bash
protoc -I protos \
  --cpp_out=generated/cpp \
  --grpc_out=generated/cpp \
  --plugin=protoc-gen-grpc=`which grpc_cpp_plugin` \
  protos/*.proto
```

If codegen fails → fix NOW.
Never “work around” broken protos.
