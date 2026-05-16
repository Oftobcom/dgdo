from sqlalchemy.orm import Session
from uuid import UUID
import models, schemas
from decimal import Decimal

def get_all_trips(db: Session):
    return db.query(models.Trip).filter(models.Trip.is_active == True).all()

def get_trip_by_id(db: Session, trip_id: UUID):
    return db.query(models.Trip).filter(models.Trip.id == trip_id, models.Trip.is_active == True).first()

def get_trips_by_passenger_id(db: Session, passenger_id: UUID):
    return db.query(models.Trip).filter(models.Trip.passenger_id == passenger_id, models.Trip.is_active == True).all()

def update_trip(db: Session, trip_id: UUID, trip_update: schemas.TripUpdate):
    trip = get_trip_by_id(db, trip_id)
    if not trip:
        return None
    
    update_data = trip_update.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(trip, key, value)
            
    db.commit()
    db.refresh(trip)
    return trip

def delete_trip(db: Session, trip_id: UUID):
    trip = get_trip_by_id(db, trip_id)
    if not trip:
        return False
    
    # Soft delete (O'chirish o'rniga is_active holatini o'zgartiramiz)
    trip.is_active = False
    db.commit()
    db.refresh(trip)
    return True

def create_trip(db: Session, trip_data: schemas.TripCreate):
    p_lon = trip_data.pickup_location.longitude
    p_lat = trip_data.pickup_location.latitude
    d_lon = trip_data.dropoff_location.longitude
    d_lat = trip_data.dropoff_location.latitude
    
    db_trip = models.Trip(
        passenger_id=trip_data.passenger_id,
        pickup_location=f"POINT({p_lon} {p_lat})",
        dropoff_location=f"POINT({d_lon} {d_lat})",
        distance=trip_data.distance,
        estimated_fare=trip_data.estimated_fare
    )
    
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return db_trip