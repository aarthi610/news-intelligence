from fastapi import FastAPI, Depends, Query, BackgroundTasks  # ← add BackgroundTasks here
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db, Article, AIAnalysis, Bookmark, Base, engine
from fetcher import fetch_and_store
from analyzer import analyze_unprocessed

Base.metadata.create_all(bind=engine)

app = FastAPI(title="News Intelligence API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# ── Articles ─────────────────────────────────────────────────────────────────

@app.get("/api/articles")
def get_articles(
    page: int = 1, limit: int = 12,
    sentiment: str = None, category: str = None, search: str = None,
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit
    query = (db.query(Article, AIAnalysis)
               .outerjoin(AIAnalysis, Article.article_id == AIAnalysis.article_id))
    if sentiment:
        query = query.filter(AIAnalysis.sentiment == sentiment)
    if category:
        query = query.filter(Article.category.ilike(f"%{category}%"))
    if search:
        term = f"%{search}%"
        query = query.filter(
            Article.title.ilike(term) |
            Article.description.ilike(term) |
            Article.source.ilike(term)
        )
    total = query.count()
    rows  = query.order_by(Article.published_at.desc()).offset(offset).limit(limit).all()
    articles = []
    for art, ai in rows:
        articles.append({
            "id": art.article_id, "title": art.title,
            "description": art.description, "url": art.url,
            "image_url": art.image_url, "source": art.source,
            "category": art.category, "published_at": str(art.published_at),
            "summary": ai.summary if ai else None,
            "sentiment": ai.sentiment if ai else None,
            "insights": ai.insights if ai else [],
        })
    return {"articles": articles, "total": total, "page": page}


# ── Stats ─────────────────────────────────────────────────────────────────────

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    total    = db.query(func.count(Article.id)).scalar()
    analyzed = db.query(func.count(AIAnalysis.id)).scalar()
    sentiment_counts = dict(
        db.query(AIAnalysis.sentiment, func.count())
          .group_by(AIAnalysis.sentiment).all()
    )
    bookmarks = db.query(func.count(Bookmark.id)).scalar()
    return {
        "total_articles": total,
        "analyzed": analyzed,
        "sentiment_breakdown": sentiment_counts,
        "bookmarks": bookmarks,
    }


# ── Pipeline background task ──────────────────────────────────────────────────

def run_pipeline_task(query: str):                          # ← NEW helper function
    fetched = fetch_and_store(query=query, pages=3)
    analyze_unprocessed(limit=fetched or 20)
    print(f"✓ Pipeline complete: {fetched} articles")


@app.post("/api/pipeline/run")
def run_pipeline(
    background_tasks: BackgroundTasks,
    query: str = Query(default="technology")   # ← simple single word
):
    background_tasks.add_task(run_pipeline_task, query)
    return {"status": "started", "message": "Pipeline running in background"}


# ── Bookmarks ─────────────────────────────────────────────────────────────────

@app.get("/api/bookmarks")
def get_bookmarks(db: Session = Depends(get_db)):
    rows = (
        db.query(Article, AIAnalysis)
          .join(Bookmark, Bookmark.article_id == Article.article_id)
          .outerjoin(AIAnalysis, AIAnalysis.article_id == Article.article_id)
          .order_by(Bookmark.saved_at.desc())
          .all()
    )
    return {
        "bookmarks": [
            {
                "id": art.article_id, "title": art.title,
                "description": art.description, "url": art.url,
                "image_url": art.image_url, "source": art.source,
                "category": art.category, "published_at": str(art.published_at),
                "summary": ai.summary if ai else None,
                "sentiment": ai.sentiment if ai else None,
                "insights": ai.insights if ai else [],
            }
            for art, ai in rows
        ]
    }


@app.post("/api/bookmarks/{article_id}")
def add_bookmark(article_id: str, db: Session = Depends(get_db)):
    exists = db.query(Bookmark).filter_by(article_id=article_id).first()
    if exists:
        return {"status": "already_bookmarked", "article_id": article_id}
    article = db.query(Article).filter_by(article_id=article_id).first()
    if not article:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Article not found")
    db.add(Bookmark(article_id=article_id))
    db.commit()
    return {"status": "bookmarked", "article_id": article_id}


@app.delete("/api/bookmarks/{article_id}")
def remove_bookmark(article_id: str, db: Session = Depends(get_db)):
    bookmark = db.query(Bookmark).filter_by(article_id=article_id).first()
    if not bookmark:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Bookmark not found")
    db.delete(bookmark)
    db.commit()
    return {"status": "removed", "article_id": article_id}


# ── Frontend ──────────────────────────────────────────────────────────────────

from fastapi.staticfiles import StaticFiles
import os
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")