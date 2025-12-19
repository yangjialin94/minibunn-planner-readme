# Minibunn Planner API

**Status:** Discontinued (December 2025)  
**Active period:** July 2025 – December 2025

Minibunn Planner API was the backend service for the Minibunn Planner web application. It handled authentication, business logic, persistence, and subscription management for a production SaaS product.

This repository is preserved **for technical review and documentation purposes only**.  
All services, billing, and deployments have been shut down.

---

## Overview

The API supported:

- Task, backlog, note, and calendar management
- User authentication and authorization
- Subscription enforcement and billing state
- Background scheduling and maintenance jobs

The system was designed as a modular FastAPI service with a clear separation between routing, business logic, and infrastructure concerns.

---

## Tech Stack

- **Language**: Python  
- **Framework**: FastAPI  
- **Database**: PostgreSQL (SQLAlchemy ORM, Alembic migrations)  
- **Authentication**: Firebase Authentication  
- **Payments**: Stripe (subscriptions, webhooks)  
- **Background Jobs**: APScheduler  
- **Testing**: Pytest  
- **Formatting**: Black  

---

## Architecture & Project Structure

```text
app/
├── core/        # Configuration and shared utilities
├── deps/        # Dependency injection
├── models/      # SQLAlchemy ORM models
├── routes/      # API route handlers
├── schemas/     # Pydantic request/response schemas
├── services/    # Business logic and integrations
├── tests/       # Unit and integration tests
migrations/      # Alembic migration scripts
```

---

## Architectural Notes

- Layered structure: Routes → Services → Models
- External systems (Firebase, Stripe) isolated behind service layers
- Authorization and subscription checks enforced via dependencies
- Background tasks decoupled from request lifecycle

---

## Testing & Reliability

The API included extensive automated testing to validate core business flows.

### Test summary

- Total tests: 102
- Pass rate: 100%
- Code coverage: ~97%

### Coverage highlights

- Models & schemas: 100%
- Core business logic: 100%
- Authentication & dependency layers: 97%
- Stripe integration: partially covered due to external dependencies

Testing consisted of both unit and integration tests to ensure correctness and maintainability.

---

## Shutdown Notes

As part of the product sunset:

- All Stripe subscriptions, webhooks, and API keys were disabled
- Backend services were shut down
- Production database was backed up and deleted
- No active endpoints or scheduled jobs remain

This ensured no ongoing cost, billing, or user impact.

---

## Related Project

This API was part of the broader Minibunn Planner project.

- Project overview: <https://github.com/yangjialin94/minibunn-planner>
- Frontend (WEB): <https://github.com/yangjialin94/minibunn-planner/app/web>

---

## ⚖️ License

- Code is **not open source** and cannot be copied, modified, or redistributed.  
- This repository is for **review purposes only**.  
