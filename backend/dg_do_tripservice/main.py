from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, get_db
import models, schemas, crud
from typing import List
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional

class AcceptTripRequest(BaseModel):
    trip_id: UUID
    driver_id: UUID

class TripArrivedRequest(BaseModel):
    trip_id: UUID

class TripCompleteRequest(BaseModel):
    trip_id: UUID

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="DG Do - Trip Service", version="3.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Trip Service API is online with CRUD & Soft Delete support!"}

@app.post("/trips/create", response_model=schemas.TripResponse, status_code=status.HTTP_201_CREATED)
def create_new_trip(trip: schemas.TripCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_trip(db=db, trip_data=trip)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Safar buyurtmasini yaratishda xatolik: {str(e)}"
        )

@app.post("/trips/accept")
def accept_trip(payload: AcceptTripRequest, db: Session = Depends(get_db)):
    trip = db.query(models.Trip).filter(models.Trip.id == payload.trip_id, models.Trip.is_active == True).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Safar topilmadi yoki faol emas")
    
    trip.status = "accepted"
    trip.driver_id = payload.driver_id
    db.commit()
    db.refresh(trip)
    return {"message": "Safar qabul qilindi", "trip": trip}

@app.post("/trips/arrived")
def set_trip_arrived(payload: TripArrivedRequest, db: Session = Depends(get_db)):
    trip = db.query(models.Trip).filter(models.Trip.id == payload.trip_id, models.Trip.is_active == True).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Safar topilmadi yoki faol emas")
    
    trip.status = "arrived"
    db.commit()
    db.refresh(trip)
    return {"message": "Haydovchi yetib bordi", "trip": trip}

@app.post("/trips/complete")
def complete_trip(payload: TripCompleteRequest, db: Session = Depends(get_db)):
    trip = db.query(models.Trip).filter(models.Trip.id == payload.trip_id, models.Trip.is_active == True).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Safar topilmadi yoki faol emas")
    
    trip.status = "completed"
    db.commit()
    db.refresh(trip)
    return {"message": "Safar yakunlandi", "trip": trip}

@app.post("/payments/create", response_model=schemas.PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_new_payment(payment: schemas.PaymentCreate, db: Session = Depends(get_db)):
    try:
        db_payment = models.Payment(
            trip_id=payment.trip_id,
            amount=payment.amount,
            currency=payment.currency,
            payment_method=getattr(payment, 'payment_method', 'cash'),
            status="success"
        )
        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)
        return db_payment
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"To'lovni amalga oshirishda xatolik: {str(e)}"
        )

# --- Yangi CRUD Endpointlar ---

@app.get("/trips", response_model=List[schemas.TripResponse])
def get_all_trips(db: Session = Depends(get_db)):
    trips = crud.get_all_trips(db)
    for trip in trips:
        # Agar distance None bo'lsa, uning o'rniga 0 qo'shamiz yoki hech narsa qilmaymiz 
        # (shunda sxema talabi buzilmaydi)
        if trip.distance is None:
            trip.distance = 0.0
    return trips

@app.get("/trips/{trip_id}", response_model=schemas.TripResponse)
def get_trip_by_id(trip_id: UUID, db: Session = Depends(get_db)):
    trip = crud.get_trip_by_id(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Safar topilmadi")
    return trip

@app.get("/trips/search/passenger", response_model=List[schemas.TripResponse])
def get_trips_by_passenger_id(passenger_id: UUID, db: Session = Depends(get_db)):
    return crud.get_trips_by_passenger_id(db, passenger_id)

@app.put("/trips/{trip_id}", response_model=schemas.TripResponse)
def update_trip(trip_id: UUID, trip_update: schemas.TripUpdate, db: Session = Depends(get_db)):
    trip = crud.update_trip(db, trip_id, trip_update)
    if not trip:
        raise HTTPException(status_code=404, detail="Safar topilmadi")
    return trip

@app.delete("/trips/{trip_id}", status_code=status.HTTP_200_OK)
def delete_trip(trip_id: UUID, db: Session = Depends(get_db)):
    success = crud.delete_trip(db, trip_id)
    if not success:
        raise HTTPException(status_code=404, detail="Safar topilmadi")
    return {"message": "Safar muvaffaqiyatli arxivlandi (o'chirildi)"}