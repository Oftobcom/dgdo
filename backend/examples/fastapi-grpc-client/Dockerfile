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

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
