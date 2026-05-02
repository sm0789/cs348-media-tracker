from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
import uvicorn
from database import get_db, init_db

app = FastAPI(title="CS348 Media Tracker")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# HOME
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    db = get_db()
    items = db.execute("SELECT * FROM MediaItems ORDER BY title").fetchall()
    db.close()
    return templates.TemplateResponse(request, "index.html", {"items": items})

# ADD MEDIA ITEM (GET form)
@app.get("/items/add", response_class=HTMLResponse)
def add_item_form(request: Request):
    return templates.TemplateResponse(request, "item_form.html", {
        "item": None,
        "action": "Add"
    })

# ADD MEDIA ITEM (POST)
@app.post("/items/add")
def add_item(
    title:        str = Form(...),
    type:         str = Form(...),
    genre:        str = Form(...),
    release_year: int = Form(...),
    description:  str = Form("")
):
    db = get_db()
    try:
        db.execute("BEGIN")
        db.execute(
            "INSERT INTO MediaItems (title, type, genre, release_year, description) VALUES (?, ?, ?, ?, ?)",
            (title, type, genre, release_year, description)
        )
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Transaction failed: {e}")
    finally:
        db.close()
    return RedirectResponse("/", status_code=303)

# EDIT MEDIA ITEM (GET form)
@app.get("/items/{item_id}/edit", response_class=HTMLResponse)
def edit_item_form(request: Request, item_id: int):
    db = get_db()
    item = db.execute("SELECT * FROM MediaItems WHERE item_id = ?", (item_id,)).fetchone()
    db.close()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return templates.TemplateResponse(request, "item_form.html", {
        "item": item,
        "action": "Edit"
    })

# EDIT MEDIA ITEM (POST)
@app.post("/items/{item_id}/edit")
def edit_item(
    item_id:      int,
    title:        str = Form(...),
    type:         str = Form(...),
    genre:        str = Form(...),
    release_year: int = Form(...),
    description:  str = Form("")
):
    db = get_db()
    try:
        db.execute("BEGIN")
        db.execute(
            "UPDATE MediaItems SET title=?, type=?, genre=?, release_year=?, description=? WHERE item_id=?",
            (title, type, genre, release_year, description, item_id)
        )
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Transaction failed: {e}")
    finally:
        db.close()
    return RedirectResponse("/", status_code=303)

# DELETE MEDIA ITEM (POST)
@app.post("/items/{item_id}/delete")
def delete_item(item_id: int):
    db = get_db()
    try:
        db.execute("BEGIN")
        db.execute("DELETE FROM MediaItems WHERE item_id = ?", (item_id,))
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Transaction failed: {e}")
    finally:
        db.close()
    return RedirectResponse("/", status_code=303)

# REPORT
# Dynamic dropdowns built from DB queries
@app.get("/report", response_class=HTMLResponse)
def report(
    request:    Request,
    type:       Optional[str] = None,
    genre:      Optional[str] = None,
    year_min:   Optional[str] = None,
    year_max:   Optional[str] = None,
    status:     Optional[str] = None,
    rating_min: Optional[str] = None,
    rating_max: Optional[str] = None,
):
    db = get_db()

    year_min_v   = int(year_min)     if year_min   and year_min.strip()   else None
    year_max_v   = int(year_max)     if year_max   and year_max.strip()   else None
    rating_min_v = float(rating_min) if rating_min and rating_min.strip() else None
    rating_max_v = float(rating_max) if rating_max and rating_max.strip() else None

    genres = [r["genre"] for r in db.execute(
        "SELECT DISTINCT genre FROM MediaItems ORDER BY genre"
    ).fetchall()]
    types = [r["type"] for r in db.execute(
        "SELECT DISTINCT type FROM MediaItems ORDER BY type"
    ).fetchall()]

    query = """
        SELECT
            m.item_id, m.title, m.type, m.genre, m.release_year,
            COUNT(l.log_id)                                        AS log_count,
            ROUND(AVG(l.rating), 2)                                AS avg_rating,
            SUM(CASE WHEN l.status='Completed' THEN 1 ELSE 0 END)  AS completed_count,
            SUM(CASE WHEN l.status='Want'      THEN 1 ELSE 0 END)  AS want_count,
            SUM(CASE WHEN l.status='Watching'  THEN 1 ELSE 0 END)  AS watching_count,
            SUM(CASE WHEN l.status='Dropped'   THEN 1 ELSE 0 END)  AS dropped_count
        FROM MediaItems m
        LEFT JOIN UserMediaLog l ON m.item_id = l.item_id
        WHERE 1=1
    """
    params = []

    if type:
        query += " AND m.type = ?"
        params.append(type)
    if genre:
        query += " AND m.genre = ?"
        params.append(genre)
    if year_min_v:
        query += " AND m.release_year >= ?"
        params.append(year_min_v)
    if year_max_v:
        query += " AND m.release_year <= ?"
        params.append(year_max_v)
    if status:
        query += " AND l.status = ?"
        params.append(status)
    if rating_min_v:
        query += " AND l.rating >= ?"
        params.append(rating_min_v)
    if rating_max_v:
        query += " AND l.rating <= ?"
        params.append(rating_max_v)

    query += " GROUP BY m.item_id ORDER BY avg_rating DESC"
    results = db.execute(query, params).fetchall()

    stats = {}
    if results:
        ratings = [r["avg_rating"] for r in results if r["avg_rating"] is not None]
        stats["count"]         = len(results)
        stats["avg_rating"]    = round(sum(ratings) / len(ratings), 2) if ratings else "N/A"
        stats["highest_rated"] = max(results, key=lambda r: r["avg_rating"] or 0)["title"]
        stats["total_logged"]  = sum(r["log_count"] for r in results)

    db.close()

    filters = {
        "type": type, "genre": genre,
        "year_min": year_min, "year_max": year_max,
        "status": status, "rating_min": rating_min, "rating_max": rating_max
    }

    return templates.TemplateResponse(request, "report.html", {
        "results": results, "genres": genres, "types": types,
        "filters": filters, "stats": stats
    })

if __name__ == "__main__":
    init_db()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
