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
* **ORM**: SQLAlchemy 2.x
* **Database Migrations**: Alembic
* **Data Validation**: Pydantic v2
* **Authentication**: JWT with Argon2 / bcrypt password hashing
* **API Style**: REST API with standard versioning under `/api/v1/`

### Database & Infrastructure
* **Database**: Local PostgreSQL 16
* **Containerization**: Docker & Docker Compose with persistent local volumes
* **Host Requirement**: No third-party cloud database dependencies (no Supabase, Firebase, PlanetScale, etc.)

---

## 3. Local Development Prerequisites

Ensure the following tools are available on your system:
* **Operating System**: Linux (Ubuntu 22.04+ recommended), macOS, or Windows WSL2
* **Docker & Docker Compose**: Docker 24+ with Compose v2
* **Python**: Python 3.10+ (with `venv` and `pip`)
* **Node.js**: Node.js 18+ (Node 20 LTS recommended) and `npm`
* **Git**

---

## 4. Planned Project Structure

```text
familynest/
├── .env                  # Local environment configuration (Git-ignored)
├── .env.example          # Template environment configuration
├── .gitignore            # Git ignore rules for Python, Node, environment, etc.
├── docker-compose.yml    # Local Docker Compose setup (PostgreSQL & persistent volume)
├── README.md             # Project documentation and architecture guide
│
├── backend/              # FastAPI Backend
│   ├── alembic/          # Alembic database migration environment
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   ├── alembic.ini       # Alembic migration configuration
│   ├── app/
│   │   ├── main.py       # FastAPI application factory and routing setup
│   │   ├── core/         # Settings, configuration, and security helpers
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── db/           # SQLAlchemy 2.x engine, session, and models
│   │   │   ├── database.py
│   │   │   └── models/
│   │   │       └── __init__.py
│   │   ├── schemas/      # Pydantic validation and serialization schemas
│   │   │   └── __init__.py
│   │   ├── api/          # API routers and endpoints
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       └── api.py
│   │   ├── services/     # Domain business logic
│   │   │   └── __init__.py
│   │   ├── repositories/ # Data access abstraction layer
│   │   │   └── __init__.py
│   │   └── tests/        # Pytest test suite
│   │       ├── __init__.py
│   │       └── test_health.py
│   ├── Dockerfile
│   ├── .dockerignore
│   └── requirements.txt
│
└── frontend/             # React + TypeScript + Vite + Tailwind CSS Frontend
    ├── index.html        # Entry HTML with mobile viewport configuration
    ├── package.json      # Dependencies and scripts
    ├── tsconfig.json     # TypeScript configuration
    ├── tsconfig.node.json
    ├── vite.config.ts    # Vite configuration
    ├── tailwind.config.js# Custom warm theme & typography
    ├── postcss.config.js
    ├── Dockerfile
    ├── .dockerignore
    └── src/
        ├── App.tsx       # Welcome interface and readiness check
        ├── main.tsx      # React root bootstrap
        ├── index.css     # Global styles & Tailwind directives
        ├── components/   # UI components
        ├── pages/        # View screens
        ├── services/     # API client services
        └── types/        # TypeScript domain models and interfaces
```

---

## 5. Getting Started (Initialization Phase)

### 1. Configure Environment
Copy `.env.example` to `.env` if not already present:
```bash
cp .env.example .env
```

### 2. Start PostgreSQL via Docker Compose
To run PostgreSQL in the background with persistent volume storage:
```bash
docker compose up -d postgres
```
Check health:
```bash
docker compose ps
```

### 3. Backend Setup
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8000
```
FastAPI interactive docs will be available at: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)

### 4. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
The Vite development server will be available at: [http://localhost:5173](http://localhost:5173)

---

## 6. Development Principles & Future Phases

1. **Phase 0 (Current)**: Project initialization and foundational structure.
2. **Phase 1 (Upcoming)**: Database schemas, migrations, and core entities (`users`, `people`, `families`, `relationships`).
3. **Phase 2+**: Authentication, family network contribution, relationship graph engine, mobile layout, and Capacitor Android bundling.
