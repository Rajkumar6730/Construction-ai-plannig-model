# ai_modules/scheduler.py
# Generates week-by-week construction schedule based on floors and duration


def generate_weekly_schedule(floors, total_weeks):
    """
    Returns a list of dicts:
      { week: int, phase: str, activities: list[str] }
    """
    schedule = [
        {
            "week": 1,
            "phase": "Site Preparation",
            "activities": ["Site clearing", "Leveling", "Setting up temporary facilities", "Safety hoarding"]
        },
        {
            "week": 2,
            "phase": "Foundation Work",
            "activities": ["Excavation", "PCC laying", "Foundation reinforcement", "Concrete pouring & curing"]
        },
        {
            "week": 3,
            "phase": "Ground Floor Slab",
            "activities": ["Formwork preparation", "Reinforcement placement", "Concrete pouring", "Curing (7 days)"]
        },
    ]

    week = 5
    for f in range(1, floors):
        schedule.append({
            "week": week,
            "phase": f"Floor {f + 1} Slab",
            "activities": [
                "Column & beam shuttering",
                "Reinforcement placement",
                "Concrete pouring",
                "Curing (7 days)"
            ]
        })
        week += 2

    finishing_phases = [
        ("Brickwork & Masonry",         ["Brick laying", "Lintel casting", "Wall plastering prep"]),
        ("Internal Plastering",          ["Wall plastering", "Ceiling plastering", "Surface finishing"]),
        ("Electrical Works",             ["Conduit laying", "Wiring", "Switch board setup", "Safety inspection"]),
        ("Plumbing & Sanitary",          ["Pipe laying", "Bathroom fixtures", "Kitchen fittings", "Water system testing"]),
        ("Wall Painting",                ["Putty application", "Primer coat", "Base paint", "Final color coat"]),
        ("Flooring & Tiling",            ["Floor leveling", "Tile laying", "Grouting", "Polishing"]),
        ("Doors, Windows & Hardware",    ["Door frames", "Window fitting", "Hardware mounting", "Glass fitting"]),
        ("Electrical & Plumbing Fit-out",["Light fixtures", "Sanitary fittings", "Switch plates", "Final connections"]),
        ("Final Finishing & Cleanup",    ["Interior polishing", "Exterior painting", "Final inspection", "Handover"]),
    ]

    for phase, activities in finishing_phases:
        schedule.append({"week": week, "phase": phase, "activities": activities})
        week += 2

    # Only return weeks that fit within the project duration
    return [s for s in schedule if s["week"] <= max(total_weeks + 2, week)]


def generate_phase_schedule(days):
    """
    Returns percentage-based phase breakdown (used in the simple schedule table).
    """
    return [
        ("Site Preparation",       int(days * 0.05)),
        ("Foundation",             int(days * 0.15)),
        ("Structure & Pillars",    int(days * 0.25)),
        ("Slab Work",              int(days * 0.20)),
        ("Brickwork & Plaster",    int(days * 0.15)),
        ("Electrical & Plumbing",  int(days * 0.10)),
        ("Finishing & Handover",   int(days * 0.10)),
    ]