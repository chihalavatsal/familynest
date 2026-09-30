# FamilyNest

FamilyNest is a private digital home for families built around real human relationships, living memories, multi-generational networks, and lasting privacy.

---

## 1. Project Purpose & Core Concepts

FamilyNest replaces generic social networks and fragmented family chats with a secure, intimate digital home.

The foundation is built on three pillars:

$$\text{People} + \text{Relationships} + \text{Family Networks}$$

* **People vs. Users**: A `PERSON` is not the same thing as a `USER`. A person record can exist without an account (e.g. an elderly relative, child, or ancestor). When a family member creates an account, they can claim their existing person record without duplicating identity or disrupting the relationship graph.
* **Family Networks**: A person can belong to multiple family networks (e.g. Mother's Family, Father's Family, Spouse's Family). Marriage and kinship links connect people without forcibly merging separate family networks.
* **Relationship Graph**: Fundamental relationships (`parent`, `child`, `spouse`, `divorced_spouse`, `sibling`, `guardian`) are stored with historical retention (non-destructive updates). Derived relationships (such as aunt, uncle, cousin, grandparent) are calculated dynamically from the graph.
* **Privacy First**: Designed for private, sensitive family information with strict boundary controls and decoupled request/response schemas.

---

## 2. Technology Stack

### Frontend
* **Framework**: React 18 with TypeScript
* **Build Tool**: Vite
* **Styling**: Tailwind CSS (warm, human, elegant palette)
* **Icons**: Lucide React
* **Platform Target**: Single responsive codebase (Desktop Web, Tablet, Mobile Web, and future Android via Capacitor)

### Backend
* **Language & Framework**: Python 3.10+ with FastAPI
* **ORM**: SQLAlchemy 2.x (Modern `DeclarativeBase`, `Mapped`, `mapped_column`, typed relationships)
* **Database Migrations**: Alembic
* **Data Validation**: Pydantic v2
* **Authentication**: JWT with Argon2 / bcrypt password hashing (prepared)
* **API Style**: REST API with standard versioning under `/api/v1/`

### Database & Infrastructure
* **Primary Database**: **Neon PostgreSQL** (serverless PostgreSQL with native UUID and JSONB support)
* **SSL Requirement**: `sslmode=require` is enforced on all Neon connections.
* **Containerization**: Docker & Docker Compose configured for Neon cloud connectivity (local PostgreSQL container available optionally for offline work).

---

## 3. Database Architecture & Core Tables

FamilyNest Phase 1 implements seven foundational tables:

1. **`users`**: Authentication credentials, verification status, and timestamps.
2. **`people`**: Real human identity records (living or deceased). Supports unclaimed records and account claiming.
3. **`families`**: Independent family network circles.
4. **`family_members`**: Links people to family circles with specific roles (`owner`, `admin`, `member`, `invited`). Supports membership in multiple families.
5. **`relationships`**: Fundamental relationships (`parent`, `child`, `spouse`, `divorced_spouse`, `sibling`, `guardian`) with date spans and historical preservation. Self-relationships (`person_a_id == person_b_id`) are prevented via database CHECK constraints.
6. **`invitations`**: Family network and claiming invitations with secure tokens and status constraints.
7. **`audit_logs`**: System audit trail capturing actor, entity, action, and JSONB metadata.

---

## 4. Environment & Database Configuration

### Environment Setup
FamilyNest uses environment variables for all configuration.

Copy the template file to `.env`:
```bash
cp .env.example .env
```

Configure your Neon connection string in `.env`:
```env
DATABASE_URL=postgresql+psycopg://<user>:<password>@<host>/<database>?sslmode=require
```

> [!IMPORTANT]
> **Security Rules:**
> * Never commit `.env` to Git.
> * Never expose the Neon connection string, usernames, or passwords in commits, issues, or logs.
> * Use `get_redacted_database_url()` for any diagnostic logging.

---

## 5. Database Migrations (Alembic)

Alembic manages all schema migrations dynamically reading `DATABASE_URL` from `.env`.

### Apply Migrations
To upgrade the database to the latest schema:
```bash
cd backend
alembic upgrade head
```

### Rollback Migrations
To revert the most recent migration:
```bash
cd backend
alembic downgrade -1
```

### Create a New Migration
To auto-generate a migration based on model changes:
```bash
cd backend
alembic revision --autogenerate -m "description_of_changes"
```

### Verify Live Database Schema
To inspect table definitions, foreign keys, constraints, and indexes on the active database:
```bash
python -m app.db.verify_db
```

---

## 6. Running Tests

Execute the comprehensive database and integrity test suite:
```bash
cd backend
pytest app/tests/test_database.py -v
```

Tests run within isolated transactions and roll back after execution, ensuring persistent Neon data is never polluted or destroyed.
