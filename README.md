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

## 5. People Domain API (Phase 3)

The People API manages canonical human records (`Person`), enforcing the strict `USER ≠ PERSON` rule. A Person record can exist independently of an application User account.

### Endpoints
* `POST /api/v1/people` - Create a new person (creator becomes `created_by_user_id`).
* `GET /api/v1/people` - List accessible people (paginated, searchable, secure).
* `GET /api/v1/people/{id}` - Get person details (includes phone/email if authorized).
* `PATCH /api/v1/people/{id}` - Partially update a person record.

### Security Rules
* All endpoints require an authenticated access token.
* `created_by_user_id` is always derived from the authenticated token.
* Attempting to access an unauthorized person returns a privacy-preserving `404 Not Found`.

---

## 6. Family Network & Membership API (Phase 4)

FamilyNest models Families as independent networks/groups. A person can belong to multiple family networks. 

### Critical Architecture Rules
1. **Marriage does NOT merge families:** Family membership is completely independent of the relationship graph. If Person A (Patel Family) and Person B (Shah Family) marry, their family networks remain separate. No family merging happens automatically.
2. **Membership does NOT imply relationship:** Adding Person A and Person B to the same family does NOT magically make them siblings, parents, or spouses.
3. **No automatic Person creation:** Creating a Family or adding a member requires existing Person records. The API does not create fake or shadow Person records.
4. **Ownership:** A Family creator automatically becomes the `owner` if their User account has a claimed Person.

### Endpoints
* `POST /api/v1/families` - Create family network.
* `GET /api/v1/families` - List accessible families (paginated, creator/member access only).
* `GET /api/v1/families/{id}` - Get family detail.
* `PATCH /api/v1/families/{id}` - Update family metadata (owner/admin only).
* `DELETE /api/v1/families/{id}` - Delete family network (owner only). Safely cascades to memberships, leaving People and Relationships untouched.

### Membership Endpoints
* `POST /api/v1/families/{id}/members` - Add existing person to family.
* `GET /api/v1/families/{id}/members` - List family members.
* `PATCH /api/v1/families/{id}/members/{person_id}` - Update member role (`admin`, `member`, etc. `owner` assignment blocked).
* `DELETE /api/v1/families/{id}/members/{person_id}` - Remove member from family.

---

## 7. Relationship Graph API (Phase 5)

Relationships represent the canonical edge connections between People. Like People, the Relationship graph is strictly independent of User accounts and Family networks.

### Supported Fundamental Types
* `parent` (`person_a` = parent, `person_b` = child)
* `child` (`person_a` = child, `person_b` = parent)
* `spouse` (symmetric)
* `divorced_spouse` (symmetric)
* `sibling` (symmetric)
* `guardian` (`person_a` = guardian, `person_b` = dependent)

*Note: Derived relationships (grandparent, uncle, cousin) are dynamically calculated by the engine and are not stored in the database.*

### Core Invariants
1. **No Auto-Merging:** Marriages (`spouse`) or divorces (`divorced_spouse`) **never** merge or split Family Networks.
2. **Duplication Protection:** Logic prevents creating multiple identical active relationships, and correctly handles symmetry (e.g. `A spouse B` is identical to `B spouse A`).
3. **Historical Preservation:** Deleting an active relationship is supported, but transitioning to a historical state (e.g. `is_current = false`, `end_date = 2020`) is preferred for divorces to preserve the genealogical tree.

### Authorization Model
To create, update, or delete a relationship, a User must have authorized access to **both** canonical People. A user gains legitimate access if:
* The user created or claimed the Person.
* The user is in a Family Network where the Person is a member.

### Endpoints
* `POST /api/v1/relationships` - Connect two existing People.
* `GET /api/v1/relationships` - List accessible relationships (can filter by `person_id` or `relationship_type`).
* `GET /api/v1/relationships/{id}` - Fetch relationship details safely.
* `PATCH /api/v1/relationships/{id}` - Update status and dates (e.g., divorce workflow).
* `DELETE /api/v1/relationships/{id}` - Hard delete a relationship (preserves People).

---

## 8. Relationship Graph Engine (Phase 6)

The Relationship Graph Engine provides an intelligent, read-only layer over canonical People and Relationships. It dynamically traverses paths (using cycle-protected BFS) to derive human-readable kinship (e.g., grandparent, cousin, uncle, nephew) without ever writing derived relationships to the database.

### Key Graph Behaviors
* **Derived Kinship:** Automatically infers `grandparent`, `grandchild`, `uncle_or_aunt`, `nephew_or_niece`, `first_cousin`, and shared-parent `sibling` relationships at runtime.
* **Pathfinding:** Solves "How am I related to X?" by calculating the shortest authorized edge-path between two Person nodes.
* **Historical Awareness:** Graph queries prioritize current active relationships but can seamlessly traverse historical edges (e.g., `former_spouse`) when requested.
* **Strict Read-Only:** The engine guarantees zero database mutation during traversal. No `family_members` rows or new `relationships` rows are ever inserted.
* **Authorization Boundaries:** Traversal only spans nodes the user has authorized access to. Attempting to traverse into an inaccessible family network halts and returns a privacy-preserving `404 Not Found`.

### Graph Endpoints
* `GET /api/v1/relationships/how-related/{person_id}` - Returns the shortest path and kinship label from the user's claimed profile.
* `GET /api/v1/relationships/path/{person_id}` - Same as above.
* `GET /api/v1/people/{person_id}/relationships` - Direct edges around a node.
* `GET /api/v1/people/{person_id}/ancestors` - Upward traversal.
* `GET /api/v1/people/{person_id}/descendants` - Downward traversal.
* `GET /api/v1/people/{person_id}/siblings` - Explicit siblings and inferred siblings via shared parents.

