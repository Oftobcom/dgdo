# dgdo

# DG Do — Open Source Ride-Hailing Platform

### Generate code (C++ + Python)

**Python**

```bash
python3 -m grpc_tools.protoc -I protos --python_out=generated/python --grpc_python_out=generated/python protos/*.proto
```

**C++**

```bash
protoc -I protos --cpp_out=generated/cpp --grpc_out=generated/cpp --plugin=protoc-gen-grpc=`which grpc_cpp_plugin` protos/*.proto
```

If codegen fails → fix NOW.
Never “work around” broken protos.
