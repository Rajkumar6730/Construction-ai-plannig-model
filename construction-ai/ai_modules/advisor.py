# ai_modules/advisor.py
# AI-powered construction advice — Ollama/Granite → IBM watsonx → rule-based fallback

import requests
import os

OLLAMA_URL = "http://localhost:11434/api/generate"
GRANITE_MODEL = "granite3.3:2b"


def get_advice(area, floors, workers, days, cement, steel, cost):
    """
    Returns a list of 3 practical recommendations.
    Priority: Ollama (Granite 3.3 2B) → IBM watsonx → rule-based
    """
    prompt = f"""You are a professional construction project manager in India.
A construction project has the following parameters:
- Area: {area} sq yards, Floors: {floors}
- Workers: {workers}, Timeline: {days} days
- Cement: {cement} bags, Steel: {steel} kg
- Estimated Cost: ₹{cost:,.0f}

Give exactly 3 short, practical recommendations to improve efficiency and reduce risk.
Each on a new line starting with a dash. Be specific."""

    # 1. Try Ollama / Granite 3.3 2B
    try:
        resp = requests.post(
            OLLAMA_URL,
            json={
                "model": GRANITE_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.7, "num_predict": 250}
            },
            timeout=25
        )
        if resp.status_code == 200:
            text = resp.json().get("response", "").strip()
            if text:
                lines = [l.strip("•-– 1234567890.) ").strip()
                         for l in text.split("\n") if l.strip()]
                lines = [l for l in lines if len(l) > 20]
                if lines:
                    return lines[:3]
    except Exception:
        pass

    # 2. Try IBM watsonx
    try:
        api_key  = os.getenv("IBM_API_KEY")
        endpoint = os.getenv("IBM_API_URL")
        if api_key and endpoint:
            resp = requests.post(
                endpoint,
                headers={"Authorization": f"Bearer {api_key}",
                         "Content-Type": "application/json"},
                json={"input": prompt},
                timeout=10
            )
            if resp.status_code == 200:
                text = str(resp.json().get("results", ""))
                if text:
                    return [text[:300]]
    except Exception:
        pass

    # 3. Rule-based fallback
    advice = []
    if workers < 20:
        advice.append("Increase workforce to at least 20 workers to maintain schedule momentum and avoid delays.")
    if cement > 2000:
        advice.append("Negotiate bulk cement purchasing to reduce material costs by 8–12% and ensure steady supply.")
    if floors > 2:
        advice.append("Multi-floor buildings require RCC structural audits at each slab stage — don't skip curing periods.")
    if days < 60:
        advice.append("Tight timeline — run foundation work and material procurement in parallel to save 1–2 weeks.")
    if not advice:
        advice.append("Maintain a 10% material buffer stock on-site to avoid supply chain delays mid-project.")
        advice.append("Schedule weekly supervisor reviews to track milestone completion and catch issues early.")
        advice.append("Ensure all concrete curing periods are respected to achieve full design strength before loading.")
    return advice[:3]


def get_risk_score(workers, days, floors, cement):
    """Returns (score: int, risk: str)"""
    score = 100
    if workers < 20: score -= 15
    if days < 60:    score -= 20
    if floors > 3:   score -= 10
    if cement > 3000: score -= 10
    risk = "Low" if score > 80 else ("Medium" if score > 60 else "High")
    return score, risk