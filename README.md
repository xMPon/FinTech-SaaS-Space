# FinTech-SaaS-Space

FinTech-SaaS-Space is a documentation-first blueprint for an AI-powered FinTech SaaS platform. The current MVP is an API-only proof of concept that runs locally with minimal setup.

**Documentation Map**
- `FINTECH_SAAS_BLUEPRINT.md` - Product vision, architecture patterns, and revenue model.
- `PROJECT_ROADMAP.md` - 12-month phased roadmap with KPIs, risks, and decision gates.
- `IMPLEMENTATION_GUIDE.md` - MVP technical approach.
- `REQUIREMENTS.md` - MVP requirements, scope, and success criteria.

**Repository Layout**
- `backend/requirements.txt` - Python backend dependencies (FastAPI, SQLAlchemy).
- `backend/app/` - API source code.

**Status**
- MVP API is implemented for local use (no authentication, API-only).

**Quickstart (Local)**
1. Create and activate a virtual environment.
2. Set an admin token (PowerShell): ``$env:FTSAAS_ADMIN_TOKEN="dev-token"``
3. Install dependencies: `pip install -r backend/requirements.txt`
4. Run the API: `uvicorn backend.app.main:app --reload`
5. Open `http://127.0.0.1:8000/docs` for Swagger UI.

**Example Request**
```bash
curl -H "X-Admin-Token: dev-token" http://127.0.0.1:8000/accounts
```

**Security Note**
- The MVP uses a static admin token and is intended for local use only.
- Add full authentication, rate limiting, and HTTPS before any public deployment.

**How To Use This Repo**
1. Start with `FINTECH_SAAS_BLUEPRINT.md` to align on vision and architecture.
2. Review `PROJECT_ROADMAP.md` to plan delivery phases and resourcing.
3. Use `IMPLEMENTATION_GUIDE.md` and `REQUIREMENTS.md` to guide implementation.
