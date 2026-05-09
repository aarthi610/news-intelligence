import httpx, os, hashlib
from datetime import datetime
from dotenv import load_dotenv  # ADD THIS
from database import SessionLocal, Article

load_dotenv()  # ADD THIS
API_KEY = os.getenv("NEWSDATA_API_KEY")
BASE_URL = "https://newsdata.io/api/1/news"

def fetch_and_store(query="technology", language="en", pages=3):
    db = SessionLocal()
    next_page = None
    stored = 0

    for _ in range(pages):
        params = {"apikey": API_KEY, "q": query, "language": language, "size": 10,"timeframe": 6}
        if next_page:
            params["page"] = next_page

        try:
            res = httpx.get(BASE_URL, params=params, timeout=15)
            res.raise_for_status()
            data = res.json()
        except Exception as e:
            print(f"Fetch error: {e}")
            break

        for item in data.get("results", []):
            # Deduplicate by article_id
            art_id = item.get("article_id") or hashlib.md5(
                item.get("title","").encode()).hexdigest()

            if db.query(Article).filter_by(article_id=art_id).first():
                continue  # skip duplicate

            # Clean & validate
            title = (item.get("title") or "").strip()
            if not title:
                continue

            article = Article(
                article_id   = art_id,
                title        = title,
                description  = (item.get("description") or "").strip(),
                content      = (item.get("content") or "").strip(),
                source       = item.get("source_id"),
                author       = ", ".join(item.get("creator") or []),
                url          = item.get("link"),
                image_url    = item.get("image_url"),
                category     = ", ".join(item.get("category") or []),
                language     = item.get("language"),
                country      = ", ".join(item.get("country") or []),
                published_at = datetime.fromisoformat(item["pubDate"])
                               if item.get("pubDate") else None,
            )
            db.add(article)
            stored += 1

        db.commit()
        next_page = data.get("nextPage")
        if not next_page:
            break

    db.close()
    print(f"Stored {stored} new articles")
    return stored