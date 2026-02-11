import os
import json
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(BASE_DIR, "data", "records.json")


# -------------------- File helpers --------------------
def ensure_data_file():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)


def write_records(records):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)


def seed_records():
    """Return >=30 real movie/TV records (watchlist domain)."""
    def rec(title, rtype, genre, year, rating, status, notes=""):
        return {
            "id": str(uuid.uuid4()),
            "title": title,
            "type": rtype,
            "genre": genre,
            "year": year,
            "rating": rating,
            "status": status,
            "notes": notes
        }

    # 35 records (mix of movies + shows)
    return [
        rec("The Dark Knight", "Movie", "Action", 2008, 9, "Completed"),
        rec("Inception", "Movie", "Sci-Fi", 2010, 9, "Completed"),
        rec("Interstellar", "Movie", "Sci-Fi", 2014, 9, "Completed"),
        rec("The Matrix", "Movie", "Sci-Fi", 1999, 9, "Completed"),
        rec("Parasite", "Movie", "Thriller", 2019, 9, "Completed"),
        rec("Get Out", "Movie", "Horror", 2017, 8, "Completed"),
        rec("The Shawshank Redemption", "Movie", "Drama", 1994, 10, "Completed"),
        rec("Pulp Fiction", "Movie", "Crime", 1994, 9, "Completed"),
        rec("Spirited Away", "Movie", "Animation", 2001, 10, "Completed"),
        rec("Avengers: Endgame", "Movie", "Action", 2019, 8, "Completed"),
        rec("Spider-Man: Into the Spider-Verse", "Movie", "Animation", 2018, 9, "Completed"),
        rec("The Lion King", "Movie", "Animation", 1994, 9, "Completed"),
        rec("Dune", "Movie", "Sci-Fi", 2021, 8, "Completed"),
        rec("Oppenheimer", "Movie", "Drama", 2023, 9, "Completed"),
        rec("Barbie", "Movie", "Comedy", 2023, 7, "Completed"),
        rec("Top Gun: Maverick", "Movie", "Action", 2022, 8, "Completed"),
        rec("The Social Network", "Movie", "Drama", 2010, 8, "Completed"),
        rec("La La Land", "Movie", "Romance", 2016, 8, "Completed"),
        rec("Knives Out", "Movie", "Mystery", 2019, 8, "Completed"),
        rec("The Grand Budapest Hotel", "Movie", "Comedy", 2014, 8, "Completed"),

        rec("Breaking Bad", "Show", "Drama", 2008, 10, "Completed"),
        rec("Better Call Saul", "Show", "Drama", 2015, 9, "Completed"),
        rec("Stranger Things", "Show", "Sci-Fi", 2016, 8, "Watching"),
        rec("The Office", "Show", "Comedy", 2005, 8, "Completed"),
        rec("Game of Thrones", "Show", "Fantasy", 2011, 7, "Completed"),
        rec("House of the Dragon", "Show", "Fantasy", 2022, 8, "Watching"),
        rec("The Mandalorian", "Show", "Sci-Fi", 2019, 8, "Watching"),
        rec("The Witcher", "Show", "Fantasy", 2019, 7, "Watching"),
        rec("Black Mirror", "Show", "Sci-Fi", 2011, 9, "Completed"),
        rec("The Boys", "Show", "Action", 2019, 8, "Watching"),
        rec("The Crown", "Show", "Drama", 2016, 8, "Planned"),
        rec("The Sopranos", "Show", "Drama", 1999, 10, "Planned"),
        rec("Narcos", "Show", "Drama", 2015, 8, "Completed"),
        rec("The Walking Dead", "Show", "Horror", 2010, 7, "Dropped"),
        rec("Chernobyl", "Show", "Drama", 2019, 10, "Completed"),
    ]


def read_records():
    """
    Read records from JSON.
    ✅ Seed ONLY if file is missing/invalid/empty (so deletes do NOT respawn records).
    """
    ensure_data_file()

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            records = json.load(f)
    except Exception:
        records = []

    if not isinstance(records, list):
        records = []

    # ✅ Seed only when empty (meets "start with >=30" without blocking deletes)
    if len(records) == 0:
        records = seed_records()
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

    try:
        year = int(data.get("year"))
    except Exception:
        return "Year must be a whole number."
    if year < 1900 or year > 2100:
        return "Year must be between 1900 and 2100."

    status = (data.get("status") or "").strip()
    if not status:
        return "Status is required."

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

    # Newest-first
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
