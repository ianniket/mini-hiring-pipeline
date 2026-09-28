from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Candidate(Base):
    __tablename__ = 'candidates'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    current_stage = Column(String)  # 'Applied', 'Screening', 'Interview', 'Offer', 'Hired', 'Rejected'
    status = Column(String) # 'Active', 'Hired', 'Rejected'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    history = relationship("StageHistory", back_populates="candidate", cascade="all, delete-orphan")

class StageHistory(Base):
    __tablename__ = 'stage_history'
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'))
    stage = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    candidate = relationship("Candidate", back_populates="history")
