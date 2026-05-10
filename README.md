# News Intelligence

AI-powered news aggregation and sentiment analysis platform built with FastAPI, PostgreSQL, Groq AI, and a modern frontend.

---

# Features

* Fetches latest news articles using NewsData.io
* AI-generated summaries and insights using Groq
* Sentiment analysis (Positive / Negative / Neutral)
* Bookmark articles
* Search and filter functionality
* Responsive modern UI
* FastAPI backend with PostgreSQL database

---

# Tech Stack

## Backend

* FastAPI
* SQLAlchemy
* PostgreSQL
* Groq API
* NewsData API

## Frontend

* HTML
* CSS
* Vanilla JavaScript

---

# Project Structure

```text
backend/
│
├── frontend/
│   └── index.html
│
├── analyzer.py
├── database.py
├── fetcher.py
├── main.py
├── requirements.txt
└── runtime.txt
```

---

# Quick Setup (Under 5 Minutes)

## 1. Clone Repository

```bash
git clone https://github.com/aarthi610/news-intelligence.git
cd news-intelligence/backend
```

---

# 2. Create Virtual Environment

## Windows

```bash
python -m venv venv
venv\Scripts\activate
```

## Mac/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

# 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 4. Create .env File

Create a `.env` file inside `backend/`

```env
DATABASE_URL=postgresql://username:password@localhost:5432/news_intelligence_db
NEWSDATA_API_KEY=your_newsdata_api_key
GROQ_API_KEY=your_groq_api_key
```

---

# 5. Get API Keys

## NewsData API

1. Visit:

[https://newsdata.io](https://newsdata.io)

2. Create a free account
3. Copy your API key

---

## Groq API

1. Visit:

[https://console.groq.com](https://console.groq.com)

2. Create API key
3. Copy the key

---

# 6. Start PostgreSQL

Make sure PostgreSQL is running locally.

Create a database named:

```text
news_intelligence_db
```

---

# 7. Run the Application

```bash
uvicorn main:app --reload
```

---

# 8. Open in Browser

Frontend:

```text
http://127.0.0.1:8000
```

Swagger API Docs:

```text
http://127.0.0.1:8000/docs
```

---

# First-Time Usage

1. Open the app
2. Click:

```text
Fetch & Analyze
```

3. Wait 10–30 seconds
4. Articles will appear automatically

---

# Deploy on Render

## 1. Push Code to GitHub

```bash
git add .
git commit -m "Initial deployment"
git push
```

---

## 2. Create Web Service on Render

Use these settings:

### Root Directory

```text
backend
```

### Build Command

```text
pip install -r requirements.txt
```

### Start Command

```text
uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

# Environment Variables on Render

Add:

```env
DATABASE_URL=your_render_postgres_url
NEWSDATA_API_KEY=your_newsdata_key
GROQ_API_KEY=your_groq_key
```

---

# Create PostgreSQL Database on Render

1. Render Dashboard → New → PostgreSQL
2. Copy Internal Database URL
3. Add it as `DATABASE_URL`

---

# Common Issues

## 1. 0 Articles Fetched

Cause:

* Invalid NewsData API key
* Free-tier API limit reached

Fix:

* Verify `NEWSDATA_API_KEY`
* Try query="technology"

---

## 2. Database Connection Error

Cause:

* Using localhost in production

Fix:

```python
DATABASE_URL = os.getenv("DATABASE_URL")
```

Never hardcode localhost on Render.

---

# API Endpoints

## Fetch Articles

```http
POST /api/pipeline/run
```

---

## Get Articles

```http
GET /api/articles
```

---

## Get Stats

```http
GET /api/stats
```

---

## Bookmarks

```http
GET /api/bookmarks
POST /api/bookmarks/{article_id}
DELETE /api/bookmarks/{article_id}
```


# Author

Aarthi S
