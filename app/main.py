import os
from contextlib import contextmanager
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import SessionLocal, engine, Base, get_db

import models, schemas, crud

# rag_engine = None

app = FastAPI(
    title="Bus Ticket Booking & RAG API",
    description="A hybrid service for bus booking (SQL) and policy lookups (RAG).",
    version="1.0.0",
)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@contextmanager
def get_db_context():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    
    Base.metadata.create_all(bind=engine)
    print("SQL Database tables created")
    
    with get_db_context() as db:
        try:
            existing_route = db.query(models.BusRoute).first()
            if existing_route:
                print("Bus routes already exist in the database. Skipping ingestion.")
            else:
                crud.ingest_routes_from_json(db, json_filepath="../data/data.json")
        except FileNotFoundError:
            print("ERROR: data/data.json not found...")
        except Exception as e:
            print(f"ERROR during route ingestion: {e}")

    # try:
    
    #     global rag_engine
    #     import rag_engine as _rag
    #     rag_engine = _rag

    #     rag_engine.create_vector_store()
    # except Exception as e:
    #     print(f"ERROR during RAG vector store setup or import: {e}")

    #     if "GEMINI_API_KEY" not in os.environ or not os.environ["GEMINI_API_KEY"]:
    #         print("GEMINI_API_KEY is missing !")

    # print(os.environ.get("GEMINI_API_KEY", "GEMINI_API_KEY not set"))
    # print("Startup Complete. API Ready.")


@app.get("/")
def check_api():
    return {"message": "Application is running."}

@app.get("/api/all_routes")
def all_routes(db: Session = Depends(get_db)):
    routes = db.query(models.BusRoute).all()
    return routes

@app.get("/api/search_buses/{origin}/{destination}", response_model=List[schemas.BusRoute])
def search_buses(origin: str, destination: str, db: Session = Depends(get_db)):
    
    routes = crud.get_buses_by_route(db, origin=origin, destination=destination)
    # print(routes)
    if not routes:
        return []
    return {
        "total": len(routes),
        "routes": routes
    }


@app.post("/api/book_ticket", response_model=schemas.Booking, status_code=status.HTTP_201_CREATED)
def book_ticket(booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    
    route = db.query(models.BusRoute).filter(models.BusRoute.id == booking.route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Bus route not found.")
        
    db_booking = crud.create_booking(db=db, booking=booking)
    return db_booking


@app.get("/api/bookings/{phone}", response_model=List[schemas.Booking])
def view_bookings(phone: str, db: Session = Depends(get_db)):
    bookings = crud.get_bookings_by_phone(db, user_phone=phone)
    
    # return [schemas.Booking.model_validate(b) for b in bookings]
    return bookings


@app.post("/api/cancel_booking/{booking_id}", response_model=schemas.Booking)
def cancel_booking_endpoint(booking_id: int, db: Session = Depends(get_db)):
    cancelled_booking = crud.cancel_booking(db, booking_id=booking_id)
    if not cancelled_booking:
        raise HTTPException(status_code=404, detail="Booking not found.")
    
    return cancelled_booking


# @app.post("/api/query_info")
# async def query_info(query_data: schemas.RAGQuery):
    
#     try:
#         if rag_engine is None:
#             raise HTTPException(
#                 status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
#                 detail="RAG service is not available. Missing dependencies or initialization failed.",
#             )

#         response_text = await rag_engine.process_rag_query(query_data.query)
#         return {"response": response_text}
#     except Exception as e:
#         # Catch LLM/API errors gracefully
#         print(f"RAG Pipeline Error: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
#             detail="The RAG service is currently unavailable or encountered an API error. Check backend logs."
#         )