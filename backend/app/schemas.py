from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class StageHistoryBase(BaseModel):
    stage: str
    timestamp: datetime

    class Config:
        from_attributes = True

class CandidateBase(BaseModel):
    name: str

class CandidateCreate(CandidateBase):
    pass

class Candidate(CandidateBase):
    id: int
    current_stage: str
    status: str
    created_at: datetime
    history: List[StageHistoryBase] = []
    
    # Extra field to determine how long they've been in the current stage
    time_in_stage: Optional[str] = None

    class Config:
        from_attributes = True

class StageMove(BaseModel):
    new_stage: str
