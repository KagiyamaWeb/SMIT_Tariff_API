from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime


Base = declarative_base()

class Rate(Base):
    __tablename__ = "rates"
    
    id = Column(Integer, primary_key=True)
    cargo_type = Column(String)
    rate = Column(Float)
    effective_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class RateChangeLog(Base):
    __tablename__ = "rate_change_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True)
    action = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    rate_id = Column(Integer, ForeignKey('rates.id'))
