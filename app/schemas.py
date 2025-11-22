from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class BusRouteBase(BaseModel):
    provider_name: str
    origin: str
    destination: str
    departure_time: Optional[str] = None
    dropping_point: str
    fare: float
    total_seats: int = 40

class BusRoute(BusRouteBase):
    id: int
    
    class Config:
        from_attributes = True
        # orm_mode = True


class BookingCreate(BaseModel):
    route_id: int
    user_name: str
    user_phone: str
    seat_number: str

class Booking(BaseModel):
    id: int
    route_id: int
    route: Optional[BusRoute]
    user_name: str
    user_phone: str
    booking_time: datetime
    status: str
    
    class Config:
        from_attributes = True
        # orm_mode = True

class RAGQuery(BaseModel):
    query: str