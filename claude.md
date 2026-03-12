# FinTech-SaaS-Space Agent Guide

This file orients agents working in this repository. It reflects the current MVP API state of the project.

## Project Summary
- FinTech-SaaS-Space is a blueprint for an AI-powered FinTech SaaS platform.
- The current MVP is an API-only, local-first proof of concept with no authentication.

## Source Of Truth
- Use `FINTECH_SAAS_BLUEPRINT.md` for vision, architecture patterns, and revenue model.
- Use `PROJECT_ROADMAP.md` for timelines, phases, KPIs, and risks.
- Use `IMPLEMENTATION_GUIDE.md` for the planned technical approach.
- Use `REQUIREMENTS.md` for MVP scope and constraints.
- `backend/requirements.txt` is the dependency list for the Python backend.

## Guardrails
- Keep the MVP local-first and simple (static admin token, no multi-tenant features).
- Keep instructions aligned with the Python stack implied by `backend/requirements.txt`.
- Avoid adding vendor-specific details unless explicitly requested.
- Use concrete dates when referencing timelines.
- Do not declare the project public-ready without full authentication and rate limiting.

## Documentation Maintenance
- Remove placeholder or duplicate docs rather than expanding them.
- Keep docs concise and consistent across files.
- When updating the roadmap, preserve decision gates and success metrics.

## When Implementing Code
- Add a clear app entrypoint under `backend/` (for example `backend/app/main.py`).
- Keep configuration in `.env` and document required keys.
- Add tests before introducing complex features like payments or ML pipelines.

## Agent Roles
- Backend Agent: Owns API endpoints, data access, and business rules.
- Data Agent: Owns schema changes, migrations, and reporting logic.
- QA Agent: Owns tests, smoke checks, and regression coverage.
- Security Agent: Owns hardening checks before any public deployment.