## 9. Person Claiming & Invitations (Phase 7)

This phase establishes the secure connection between a User account and their canonical Person profile in the graph. The strict rule `ONE REAL HUMAN = ONE CANONICAL PERSON` is enforced.

### Key Workflows
* **Direct Claiming:** A User creating their own account can create a Person and immediately claim it.
* **Token-Based Invitations:** Users can invite family members using cryptographically secure tokens.
* **Conflict Protection:** A User can only claim one Person. A Person can only be claimed by one User. Deceased people cannot be claimed.
* **Atomic Transactions:** Accepting an invitation securely updates the Person, marks the Invitation accepted, revokes all other pending invitations for that Person, and creates detailed Audit Logs atomically.

### Endpoints
* `POST /api/v1/people/{id}/claim` - Directly claim a Person (requires creator rights).
* `POST /api/v1/people/{id}/invitations` - Generate a secure invitation token for a Person.
* `GET /api/v1/invitations/me` - List your pending/active invitations.
* `POST /api/v1/invitations/{token}/accept` - Consume token and bind your User account to the Person.
* `POST /api/v1/invitations/{token}/cancel` - Cancel an invitation (creator only).

## 10. Notification Foundation (Phase 8)

This phase establishes the foundational backend infrastructure for audience targeting and notifications.

### Key Workflows
* **Audience Isolation:** Family networks are independent. Marriages do not merge notification audiences.
* **Audience Resolution:** The `AudienceService` deduplicates recipients and enforces strict privacy authorization before generating the recipient snapshots.
* **Notification State:** Each targeted user has an independent `notification_recipients` record tracking `is_read`, `read_at`, and `dismissed_at`.
* **Unclaimed People:** Notification target resolution intentionally filters out `Person` records without claimed user accounts to prevent fake notifications or accounts.

### Endpoints
* `POST /api/v1/notifications` - Create a notification targeting a `family`, `selected_members`, or `user` audience.
* `GET /api/v1/notifications` - List notifications (with `unread` filtering).
* `POST /api/v1/notifications/read-all` - Bulk mark notifications read.
* `POST /api/v1/notifications/{id}/read` - Mark specific notification read.
* `POST /api/v1/notifications/{id}/unread` - Mark specific notification unread.
* `POST /api/v1/notifications/{id}/dismiss` - Safely dismiss (soft delete) a notification.
* `GET /api/v1/notifications/preferences` - Get notification preferences.

---

## 11. Family Events & Activity (Phase 9)

FamilyNest supports a dedicated `Event` domain to record significant dates, gatherings, and family activities. Events can represent birthdays, anniversaries, important dates, announcements, and traditional family events.

**Important Dates:**
- `birthday`: Represents a Person's birthday.
- `anniversary`: Represents a milestone (like marriage).
- `important_date`: General meaningful dates (graduation, memorial, etc.).
- `family_event`: Structured events like family meetings, weddings.
- `announcement`: General family announcements with controlled visibility.

**Event Participants:**
Participants (`EventParticipant`) are canonical `Person` records. A participant does not automatically need to be a claimed `User`. This allows recording an event for an unclaimed relative (e.g., Grandfather). 

**Privacy & Family Isolation:**
Events follow the strict family isolation architecture. An event is secured via an `EventTarget` (audience).
- A Father's family event is invisible to the Mother's family unless explicitly shared.
- Marriage does not merge event visibility. 
- You can target specific families, selected members, or just the current user.

**Family Activity:**
The `Activity` model records lightweight audit trails for major domain changes (e.g., event created, person joined family) to power a future dashboard. 
- Activity is derived from canonical domain objects.
- Activity feed visibility mirrors the underlying object's visibility rules.
- Activity is not a global social media feed.

## 12. Profile, Privacy & Dashboard (Phase 10)

This phase finalizes the backend foundation, providing unified dashboards and explicit privacy controls.

**Privacy Architecture:**
FamilyNest is private-by-design. The `PersonPrivacySettings` model enforces field-level visibility (`private`, `family`, `public`/`selected`) on sensitive properties.
- **Sensitive Fields:** `phone`, `email`, `date_of_birth`, and `bio`.
- **Dynamic Redaction:** The API (`SafePersonSummary`) automatically strips sensitive data depending on the viewer's authorization and the profile owner's privacy settings. Unclaimed profiles default to `private` for sensitive data.

**Dashboard Aggregation:**
The `/api/v1/dashboard` endpoint acts as an aggregation layer over existing domain APIs.
- It aggregates Profile Summaries, Relationship Counts (parents, children, siblings, spouses), Upcoming Events, and Recent Activity.
- It is bound by limits to avoid N+1 queries.
- It strictly preserves Family Separation (e.g., Mother's family and Father's family remain distinct lists).

**Completeness Validation:**
A dynamic profile completeness checker helps guide users to fill out essential information (name, dob, bio, profile photo).

---

## 13. Environment & Database Configuration

### Environment Setup
FamilyNest uses environment variables for all configuration.

Copy the template file to `.env`:
```bash
cp backend/.env.example backend/.env
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

## 14. Database Migrations (Alembic)

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

## 15. Running Tests

Execute the complete test suite (157 tests covering database integrity, authentication, people domain, family network, relationships, graph engine traversal, person claiming, notifications, events, privacy, and health checks):
```bash
cd backend
pytest -v
```

Tests run within isolated transactions and roll back after execution, ensuring persistent Neon data is never polluted or destroyed.
