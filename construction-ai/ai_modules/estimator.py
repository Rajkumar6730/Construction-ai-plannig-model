# ai_modules/estimator.py
import json, os

_DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample_projects.json')

def _load_projects():
    try:
        with open(_DATA_PATH) as f:
            return json.load(f)
    except Exception:
        return []

def find_similar_project(area, floors):
    projects = _load_projects()
    if not projects:
        return None
    best, best_score = None, float("inf")
    for p in projects:
        score = abs(p["area"]-area)/max(area,1)*0.7 + abs(p["floors"]-floors)/max(floors,1)*0.3
        if score < best_score:
            best_score, best = score, p
    if not best:
        return None
    return {
        "name":        best["project_name"],
        "area":        best["area"],
        "floors":      best["floors"],
        "cost":        f"₹{best['estimated_cost']:,}",
        "days":        best["duration_days"],
        "workers":     best["workers"],
        "type":        best.get("type", "Residential RCC"),
        "location":    best.get("location", "India"),
        "match_score": f"{max(0, round((1 - best_score) * 100))}%"
    }