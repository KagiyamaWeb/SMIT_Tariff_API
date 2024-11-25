import json

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from kafka import KafkaProducer
from typing import Optional

from datetime import datetime
from database import get_db
from schemas import RateCreate, InsuranceCalculationRequest
from models import Rate

app = FastAPI()


producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def log_change(user_id: Optional[int], action: str):
    message = {
        "user_id": user_id,
        "action": action,
        "timestamp": datetime.utcnow().isoformat()
    }
    producer.send('rate_changes', message)

@app.post("/rates/")
async def create_rate(rate: RateCreate, db: Session = Depends(get_db)):
    db_rate = Rate(**rate.dict())
    db.add(db_rate)
    db.commit()
    db.refresh(db_rate)
    
    log_change(None, f"Created rate for {rate.cargo_type}")
    return db_rate

@app.delete("/rates/{rate_id}")
async def delete_rate(rate_id: int, db: Session = Depends(get_db)):
    rate = db.query(Rate).filter(Rate.id == rate_id).first()
    if not rate:
        raise HTTPException(status_code=404, detail="Rate not found")
    
    db.delete(rate)
    db.commit()
    
    log_change(None, f"Deleted rate {rate_id}")
    return {"message": "Rate deleted"}

@app.put("/rates/{rate_id}")
async def update_rate(rate_id: int, rate: RateCreate, db: Session = Depends(get_db)):
    db_rate = db.query(Rate).filter(Rate.id == rate_id).first()
    if not db_rate:
        raise HTTPException(status_code=404, detail="Rate not found")
    
    for key, value in rate.dict().items():
        setattr(db_rate, key, value)
    
    db.commit()
    db.refresh(db_rate)
    
    log_change(None, f"Updated rate {rate_id}")
    return db_rate

@app.post("/calculate-insurance/")
async def calculate_insurance(request: InsuranceCalculationRequest, db: Session = Depends(get_db)):
    rate = db.query(Rate)\
        .filter(Rate.cargo_type == request.cargo_type)\
        .filter(Rate.effective_date <= request.date)\
        .order_by(Rate.effective_date.desc())\
        .first()
    
    if not rate:
        raise HTTPException(status_code=404, detail="No rate found for given cargo type and date")
    
    insurance_cost = request.declared_value * rate.rate
    return {"insurance_cost": insurance_cost}