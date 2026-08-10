# System Architecture

## Architecture Diagram

```text
  [ React 19 Frontend (Vercel) ]
                 │
                 │ HTTP / REST / JSON
                 ▼
  [ FastAPI Backend Service (Render) ]
          │                │
          │                ▼
          │      [ Gemini API Service ]
          ▼
 [ Neon PostgreSQL DB ]
```

## Core Infrastructure
- **Frontend Layer:** React 19 single-page application built with Vite and styled with Tailwind CSS. Deployed on Vercel.
- **Backend Layer:** FastAPI high-performance asynchronous API framework managing security, ORM data access via SQLAlchemy, and business logic. Deployed on Render.
- **AI Engine Integration:** Google Gemini API for resume parsing, mock interviews, roadmap generation, and career advice.
- **Data Store:** Cloud-hosted Neon PostgreSQL managed via SQLAlchemy and Alembic migrations.
