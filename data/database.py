import json
import os
import threading
from typing import List, Dict

DB_FILE = os.path.join(os.path.dirname(__file__), "custom_candidates_db.json")
_db_lock = threading.Lock()

def load_custom_candidates() -> List[Dict]:
    """Load all custom candidates from the JSON database file."""
    if not os.path.exists(DB_FILE):
        return []
    
    with _db_lock:
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

def load_custom_candidates_by_batch(batch_name: str) -> List[Dict]:
    """Load candidates belonging to a specific upload batch."""
    all_candidates = load_custom_candidates()
    return [c for c in all_candidates if c.get("upload_batch_name") == batch_name]

def get_upload_history() -> List[Dict]:
    """Get a list of unique upload batches with their counts and timestamps."""
    all_candidates = load_custom_candidates()
    batches = {}
    
    for c in all_candidates:
        batch_name = c.get("upload_batch_name")
        if not batch_name:
            continue
            
        if batch_name not in batches:
            batches[batch_name] = {
                "batch_name": batch_name,
                "timestamp": c.get("upload_timestamp", ""),
                "count": 0
            }
        batches[batch_name]["count"] += 1
        
    # Sort by timestamp descending
    return sorted(list(batches.values()), key=lambda x: x["timestamp"], reverse=True)

def save_custom_candidates_batch(new_candidates: List[Dict], batch_name: str):
    """Append a batch of custom candidates to the JSON database file."""
    from datetime import datetime
    timestamp = datetime.now().isoformat()
    
    for c in new_candidates:
        c["upload_batch_name"] = batch_name
        c["upload_timestamp"] = timestamp

    with _db_lock:
        candidates = []
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, "r", encoding="utf-8") as f:
                    candidates = json.load(f)
            except Exception:
                pass
                
        # Check for duplicates by ID
        existing_ids = {c.get("id") for c in candidates}
        for candidate in new_candidates:
            if candidate.get("id") not in existing_ids:
                candidates.append(candidate)
                existing_ids.add(candidate.get("id"))
                
        try:
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump(candidates, f, indent=2)
        except Exception:
            pass

def save_custom_candidate(candidate: Dict):
    """Backward compatibility wrapper, default batch name."""
    save_custom_candidates_batch([candidate], "single_upload")
