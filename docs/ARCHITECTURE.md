# System Architecture — منصة تحليل المشاعر

## Overview

Multilingual sentiment analysis platform for graduation project and commercial extension.

```
[User / API Client]
        │
        ▼
┌───────────────────┐     ┌─────────────────┐
│  Streamlit UI     │     │  FastAPI REST   │
│  (app/main.py)    │     │  (src/api/)     │
└─────────┬─────────┘     └────────┬────────┘
          │                        │
          └──────────┬─────────────┘
                     ▼
          ┌──────────────────────┐
          │  Core Services (src/) │
          │  • models (TF-IDF/BERT)│
          │  • analytics           │
          │  • evaluation (LIME)   │
          │  • comment_fetcher     │
          └──────────┬─────────────┘
                     ▼
          ┌──────────────────────┐
          │  SQLite Database       │
          │  data/sentiment_       │
          │  platform.db           │
          └──────────────────────┘
```

## Database Schema (ER)

| Table | Purpose |
|-------|---------|
| `users` | Login, roles (admin / analyst / viewer) |
| `analysis_batches` | Each batch run (source, counts, avg confidence) |
| `analysis_items` | Individual comment results |
| `alerts` | Negative spikes, low confidence warnings |
| `api_keys` | Optional API authentication (future) |

**Relations:**
- `users` 1 ── * `analysis_batches`
- `analysis_batches` 1 ── * `analysis_items`
- `analysis_batches` 1 ── * `alerts`

## Data Flow (Step by Step)

1. **Input** — Single comment, CSV batch, or live fetch (YouTube / Play / Reddit)
2. **Preprocessing** — Language detection, Arabic normalization, stopwords
3. **Inference** — BERT (default) or TF-IDF + optional LIME
4. **Analytics** — Keywords, trend label, alerts
5. **Storage** — Optional save to SQLite + export PDF/Excel
6. **Dashboard** — KPIs, charts, alert history

## Security

- Passwords: PBKDF2-SHA256 (120k iterations)
- Roles: admin, analyst, viewer
- API: optional `X-API-Key` header via env `SENTIMENT_API_KEY`
- CORS enabled for integration demos

## Cloud / Scale (Recommended for Production)

| Layer | Dev (Project) | Production |
|-------|---------------|------------|
| App | Streamlit local | Docker + reverse proxy |
| API | Uvicorn | Kubernetes / Cloud Run |
| DB | SQLite | PostgreSQL |
| Models | Local files | S3 + GPU inference |
| Queue | — | Redis + Celery for 10k+ reviews |

## What Was NOT Implemented (By Design)

- OAuth / social login — out of graduation scope
- Full cloud deployment — documented only
- Real-time push notifications — UI alerts sufficient for demo
- Heavy recommendation engine — replaced with trend + keyword insights

## Demo Accounts

| Role | User | Password |
|------|------|----------|
| Admin | admin | Admin@2026 |
| Analyst | analyst | Analyst@2026 |
| Viewer | viewer | Viewer@2026 |
