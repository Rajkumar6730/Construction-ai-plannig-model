from ai_modules.estimator import find_similar_project
from ai_modules.advisor   import get_advice, get_risk_score
from ai_modules.scheduler import generate_weekly_schedule, generate_phase_schedule
from flask import Flask, render_template, request, jsonify
import math, time

app = Flask(__name__)

print("=" * 60)
print("🏗️  Construction Planning System")
print("🤖 Model: granite3.3:2b")
print("🔌 Running locally via Ollama")
print("=" * 60)

# ── Blueprint helper ──────────────────────────────────────
def generate_blueprint(area, floors):
    scale = math.sqrt(area / 100)
    bp = []
    for i in range(floors):
        bp.append({
            "floor_name": "GROUND FLOOR" if i == 0 else f"FLOOR {i+1}",
            "rooms": [
                {"name":"MASTER BEDROOM","label":"Bed 1","dim":f"{round(10.7*scale,1)}' × {round(11.8*scale,1)}'"},
                {"name":"BEDROOM 2",     "label":"Bed 2","dim":f"{round(10.0*scale,1)}' × {round(11.0*scale,1)}'"},
                {"name":"LIVING ROOM",   "label":"Hall", "dim":f"{round(13.0*scale,1)}' × {round(11.0*scale,1)}'"},
                {"name":"KITCHEN",       "label":"KT",   "dim":f"{round(6.8*scale,1)}' × {round(12.0*scale,1)}'"},
                {"name":"BATHROOM",      "label":"WC",   "dim":f"{round(6.2*scale,1)}' × {round(9.5*scale,1)}'"},
                {"name":"BALCONY",       "label":"Bal",  "dim":f"{round(8.2*scale,1)}' × {round(6.5*scale,1)}'"},
            ],
            "total_area": f"{area} Sq. Yards | Scale: 1/100"
        })
    return bp

# ── Worker breakdown ──────────────────────────────────────
def worker_breakdown(total):
    return {
        "total":         total,
        "masons":        max(1, int(total * 0.30)),
        "helpers":       max(1, int(total * 0.35)),
        "steel_workers": max(1, int(total * 0.15)),
        "carpenters":    max(1, int(total * 0.10)),
        "supervisors":   max(1, int(total * 0.10)),
    }

# ── Routes ────────────────────────────────────────────────
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate():
    area   = float(request.form["area"])
    floors = int(request.form["floors"])
    days   = int(request.form["days"])
    wage   = float(request.form["wage"])

    total_workers = max(5, int(area * floors / 100))
    wd = worker_breakdown(total_workers)

    cement    = round(area * floors * 0.4, 2)
    steel     = round(area * floors * 0.2, 2)
    sand_tons = round(area * floors * 0.6, 1)
    water_l   = int(area * floors * 500)

    material_cost = area * floors * 1500
    labor_cost    = total_workers * wage * days
    overhead      = (material_cost + labor_cost) * 0.1
    cost          = material_cost + labor_cost + overhead

    weeks  = math.ceil(days / 7)
    months = round(days / 30, 1)

    advice               = get_advice(area, floors, total_workers, days, cement, steel, cost)
    score, risk          = get_risk_score(total_workers, days, floors, cement)
    schedule_phases      = generate_phase_schedule(days)
    weekly_schedule      = generate_weekly_schedule(floors, weeks)
    blueprint            = generate_blueprint(area, floors)
    similar_project      = find_similar_project(area, floors)

    return render_template("results.html",
        area=area, floors=floors, days=days, wage=wage,
        workers=total_workers,
        masons=wd["masons"], helpers=wd["helpers"],
        steel_workers=wd["steel_workers"],
        carpenters=wd["carpenters"], supervisors=wd["supervisors"],
        cement=cement, steel=steel,
        sand_tons=sand_tons, water_liters=f"{water_l:,}",
        cost=cost, material_cost=material_cost,
        labor_cost=labor_cost, overhead=overhead,
        cost_per_sq_yard=round(cost / area),
        weeks=weeks, months=months,
        schedule=schedule_phases,
        weekly_schedule=weekly_schedule,
        blueprint=blueprint,
        advice=advice,
        score=score, risk=risk,
        similar_project=similar_project,
        assumptions={
            "Location":       "India",
            "Building Type":  "Residential RCC",
            "Daily Wage":     f"₹{wage}/day",
            "Cost/Sq. Yard":  "₹1500",
            "Overhead":       "10%",
            "Built-up Area":  f"{area} Sq. Yards",
            "Total Floors":   str(floors),
        }
    )

@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    data   = request.get_json()
    area   = float(data["area"])
    floors = int(data["floors"])
    days   = int(data["days"])
    wage   = float(data["wage"])

    total_workers = max(5, int(area * floors / 100))
    wd = worker_breakdown(total_workers)

    cement        = round(area * floors * 0.4, 2)
    steel         = round(area * floors * 0.2, 2)
    material_cost = area * floors * 1500
    labor_cost    = total_workers * wage * days
    overhead      = (material_cost + labor_cost) * 0.1
    cost          = material_cost + labor_cost + overhead
    weeks         = math.ceil(days / 7)

    score, risk  = get_risk_score(total_workers, days, floors, cement)
    advice       = get_advice(area, floors, total_workers, days, cement, steel, cost)

    return jsonify({
        "workers":          wd,
        "cement":           cement,
        "steel":            steel,
        "total_cost":       round(cost),
        "material_cost":    round(material_cost),
        "labor_cost":       round(labor_cost),
        "overhead":         round(overhead),
        "cost_per_sq_yard": round(cost / area),
        "timeline":         {"days": days, "weeks": weeks, "months": round(days/30, 1)},
        "schedule":         generate_phase_schedule(days),
        "weekly_schedule":  generate_weekly_schedule(floors, weeks),
        "blueprint":        generate_blueprint(area, floors),
        "efficiency_score": score,
        "risk_level":       risk,
        "advice":           advice,
        "similar_project":  find_similar_project(area, floors)
    })

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

@app.route("/api/chat", methods=["POST"])
def api_chat():
    """Simple chatbot endpoint — Granite via Ollama."""
    import requests as req
    msg = request.get_json().get("message", "")
    prompt = f"""You are BuildAI Pro, an expert AI construction planning assistant for India.
Answer this construction question helpfully and concisely (2-4 sentences):
{msg}"""
    try:
        resp = req.post(
            "http://localhost:11434/api/generate",
            json={"model":"granite3.3:2b","prompt":prompt,"stream":False,
                  "options":{"temperature":0.7,"num_predict":200}},
            timeout=25
        )
        if resp.status_code == 200:
            return jsonify({"reply": resp.json().get("response","").strip()})
    except Exception:
        pass
    return jsonify({"reply": "I'm your construction planning assistant. Please ask about costs, materials, timelines, or workforce planning!"})

@app.route("/health")
def health():
    return jsonify({"status":"healthy","system":"Construction Planning System","timestamp":time.time()})

if __name__ == "__main__":
    print("🚀 Running at http://localhost:5000")
    app.run(debug=True)