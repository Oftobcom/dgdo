from fastapi import FastAPI

# Payment router ni import qilamiz
from app.presentation.api.payment_router import router as payment_router


# FastAPI application yaratamiz
app = FastAPI(
    title="DG Do PaymentService",   # Service nomi
    version="1.0.0",               # Service versiyasi
)

# Payment routelarini ulaymiz
app.include_router(payment_router)


# Healthcheck endpoint
@app.get("/")
def healthcheck():

    # Service ishlab turganini qaytaradi
    return {"message": "PaymentService is running"}