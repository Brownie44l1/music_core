# music_core

> Personalised Nigerian music recommendation system.
> Academic ML project demonstrating collaborative filtering with Explainable AI.

## Services

| Service    | Stack              | Deploy       |
|------------|--------------------|--------------|
| `ml/`      | Python + FastAPI   | Render.com   |
| `backend/` | Python + FastAPI   | Render.com   |
| `frontend/`| React.js           | Vercel       |

## Architecture

```mermaid
flowchart LR
    Client((Developer App))
    Webhook((Webhook Endpoint))

    subgraph service[Chug Service]
        API[API Server]
        Queue[(Redis Queue)]
        Worker[Background Worker]
        DB[(PostgreSQL)]
        R2[(Cloudflare R2)]

        API <--> DB
        API -->|Enqueue| Queue
        Queue --> Worker
        Worker <--> DB
        Worker --> R2
    end

    Client -->|POST /uploads| API
    Client <-->|GET /uploads/:job_id| API
    Worker -->|POST Callback| Webhook
```

## Local Development

See README.md in each service folder for setup instructions.
