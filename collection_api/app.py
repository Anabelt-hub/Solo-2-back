import os
import json
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Allow Netlify (and other origins) to call your API
# Later you can lock this down to only your Netlify site.
CORS(app)

BASE_DIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(BASE_DIR, "data", "records.json")


# -------------------- File helpers --------------------
def ensure_data_file():
    """Ensure data directory + records.json exist."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)


def write_records(records):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)


def seed_records(n=30):
    """Create N starter watchlist records."""
    seed = []
    genres = ["Action", "Drama", "Comedy", "Sci-Fi", "Horror", "Fantasy"]
    types = ["Movie", "Show", "Anime", "Book", "Game"]
    statuses = ["Planned", "Watching", "Completed", "Dropped"]

    for i in range(n):
        seed.append({
            "id": str(uuid.uuid4()),
            "title": f"Seed Title {i + 1}",
            "type": types[i % len(types)],
            "genre": genres[i % len(genres)],
            "year": 2000 + (i % 20),
            "rating": None,
            "status": statuses[i % len(statuses)],
            "notes": ""
        })
    return seed


def read_records():
    """
    Read records from JSON.
    ✅ If missing/invalid/empty/<30: seed to 30 and persist.
    """
    ensure_data_file()

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            records = json.load(f)
    except Exception:
        records = []

    if not isinstance(records, list):
        records = []

    # ✅ Assignment requirement: start with at least 30 records
    if len(records) < 30:
        records = seed_records(30)
        write_records(records)

    return records


# -------------------- Validation --------------------
def validate_record(data):
    title = (data.get("title") or "").strip()
    if not title:
        return "Title is required."

    rtype = (data.get("type") or "").strip()
    if not rtype:
        return "Type is required."

    genre = (data.get("genre") or "").strip()
    if not genre:
        return "Genre is required."

    # Year
    try:
        year = int(data.get("year"))
    except Exception:
        return "Year must be a whole number."
    if year < 1900 or year > 2100:
        return "Year must be between 1900 and 2100."

    status = (data.get("status") or "").strip()
    if not status:
        return "Status is required."

    # Rating (optional)
    rating = data.get("rating", None)
    if rating is not None:
        try:
            rating = int(rating)
        except Exception:
            return "Rating must be a whole number."
        if rating < 1 or rating > 10:
            return "Rating must be between 1 and 10."

    return None


# -------------------- Routes --------------------
@app.get("/")
def home():
    return "Solo Project 2 API is running. Try /api/records", 200


@app.get("/api/records")
def get_records():
    records = read_records()
    return jsonify(records), 200


@app.post("/api/records")
def create_record():
    data = request.get_json(force=True) or {}
    err = validate_record(data)
    if err:
        return jsonify({"error": err}), 400

    records = read_records()

    new_rec = {
        "id": str(uuid.uuid4()),
        "title": (data.get("title") or "").strip(),
        "type": (data.get("type") or "").strip(),
        "genre": (data.get("genre") or "").strip(),
        "year": int(data.get("year")),
        "rating": data.get("rating", None),
        "status": (data.get("status") or "").strip(),
        "notes": (data.get("notes") or "").strip(),
    }

    # Insert at top (newest-first)
    records.insert(0, new_rec)
    write_records(records)
    return jsonify(new_rec), 201


@app.put("/api/records/<rid>")
def update_record(rid):
    data = request.get_json(force=True) or {}
    err = validate_record(data)
    if err:
        return jsonify({"error": err}), 400

    records = read_records()
    for r in records:
        if r.get("id") == rid:
            r["title"] = (data.get("title") or "").strip()
            r["type"] = (data.get("type") or "").strip()
            r["genre"] = (data.get("genre") or "").strip()
            r["year"] = int(data.get("year"))
            r["rating"] = data.get("rating", None)
            r["status"] = (data.get("status") or "").strip()
            r["notes"] = (data.get("notes") or "").strip()

            write_records(records)
            return jsonify({"ok": True}), 200

    return jsonify({"error": "Record not found."}), 404


@app.delete("/api/records/<rid>")
def delete_record(rid):
    records = read_records()
    new_records = [r for r in records if r.get("id") != rid]

    if len(new_records) == len(records):
        return jsonify({"error": "Record not found."}), 404

    write_records(new_records)
    return jsonify({"ok": True}), 200


# -------------------- Run locally / Render --------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
