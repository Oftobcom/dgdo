Create a simple Docker-based FastAPI example. Here's a complete setup:

## Project Structure
```
fastapi-docker-example/
├── app/
│   ├── __init__.py
│   └── main.py
├── requirements.txt
├── Dockerfile
└── README.md
```

## 1. requirements.txt
```txt
fastapi==0.104.1
uvicorn==0.24.0
```

## 2. app/main.py
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Simple FastAPI Docker Example", version="1.0.0")

class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None

@app.get("/")
async def read_root():
    return {"message": "Hello, World! Welcome to FastAPI with Docker"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

@app.post("/items/")
async def create_item(item: Item):
    return {
        "message": "Item created successfully",
        "item": item.dict(),
        "total_price": item.price + (item.tax or 0)
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Service is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 3. Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app ./app

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

## 4. Build and Run

### Build the Docker image:
```bash
docker build -t fastapi-docker-example .
```

### Run the container:
```bash
docker run -d -p 8000:8000 --name fastapi-app fastapi-docker-example
```

### For development with auto-reload (mount current directory):
```bash
docker run -d -p 8000:8000 -v $(pwd)/app:/app/app --name fastapi-dev fastapi-docker-example
```

## 5. Test the API

Once running, you can test the API:

### Using curl:
```bash
# Test root endpoint
curl http://localhost:8000/

# Test health check
curl http://localhost:8000/health

# Test GET endpoint
curl http://localhost:8000/items/123?q=test

# Test POST endpoint
curl -X POST "http://localhost:8000/items/" \
     -H "Content-Type: application/json" \
     -d '{"name": "Laptop", "description": "Gaming laptop", "price": 999.99, "tax": 99.99}'
```

### Using browser:
- Open http://localhost:8000/docs for interactive Swagger UI
- Open http://localhost:8000/redoc for ReDoc documentation

## 6. Docker Compose (Optional)

Create a `docker-compose.yml` file for easier management:

```yaml
version: '3.8'

services:
  fastapi-app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./app:/app/app  # For development with hot-reload
    environment:
      - ENVIRONMENT=development
    container_name: fastapi-container
```

Run with Docker Compose:
```bash
docker-compose up -d
```

## Key Features:

1. **Simple FastAPI app** with GET and POST endpoints
2. **Dockerized** for easy deployment
3. **Auto-reload** for development
4. **Interactive documentation** automatically generated
5. **Health check** endpoint
6. **Pydantic models** for request validation

The API will be available at `http://localhost:8000` with automatic interactive documentation at `/docs` and `/redoc`.