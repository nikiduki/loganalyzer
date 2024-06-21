from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="LogAnalyzer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Log(Base):
    '''Model of data for logs in a database.
       :param id (int): Log ID.
       :param timestamp (datetime): Time of log creation.
       :param server_id (str): Server ID.
       :param log_level (str): Level of log (INFO, WARNING, ERROR, etc.).
       :param message (str): Log message.
       :param anomaly_score (float): Anomaly score.
    '''
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    server_id = Column(String, index=True)
    log_level = Column(String, index=True)
    message = Column(String)
    anomaly_score = Column(Float, index=True)

Base.metadata.create_all(bind=engine)

class LogSchema(BaseModel):
    '''Data schema for API responses.
    '''
    id: int
    timestamp: datetime
    server_id: str
    log_level: str
    message: str
    anomaly_score: float

    class Config:
        orm_mode = True

def get_db():
    '''Dependency to get a database session.
    '''
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/logs/", response_model=List[LogSchema])
async def get_logs(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)):
    '''Getting a list of logs with pagination.
       :param skip (int): Number of records to skip.
       :param limit (int): Maximum number of records to be returned.
       :param db (Session): Database session.
       :return (List[LogSchema]): List of logs.
    '''
    logs = db.query(Log).offset(skip).limit(limit).all()
    return logs

@app.get("/logs/anomalous/", response_model=List[LogSchema])
async def get_anomalous_logs(
    threshold: float = 0.8, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)):
    '''Getting a list of anomalous logs with pagination.
       :param threshold (float): Threshold value for defining an anomaly.
       :param skip (int): Number of records to skip.
       :param limit (int): Maximum number of records to be returned.
       :param db (Session): Database session.
       :return (List[LogSchema]): List of anomalous logs.
    '''
    logs = db.query(Log).filter(Log.anomaly_score > threshold).offset(skip).limit(limit).all()
    return logs

@app.get("/logs/stats/")
async def get_log_stats(db: Session = Depends(get_db)):
    '''Getting log statistics.
       :param db (Session): Database session.
       :return (dict): Log statistics.
    '''
    total_logs = db.query(Log).count()
    anomalous_logs = db.query(Log).filter(Log.anomaly_score > 0.8).count()
    return {
        "total_logs": total_logs,
        "anomalous_logs": anomalous_logs,
        "anomaly_percentage": (anomalous_logs / total_logs) * 100 if total_logs > 0 else 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
