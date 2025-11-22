from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class BusRoute(Base):
    """Represents a specific bus trip available for booking."""
    __tablename__ = "bus_routes"

    id = Column(Integer, primary_key=True, index=True)
    provider_name = Column(String, index=True)
    origin = Column(String, index=True)
    destination = Column(String, index=True)
    dropping_point = Column(String)
    departure_time = Column(String, nullable=True)
    fare = Column(Float)
    total_seats = Column(Integer, default=40)
    
    bookings = relationship("Booking", back_populates="route")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String)
    user_phone = Column(String, index=True)
    seat_number = Column(String) # Simple seat ID (e.g., "A1")
    booking_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status = Column(String, default="Booked")
    
    route_id = Column(Integer, ForeignKey("bus_routes.id"))
    route = relationship("BusRoute", back_populates="bookings")