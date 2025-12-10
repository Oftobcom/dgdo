FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy proto for stub generation
COPY ../proto /app/proto_src
# generate python grpc code into package 'proto'
RUN python -m grpc_tools.protoc -I/proto_src --python_out=./proto --grpc_python_out=./proto /proto_src/helloworld.proto \
 && sed -i "1i# Generated stub - package fix" proto/helloworld_pb2.py || true

# copy app
COPY app.py /app/app.py

ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
