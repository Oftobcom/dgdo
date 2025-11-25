from fastapi import FastAPI

from .routes import passenger, driver, trip

app = FastAPI()

app.include_router(passenger.router)
app.include_router(driver.router)
app.include_router(trip.router)

@app.get("/")
def root():
    return {"status": "DG Do API Gateway running"}
