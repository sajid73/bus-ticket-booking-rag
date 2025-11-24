import json
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from models import BusRoute
import models, schemas
from fastapi import Request, HTTPException

def ingest_routes_from_json(db: Session, json_filepath: str = "../data/data.json"):
    data = {}
    with open(json_filepath, 'r') as f:
        data.update(json.load(f))
        
    routes = []
    district_lookup = {d["name"]: d["dropping_points"] for d in data["districts"]}
    
    db.query(models.BusRoute).delete()
    db.commit()
    
    for provider in data["bus_providers"]:

        provider_name = provider["name"]
        covered = provider["coverage_districts"]
        
        for origin in covered:
            for destination in covered:
                if origin == destination:
                    continue

                dropping_points = district_lookup[destination]

                for dp in dropping_points:
                    route = {
                        "provider_name": provider_name,
                        "origin": origin,
                        "destination": destination,
                        "dropping_point": dp["name"],
                        "fare": dp["price"]
                    }
                    
                    routes.append(route)

    
    db.add_all([BusRoute(**route) for route in routes])
    db.commit()
    print(f"Successfully ingested {len(routes)} bus routes.")


def get_buses_by_route(db: Session, request: Request):
    origin = request.query_params.get("origin")
    destination = request.query_params.get("destination")
    if not origin or not destination:
        raise HTTPException(status_code=400, detail="Please provide both 'origin' and 'destination' query parameters.")
    
    return db.query(models.BusRoute).filter(
        func.lower(models.BusRoute.origin) == origin.lower(),
        func.lower(models.BusRoute.destination) == destination.lower()
    ).all()

def create_booking(db: Session, booking: schemas.BookingCreate):
    
    db_booking = models.Booking(
        route_id=booking.route_id,
        user_name=booking.user_name,
        user_phone=booking.user_phone,
        seat_number=booking.seat_number,
        status="Booked"
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

def get_bookings_by_phone(db: Session, user_phone: str):
    if not user_phone:
        return []

    try:
        phone_val = user_phone.strip()
        return db.query(models.Booking).options(joinedload(models.Booking.route)).filter(
            models.Booking.user_phone == phone_val
        ).all()
    except Exception as e:
        print(f"Error retrieving bookings for phone {user_phone}: {e}")
        return []

def cancel_booking(db: Session, booking_id: int):
    db_booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if db_booking:
        db_booking.status = "Canceled"
        db.commit()
        db.refresh(db_booking)
    return db_booking