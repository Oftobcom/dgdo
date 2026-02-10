## What Auth Service must do (MVP discipline)

**It must:**

1. Authenticate user (login)
2. Issue **JWT access token**
3. Validate credentials against its own DB
4. Be callable **only by API Gateway**

**It must NOT (yet):**

* Refresh tokens
* OAuth / social login
* Roles & permissions
* Device management
* Session storage
* Email / SMS verification

👉 Auth is a **token factory**, nothing more.

---

## Contract between API Gateway ↔ Auth Service

**Login flow (only one):**

```
POST /auth/login
→ { email, password }
← { access_token, token_type: "bearer" }
```

That’s it. No extra endpoints.

---

## Minimal project structure

```
auth-service/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── security.py
│   ├── models.py
│   └── routes.py
├── requirements.txt
└── Dockerfile
```

Still boring. Good.

---

## `requirements.txt`

```txt
fastapi
uvicorn
python-jose[cryptography]
passlib[bcrypt]
sqlalchemy
psycopg2-binary
```

No Redis. No Celery. No Kafka.
You’re building auth, not a PhD thesis.

---

## `config.py`

```python
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://auth_user:auth_pass@postgres:5432/auth_db"
)

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60
```

---

## `security.py`

All crypto lives here. No leaks.

```python
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def create_access_token(subject: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {
        "sub": subject,
        "exp": expire
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
```

---

## `models.py` (minimal User model)

```python
from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
```

No roles. No status flags. MVP only.

---

## `routes.py`

```python
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from app.security import verify_password, create_access_token
from app.models import User

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login")
def login(email: str, password: str, db: Session):
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(subject=user.id)
    return {
        "access_token": token,
        "token_type": "bearer"
    }
```

This endpoint does **exactly one thing**.
That’s intentional.

---

## `main.py`

```python
from fastapi import FastAPI
from app.routes import router

app = FastAPI(
    title="DG Do Auth Service",
    version="0.1.0"
)

app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok"}
```

---

## Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## How API Gateway uses Auth (important discipline)

**Gateway behavior:**

* `/auth/login` → forward to Auth Service
* For protected routes:

  * **do NOT validate JWT**
  * only forward `Authorization: Bearer ...`

**Later** you can add token validation in Gateway or downstream services.

---

## STOP POINT (critical)

Once this works, **STOP**.

Do **NOT**:

* add refresh tokens
* add middleware
* add roles
* add permissions
* add “just one more endpoint”

Every extra feature here delays DG Do.

---

## Architecture sanity check

```
Mobile App
   ↓
API Gateway
   ↓
Auth Service ──→ PostgreSQL
```

Auth never talks to other services.
Other services trust the Gateway.
