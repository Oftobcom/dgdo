FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y gcc \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Proto files
COPY protos/ /app/protos/

# Generate gRPC Python code
RUN python -m grpc_tools.protoc \
    -I=/app/protos \
    --python_out=/app \
    --grpc_python_out=/app \
    /app/protos/*.proto

ENV PYTHONPATH=/app
