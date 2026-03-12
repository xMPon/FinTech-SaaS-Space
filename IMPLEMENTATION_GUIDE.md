# Implementation Guide

This guide describes the MVP technical approach for FinTech-SaaS-Space. The MVP is API-only, runs locally, and uses SQLite by default. A static admin token is required for API access.

## Table of Contents
1. [Project Setup](#project-setup)
2. [API Design](#api-design)
3. [Data Model](#data-model)
4. [Reporting](#reporting)
5. [Security Posture](#security-posture)
6. [Local Deployment](#local-deployment)
7. [Future Enhancements](#future-enhancements)

---

## Project Setup

### Prerequisites
- Python 3.11+

### Steps
1. Create a Python virtual environment.
2. Install backend dependencies from `backend/requirements.txt`.
3. Run the API with `uvicorn backend.app.main:app --reload`.

---

## API Design
### Overview
- API-only MVP using REST endpoints with OpenAPI docs.
- Static admin token required via `X-Admin-Token` header.

### Core Endpoints
- `/health`
- `/accounts`
- `/transactions`
- `/reports/summary`
- `/reports/by-account`
- `/export/transactions.csv`
- `/audit-logs`

---

## Data Model
### Entities
- `accounts`: name, description, is_active
- `transactions`: account_id, type (income/expense), amount, currency, created_at
- `audit_logs`: action, entity_type, entity_id, details

### Notes
- Transactions are immutable; corrections are modeled as adjustment entries.
- Single currency for MVP, with schema extensible to multi-currency later.

---

## Reporting
### MVP Reports
- Totals by time range
- Totals by account
- CSV export of transactions

---

## Security Posture
### MVP
- Local-only use with static admin token.
- Add full authentication and multi-tenant isolation before any public deployment.

---

## Local Deployment
### MVP Run
1. Install dependencies.
2. Start the API server with `uvicorn backend.app.main:app --reload`.
3. Use the Swagger UI at `/docs` for manual testing.

---

## Future Enhancements
- Authentication and role-based access control.
- Multi-tenant data isolation.
- Payment processing integrations.
- Frontend UI.
