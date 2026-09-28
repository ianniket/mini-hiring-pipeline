from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime, timedelta
from typing import List, Dict, Any

from . import models, schemas, database
from .search_parser import parse_search_query

# Create tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Mini Hiring Pipeline")

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

STAGE_ORDER = {
    "Applied": 0,
    "Screening": 1,
    "Interview": 2,
    "Offer": 3,
    "Hired": 4
}

def format_time_in_stage(candidate, current_time=None):
    if current_time is None:
        current_time = datetime.utcnow()
    # Find the timestamp when they entered the current stage
    # Assuming history is sorted, we can look for the most recent entry of the current_stage
    entry_time = candidate.created_at
    for h in candidate.history:
        if h.stage == candidate.current_stage:
            entry_time = h.timestamp
            break
            
    diff = current_time - entry_time
    days = diff.days
    if days == 0:
        return "Today"
    elif days == 1:
        return "1 day"
    return f"{days} days"


@app.get("/")
def root():
    return {"message": "Mini Hiring Pipeline API is running"}


@app.post("/candidates", response_model=schemas.Candidate)
def create_candidate(candidate: schemas.CandidateCreate, db: Session = Depends(get_db)):
    db_candidate = models.Candidate(
        name=candidate.name,
        current_stage="Applied",
        status="Active"
    )
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    
    # Add history
    history = models.StageHistory(candidate_id=db_candidate.id, stage="Applied")
    db.add(history)
    db.commit()
    db.refresh(db_candidate)
    
    return db_candidate

@app.get("/candidates", response_model=List[schemas.Candidate])
def get_candidates(db: Session = Depends(get_db)):
    candidates = db.query(models.Candidate).all()
    # Populate time_in_stage
    now = datetime.utcnow()
    for c in candidates:
        c.time_in_stage = format_time_in_stage(c, now)
    return candidates

@app.get("/candidates/{candidate_id}", response_model=schemas.Candidate)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    c = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Candidate not found")
    c.time_in_stage = format_time_in_stage(c)
    return c

@app.post("/candidates/{candidate_id}/stage", response_model=schemas.Candidate)
def move_candidate(candidate_id: int, move: schemas.StageMove, db: Session = Depends(get_db)):
    c = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    if c.status in ["Hired", "Rejected"]:
        raise HTTPException(status_code=400, detail="Cannot change stage of a finalized candidate.")
        
    new_stage = move.new_stage
    
    if new_stage == "Rejected":
        c.status = "Rejected"
    else:
        # Check order
        if new_stage not in STAGE_ORDER:
            raise HTTPException(status_code=400, detail="Invalid stage.")
            
        current_order = STAGE_ORDER.get(c.current_stage, 0)
        new_order = STAGE_ORDER[new_stage]
        
        if new_order != current_order + 1:
            raise HTTPException(status_code=400, detail=f"Cannot skip stages or move backward. Must move from {c.current_stage} to the next stage.")
            
        c.current_stage = new_stage
        if new_stage == "Hired":
            c.status = "Hired"
            
    # Add history
    history = models.StageHistory(candidate_id=c.id, stage=new_stage)
    db.add(history)
    db.commit()
    db.refresh(c)
    
    return c

@app.get("/search")
def search_candidates(q: str, db: Session = Depends(get_db)):
    filters = parse_search_query(q)
    
    if "error" in filters:
        return {"error": filters["error"], "results": []}
        
    candidates = db.query(models.Candidate).all()
    results = []
    now = datetime.utcnow()
    
    for c in candidates:
        match_score = 0
        include = True
        
        # 1. fuzzy name
        if "name_fuzzy" in filters:
            # Simple matching + basic distance check implemented in search_parser
            q_name = filters["name_fuzzy"].lower()
            c_name = c.name.lower()
            
            # Simple substring match
            if q_name in c_name:
                match_score += 100
            else:
                # Custom distance check for typos like "sharam" -> "sharma"
                def levenshtein(s1, s2):
                    if len(s1) < len(s2):
                        return levenshtein(s2, s1)
                    if len(s2) == 0:
                        return len(s1)
                    prev_row = range(len(s2) + 1)
                    for i, c1 in enumerate(s1):
                        curr_row = [i + 1]
                        for j, c2 in enumerate(s2):
                            insertions = prev_row[j + 1] + 1
                            deletions = curr_row[j] + 1
                            substitutions = prev_row[j] + (c1 != c2)
                            curr_row.append(min(insertions, deletions, substitutions))
                        prev_row = curr_row
                    return prev_row[-1]
                
                # Check distance against parts of the name
                parts = c_name.split()
                best_dist = min([levenshtein(q_name, p) for p in parts] + [levenshtein(q_name, c_name)])
                
                # If distance is small relative to word length (e.g. 2 char difference for a 6 char word)
                if best_dist <= 2 and len(q_name) > 4:
                    match_score += 75
                else:
                    if len(filters) == 1:
                        include = False
                    else:
                        match_score += 5
                    
        # 2. current_stage
        if "current_stage" in filters:
            if c.current_stage not in filters["current_stage"]:
                include = False
            else:
                match_score += 100
                
        # 3. stuck_stage
        if "stuck_stage" in filters:
            stuck_info = filters["stuck_stage"]
            if c.current_stage != stuck_info["stage"]:
                include = False
            else:
                # calculate days in stage
                days_in = 0
                for h in c.history:
                    if h.stage == c.current_stage:
                        days_in = (now - h.timestamp).days
                        break
                if days_in < stuck_info["days_min"]:
                    include = False
                else:
                    match_score += 100
                    
        # 4. moved_stage (e.g. moved to Interview since Monday)
        if "moved_stage" in filters:
            moved_info = filters["moved_stage"]
            stage = moved_info["stage"]
            
            # Simple heuristic for "since monday" etc -> let's just say "in the last 7 days" for demo purposes
            # Or we can do better date math, but for now:
            cutoff = now - timedelta(days=7) 
            
            moved = False
            for h in c.history:
                if h.stage == stage and h.timestamp >= cutoff:
                    moved = True
                    break
                    
            if not moved:
                include = False
            else:
                match_score += 100
                
        # 5. reached_stage_but_not
        if "reached_stage_but_not" in filters:
            reached = filters["reached_stage_but_not"]["reached"]
            not_stage = filters["reached_stage_but_not"]["not_stage"]
            
            has_reached = any(h.stage == reached for h in c.history)
            has_not = not any(h.stage == not_stage for h in c.history)
            
            if not (has_reached and has_not):
                include = False
            else:
                match_score += 100
                
        # 6. exclude_status
        if "exclude_status" in filters:
            if c.status in filters["exclude_status"]:
                include = False
                
        if include:
            c_dict = schemas.Candidate.from_orm(c).dict()
            c_dict["time_in_stage"] = format_time_in_stage(c, now)
            results.append({
                "candidate": c_dict,
                "score": match_score
            })
            
    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    
    # Return just the candidates
    final_candidates = [r["candidate"] for r in results]
    
    return {"filters_applied": filters, "results": final_candidates}