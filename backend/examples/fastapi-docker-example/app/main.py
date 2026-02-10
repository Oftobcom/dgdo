from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Simple FastAPI Docker Example")

class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None

@app.get("/")
async def read_root():
    return {"message": "Hello from FastAPI Docker! Greetings from Rahmatjon I. Hakimov!"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

@app.post("/items/")
async def create_item(item: Item):
    return {"message": f"Item {item.name} created", "item": item}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}