CATEGORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "categories.json")

@app.get("/api/news/category/{category}")
async def get_news_by_category(category: str):
    if not os.path.exists(CATEGORY_FILE):
        raise HTTPException(status_code=404, detail="No category data yet.")
    with open(CATEGORY_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    key = category.lower()
    if key not in data:
        raise HTTPException(status_code=404, detail=f"Unknown category: {category}")
    return {"category": key, "last_updated": data.get("last_updated"), "articles": data[key]}
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
