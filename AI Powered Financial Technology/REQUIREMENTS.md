# Requirements

This document defines the MVP requirements for FinTech-SaaS-Space. It is the source of truth for what must be built before implementation begins.

## Product Goal
Deliver a proof-of-concept FinTech SaaS MVP for small and individual use that runs locally with minimal setup and provides a simple financial ledger and basic analytics through an API-only interface.

## Target Users
- Individuals who want simple personal finance tracking.
- Small businesses with lightweight internal bookkeeping needs.

## MVP Scope
- Single-tenant, local-first experience
- API-only proof of concept (UI deferred)
- Account and transaction management
- Basic reporting and analytics

## User Roles
- Admin: Single role with full access (static admin token, no login UI).

## Core User Journeys
1. User runs the API locally.
2. Admin creates accounts and records transactions.
3. Admin fetches ledger and basic analytics.

## Functional Requirements
- Static admin token required on API requests (no login UI).
- Single-tenant data model.
- SQLite default database for local setup.
- CRUD for accounts and transactions.
- Transaction ledger with immutable history.
- Basic analytics: totals by account, totals by time range.
- Local-first setup with minimal configuration.

## Non-Functional Requirements
- Simplicity: setup and run locally in minutes.
- Performance: 95% of API responses under 300ms for common queries.
- Observability: structured logs and basic error tracking.

## Data Requirements
- Entities: accounts, transactions, audit_logs.
- Mandatory fields: `created_at`, `updated_at`.
- Soft delete for accounts.
- Immutable transaction records with adjustment entries.
- Single-currency storage for MVP, with room to add multi-currency later.

## Integrations
- None required for MVP.

## Reporting Requirements
- Account balances and totals by time range.
- Transaction volume by day and by account.
- Export to CSV.

## Security Requirements
- Static admin token required for API access.
- Add full authentication and multi-tenant isolation before any public deployment.

## Out Of Scope For MVP
- Authentication and multi-user access control.
- Multi-tenant support.
- UI/UX and frontend application.
- Full payment processing and reconciliation.
- Real-time fraud detection.
- Advanced ML personalization.
- Mobile applications.

## Success Criteria
- Local app runs in under 5 minutes from clone.
- Users can create accounts and record transactions without errors.
- Basic analytics are usable for small/individual workflows.

## Open Questions
- What is the expected retention period for audit logs?
