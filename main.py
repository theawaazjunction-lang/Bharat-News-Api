from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
import os
import json
from fetch_news import get_all_news
from process_data_india import process_and_push_to_db
from fastapi.responses import FileResponse

app = FastAPI(title="Bharat News API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("favicon.ico")

@app.get("/")
async def root():
    return {"message": "Bharat News API is live. Go to '/api/news' or '/api/news/state_code'."}

@app.get("/api/news")
async def get_news():
    if not os.path.exists(DATA_FILE):
        raise HTTPException(status_code=404, detail="No data yet.")
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

@app.get("/api/news/{state_code}")
async def get_news_by_state(state_code: str):
    if not os.path.exists(DATA_FILE):
        raise HTTPException(status_code=404, detail="No data yet.")
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        records = json.load(f)
    for record in records:
        if str(record.get("Code", "")).upper() == state_code.upper():
            return record
    raise HTTPException(status_code=404, detail=f"No news for: {state_code.upper()}")

@app.get("/api/health")
async def health_check():
    if not os.path.exists(DATA_FILE):
        return {"status": "empty", "last_updated": None}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        records = json.load(f)
    if not records:
        return {"status": "empty", "last_updated": None}
    return {"status": "healthy", "last_updated": records[0].get("last_updated")}
