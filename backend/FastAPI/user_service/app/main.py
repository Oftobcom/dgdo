from fastapi import FastAPI

# users_router ni import qilamiz
from app.presentation.routers.users_router import router as users_router


# FastAPI application yaratamiz
app = FastAPI(
    title="DG Do UserService",   # Service nomi
    version="1.0.0",            # Service versiyasi
)


# Users API routelarini ulaymiz
app.include_router(users_router)


# Healthcheck endpoint
@app.get("/")
def healthcheck():
    # Service ishlab turganini qaytaradi
    return {"message": "UserService is running"}