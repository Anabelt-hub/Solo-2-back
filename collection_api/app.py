from flask import Flask, request, jsonify
from flask_cors import CORS
import json, os, uuid

app = Flask(__name__)

# Allow your Netlify site to call this API
# For now allow all origins; later you can lock it to https://collection2.netlify.app
CORS(app)

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "records.json")

ALLOWED_TYPES = {"Movie", "Show", "Anime", "Book", "Game"}
ALLOWED_STATUSES = {"Planned", "Watching", "Completed", "Dropped"}

def read_records():
    if not os.path.exists(DATA_FILE):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        # Seed 30 records if file doesn't exist
        seed = []
        for i in range(30):
            seed.append({
                "id": str(uuid.uuid4()),
                "title": f"Seed Title {i+1}",
                "type": "Movie",
                "genre": "Drama",
                "year": 2000 + (i % 20),
                "rating": None,
                "status": "Planned",
                "notes": ""
            })
        write_records(seed)

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def write_records(records):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

def validate_record(data, is_update=False):
    # basic server-side validation
    title = (data.get("title") or "").strip()
    if not title:
        return "Title is required."

    rtype = data.get("type")
    if not rtype:
        return "Type is required."
    # If you want to enforce allowed types, uncomment:
    # if rtype not in ALLOWED_TYPES: return "Invalid type."

    genre = (data.get("genre") or "").strip()
    if not genre:
        return "Genre is required."

    try:
        year = int(data.get("year"))
    except Exception:
        return "Year must be a whole number."
    if year < 1900 or year > 2100:
        return "Year must be between 1900 and 2100."

    status = data.get("status")
    if not status:
        return "Status is required."
    # If enforcing allowed statuses:
    # if status not in ALLOWED_STATUSES: return "Invalid status."

    rating = data.get("rating", None)
    if rating is not None:
        try:
            rating = int(rating)
        except Exception:
            return "Rating must be a whole number."
        if rating < 1 or rating > 10:
            return "Rating must be between 1 and 10."

    return None

@app.get("/api/records")
def get_records():
    records = read_records()
    return jsonify(records)

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
        "type": data.get("type"),
        "genre": (data.get("genre") or "").strip(),
        "year": int(data.get("year")),
        "rating": data.get("rating", None),
        "status": data.get("status"),
        "notes": (data.get("notes") or "").strip()
    }
    records.insert(0, new_rec)  # newest-first
    write_records(records)
    return jsonify(new_rec), 201

@app.put("/api/records/<rid>")
def update_record(rid):
    data = request.get_json(force=True) or {}
    err = validate_record(data, is_update=True)
    if err:
        return jsonify({"error": err}), 400

    records = read_records()
    found = False
    for r in records:
        if r["id"] == rid:
            r["title"] = (data.get("title") or "").strip()
            r["type"] = data.get("type")
            r["genre"] = (data.get("genre") or "").strip()
            r["year"] = int(data.get("year"))
            r["rating"] = data.get("rating", None)
            r["status"] = data.get("status")
            r["notes"] = (data.get("notes") or "").strip()
            found = True
            break

    if not found:
        return jsonify({"error": "Record not found."}), 404

    write_records(records)
    return jsonify({"ok": True})

@app.delete("/api/records/<rid>")
def delete_record(rid):
    records = read_records()
    new_records = [r for r in records if r["id"] != rid]
    if len(new_records) == len(records):
        return jsonify({"error": "Record not found."}), 404
    write_records(new_records)
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
