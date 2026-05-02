# CS348 Media Tracker

A database-backed web application built with Python, FastAPI, Jinja2, and SQLite.

## Project Structure

```
mediatracker/
├── main.py           # FastAPI routes (all backend logic)
├── database.py       # DB connection + init_db()
├── schema.sql        # Table definitions + seed data
├── requirements.txt  # Python dependencies
├── static/
│   └── css/
│       └── style.css
└── templates/
    ├── base.html     # Shared nav/layout
    ├── index.html    # Home page — all media items (Req 1)
    ├── item_form.html# Add / Edit form (Req 1)
    └── report.html   # Filtered report with stats (Req 2)
```
