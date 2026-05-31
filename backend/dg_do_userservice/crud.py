from sqlalchemy.orm import Session
from passlib.context import CryptContext
import models, schemas
from uuid import UUID
from fastapi import HTTPException, status

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def get_user_by_phone(db: Session, phone: str):
    # Faqat is_active = True bo'lgan foydalanuvchini tekshiramiz
    return db.query(models.User).filter(
        models.User.phone == phone,
        models.User.is_active == True
    ).first()

def get_user_by_id(db: Session, user_id: UUID):
    return db.query(models.User).filter(
        models.User.id == user_id,
        models.User.is_active == True
    ).first()

# --- YANGI: Telefon raqamining oxiri yoki biror qismi bo'yicha qidirish ---
from sqlalchemy.orm import Session
import models

# --- TELEFON RAQAMNING ISTALGAN QISMI BO'YICHA QIDIRISH ---
def search_users_by_email_start(db: Session, email_prefix: str):
    """
    Email tarkibida kiritilgan matn bor barcha foydalanuvchilarni topadi.
    is_active sharti olib tashlandi, hamma foydalanuvchilardan qidiradi.
    """
    return db.query(models.User).filter(
        models.User.email.ilike(f"%{email_prefix}%")
    ).all()

# --- TELEFON BO'YICHA ISTALGAN QISMI ORQALI QIDIRISH ---
def search_users_by_phone_part(db: Session, phone_part: str):
    """
    Telefon raqami tarkibida shu sonlar bor barcha foydalanuvchilarni topadi.
    """
    return db.query(models.User).filter(
        models.User.phone.like(f"%{phone_part}%")
    ).all()

# Pagination olib tashlandi, faqat aktivlar to'liq chiqadi
def get_users(db: Session):
    return db.query(models.User).filter(models.User.is_active == True).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)

    db_user = models.User(
        role=user.role,
        phone=user.phone,
        email=user.email,
        password_hash=hashed_password,
        is_active=True # Yangi foydalanuvchi avtomatik aktiv bo'ladi
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    if user.role == "passenger":
        db_profile = models.Passenger(user_id=db_user.id, full_name=user.full_name)
        db.add(db_profile)
    else:
        db_profile = models.Driver(user_id=db_user.id, full_name=user.full_name, license_number=f"TJK-{str(db_user.id)[:8]}")
        db.add(db_profile)

    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: UUID, user_update: schemas.UserUpdate):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        if key == "password":
            setattr(db_user, "password_hash", get_password_hash(value))
        else:
            setattr(db_user, key, value)
            
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: UUID):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False
    
    # O'chirish o'rniga is_active holatini False qilamiz
    db_user.is_active = False
    db.commit()
    db.refresh(db_user)
    return True