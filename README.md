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
* **Authentication**: JWT (Access + Refresh tokens) with Argon2id password hashing
* **API Style**: REST API with standard versioning under `/api/v1/`

### Database & Infrastructure
* **Primary Database**: **Neon PostgreSQL** (serverless PostgreSQL 18.6 with native UUID and JSONB support)
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

## 4. Authentication Architecture (Phase 2)

FamilyNest implements secure authentication under `/api/v1/auth/`:

```text
                    Client
                      |
                      v
              FastAPI Auth API
                      |
          +-----------+-----------+
          |                       |
          v                       v
   Password Hashing          JWT Tokens
     Argon2id               Access/Refresh
          |                       |
          +-----------+-----------+
                      |
                      v
                Neon PostgreSQL
                    users
```

### Password Policy & Hashing
* **Algorithm**: **Argon2id** (via `passlib` context)
* **Minimum Length**: 8 characters
* **Maximum Length**: 128 characters
* **Protection**: Plaintext passwords and `password_hash` are never stored plaintext or returned in any API responses.

### Token Specifications
* **Access Token**: Short-lived JWT (15 minutes default) containing `sub` (User UUID) and `type: "access"`.
* **Refresh Token**: Longer-lived JWT (7 days default) containing `sub` (User UUID) and `type: "refresh"`.
* **Token Isolation**: Access tokens are strictly rejected on `/refresh`; refresh tokens are strictly rejected on `/me`.

### Endpoints & Usage Examples

#### 1. Register User Account
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "display_name": "Family Member"
}
```
*Note: Registration creates a `User` account and does NOT automatically create a `Person` record.*

#### 2. User Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```
Response:
```json
{
  "access_token": "<jwt_access_token>",
  "refresh_token": "<jwt_refresh_token>",
  "token_type": "bearer",
  "expires_in": 900
}
```

#### 3. Refresh Access Token
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "<jwt_refresh_token>"
}
```

#### 4. Get Current User Profile
```http
GET /api/v1/auth/me
Authorization: Bearer <jwt_access_token>
```

#### 5. Logout
```http
POST /api/v1/auth/logout
Authorization: Bearer <jwt_access_token>
```
*Note: In this stateless JWT model, the client purges stored tokens upon logout.*

---

## 5. Environment & Database Configuration

### Environment Setup
FamilyNest uses environment variables for all configuration.

Copy the template file to `.env`:
```bash
cp .env.example .env
```

Configure parameters in `.env`:
```env
JWT_SECRET_KEY=your_secure_random_jwt_secret_key_32chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
DATABASE_URL=postgresql+psycopg://<user>:<password>@<host>/<database>?sslmode=require
```

> [!IMPORTANT]
> **Security Rules:**
> * Never commit `.env` to Git.
> * Never expose the Neon connection string, usernames, or passwords in commits, issues, or logs.
> * Use `get_redacted_database_url()` for any diagnostic logging.

---

## 6. Database Migrations (Alembic)

Alembic manages all schema migrations dynamically reading `DATABASE_URL` from `.env`.

### Apply Migrations
```bash
cd backend
alembic upgrade head
```

### Rollback Migrations
```bash
cd backend
alembic downgrade -1
```

### Create a New Migration
```bash
cd backend
alembic revision --autogenerate -m "description_of_changes"
```

### Verify Live Database Schema
```bash
python -m app.db.verify_db
```

---

## 7. Running Tests

Execute the complete test suite (39 tests covering database integrity, constraints, health checks, and authentication):
```bash
cd backend
pytest -v
```

Tests run within isolated transactions and roll back after execution, ensuring persistent Neon data is never polluted or destroyed.
