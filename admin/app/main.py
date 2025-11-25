from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"admin": "DG Do admin panel placeholder"}
