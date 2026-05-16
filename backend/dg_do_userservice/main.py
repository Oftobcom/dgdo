from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, get_db
import models, schemas, crud
from typing import List
from uuid import UUID

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="DG Do - User Service", version="3.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/users/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_phone(db, phone=user.phone)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Bu telefon raqam allaqachon ro'yxatdan o'tgan!"
        )
    return crud.create_user(db=db, user=user)

@app.get("/users", response_model=List[schemas.UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    return crud.get_users(db)

@app.get("/users/search/name", response_model=List[schemas.UserResponse])
def search_users_by_email(name: str, db: Session = Depends(get_db)):
    """
    Swaggerda 'name' maydoniga emailning bir qismini (masalan: abbos yoki gmail) 
    yozib izlasangiz ham ishlayveradi.
    """
    return crud.search_users_by_email_start(db, email_prefix=name)

# --- GET /users/phone/{phone} ---
@app.get("/users/phone/{phone}", response_model=List[schemas.UserResponse])
def get_user_by_phone_part(phone: str, db: Session = Depends(get_db)):
    """
    Telefon raqamining xohlagan qismini yozib qidirish.
    """
    return crud.search_users_by_phone_part(db, phone_part=phone)

@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user_by_id(user_id: UUID, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_id(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    return db_user

@app.put("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: UUID, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = crud.update_user(db, user_id=user_id, user_update=user_update)
    if not db_user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    return db_user

@app.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(user_id: UUID, db: Session = Depends(get_db)):
    success = crud.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    return {"message": "Foydalanuvchi muvaffaqiyatli o'chirildi"}