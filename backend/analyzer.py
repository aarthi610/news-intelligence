import os, json
from dotenv import load_dotenv
load_dotenv()
from groq import Groq
from database import SessionLocal, Article, AIAnalysis

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

PROMPT_TEMPLATE = """Analyze this news article and respond ONLY with valid JSON.

Title: {title}
Content: {content}

Return exactly this JSON structure:
{{
  "summary": "1-2 sentence summary",
  "sentiment": "positive" | "negative" | "neutral",
  "insights": ["insight 1", "insight 2", "insight 3", "insight 4", "insight 5"]
}}"""

def analyze_article(title: str, content: str) -> dict:
    text = content or title
    prompt = PROMPT_TEMPLATE.format(title=title, content=text[:2000])

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
        temperature=0.3,
    )
    raw = response.choices[0].message.content.strip()

    # Strip markdown fences if present
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def analyze_unprocessed(limit=20):
    db = SessionLocal()
    analyzed_ids = {r.article_id for r in db.query(AIAnalysis.article_id).all()}

    articles = (db.query(Article)
                  .filter(~Article.article_id.in_(analyzed_ids))
                  .order_by(Article.published_at.desc())
                  .limit(limit).all())

    for art in articles:
        try:
            result = analyze_article(art.title, art.content or art.description)
            ai = AIAnalysis(
                article_id = art.article_id,
                summary    = result.get("summary", ""),
                sentiment  = result.get("sentiment", "neutral"),
                insights   = result.get("insights", []),
            )
            db.add(ai)
            db.commit()
            print(f"✓ Analyzed: {art.title[:60]}")
        except Exception as e:
            print(f"✗ Failed: {art.title[:50]} — {e}")
            db.rollback()

    db.close()
