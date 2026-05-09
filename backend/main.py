from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db, Article, AIAnalysis
from fetcher import fetch_and_store
from analyzer import analyze_unprocessed

app = FastAPI(title="News Intelligence API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/api/articles")
def get_articles(
    page: int = 1, limit: int = 12,
    sentiment: str = None, category: str = None,
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit
    query = (db.query(Article, AIAnalysis)
               .outerjoin(AIAnalysis, Article.article_id == AIAnalysis.article_id))

    if sentiment:
        query = query.filter(AIAnalysis.sentiment == sentiment)
    if category:
        query = query.filter(Article.category.ilike(f"%{category}%"))

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

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(Article.id)).scalar()
    analyzed = db.query(func.count(AIAnalysis.id)).scalar()
    sentiment_counts = dict(db.query(AIAnalysis.sentiment, func.count())
                              .group_by(AIAnalysis.sentiment).all())
    return {"total_articles": total, "analyzed": analyzed,
            "sentiment_breakdown": sentiment_counts}

@app.post("/api/pipeline/run")
def run_pipeline(query: str = Query(default="technology")):
    fetched = fetch_and_store(query=query, pages=3)
    analyze_unprocessed(limit=fetched or 20)
    return {"status": "done", "fetched": fetched}