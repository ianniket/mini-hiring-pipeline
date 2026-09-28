import re
from typing import Dict, Any, List
from datetime import datetime, timedelta

def parse_search_query(query: str) -> Dict[str, Any]:
    """
    Parses a natural language search query for candidates.
    Returns a dictionary of filters, e.g.:
    {
        "name_fuzzy": "priya sharma",
        "current_stage": ["Interview"],
        "stuck_stage": {"stage": "Screening", "days_min": 7},
        "moved_stage": {"stage": "Interview", "since": datetime},
        "reached_stage_but_not": {"reached": "Offer", "not_stage": "Hired"},
        "exclude_status": ["Rejected"],
        "error": "Message if doesn't make sense"
    }
    """
    query = query.lower().strip()
    filters = {}
    
    # Check for empty query
    if not query:
        return {"error": "Please enter a search query."}

    # 1. "Who's in Interview right now?"
    if "right now" in query or "who is in" in query or "who's in" in query:
        stages = ["applied", "screening", "interview", "offer", "hired"]
        found_stages = [s for s in stages if s in query]
        if found_stages:
            filters["current_stage"] = [s.capitalize() for s in found_stages]
    
    # 2. "Who has been stuck in Screening for more than a week?"
    stuck_match = re.search(r"stuck in (applied|screening|interview|offer) for more than a (week|month|day|\d+ days?)", query)
    if stuck_match:
        stage = stuck_match.group(1).capitalize()
        duration_str = stuck_match.group(2)
        days = 7
        if "month" in duration_str:
            days = 30
        elif "day" in duration_str and not "days" in duration_str:
            days = 1
        elif "days" in duration_str:
            days = int(re.search(r"\d+", duration_str).group(0))
            
        filters["stuck_stage"] = {"stage": stage, "days_min": days}
        
    # 3. "Who moved to Interview since Monday?"
    # A bit hard to parse "Monday" accurately without date context, we will map "monday", "yesterday", etc. to approx dates,
    # or just look for "moved to X since Y"
    moved_match = re.search(r"moved to (applied|screening|interview|offer|hired) since (\w+)", query)
    if moved_match:
        stage = moved_match.group(1).capitalize()
        since_word = moved_match.group(2)
        # We will handle "monday" in the main handler or just pass the word down
        filters["moved_stage"] = {"stage": stage, "since_word": since_word}

    # 4. "Who reached the Offer stage but didn't get hired?"
    reached_match = re.search(r"reached (the )?(applied|screening|interview|offer) (stage )?but didn'?t get (hired|an offer|interviewed)", query)
    if reached_match:
        reached = reached_match.group(2).capitalize()
        not_got = reached_match.group(4)
        not_stage = "Hired"
        if not_got == "an offer": not_stage = "Offer"
        if not_got == "interviewed": not_stage = "Interview"
        filters["reached_stage_but_not"] = {"reached": reached, "not_stage": not_stage}

    # 5. "Everyone except rejected candidates."
    if "except rejected" in query or "not rejected" in query:
        filters["exclude_status"] = ["Rejected"]
        
    # 6. Name search / fallback
    # If no complex regex matched, or if there's leftover text, treat it as a fuzzy name search
    # E.g. "Find Priya Sharma"
    find_match = re.search(r"find ([\w\s]+)", query)
    if find_match:
        filters["name_fuzzy"] = find_match.group(1).strip()
    
    # If no filters applied at all, just treat the whole query as a name fuzzy search
    if not filters:
        # Check if they typed a bunch of gibberish
        if len(query) > 50 and len(query.split()) > 10:
             return {"error": "This search is too complex or doesn't make sense to me. Try asking something like 'Who is in Interview?'"}
             
        filters["name_fuzzy"] = query.strip()
        
    return filters
