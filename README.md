# URL Shortener gRPC API

---

## Features

- High-performance async **gRPC API**
- URL shortening with PostgreSQL + Redis caching
- Event-driven via Kafka (FastStream)
- Full DDD / Clean Architecture setup
- Async ORM with SQLAlchemy & Alembic migrations
- Unit of Work & transaction management
- DI with Dishka, testing with pytest
- Observability stack: Prometheus, Grafana, Loki, Promtail

---

## Tech Stack
| Layer               | Tools & Tech                            |
|---------------------|-----------------------------------------|
| API                 | gRPC (protobuf)                         |
| DB & ORM            | PostgreSQL, SQLAlchemy (async), Alembic |
| Caching             | Redis                                   |
| Messaging           | Kafka (FastStream)                      |
| DI & Architecture   | Dishka, DDD, Clean Architecture         |
| Testing & QA        | pytest, Ruff, Pyright                   |
| Observability       | Prometheus, Grafana, Loki, Promtail     |
| DevOps & Containers | Docker, Docker Compose, Justfile        |

---

## Documentation

### gRPC UI (grpcui)

```bash
grpcui -plaintext localhost:50051
````

### Additional docs

* [gRPC docs](docs/grpc/grpc.md)

---

## Architecture Diagrams

<details>
<summary>DB Schema</summary>
<img src="docs/images/schemas/db.png" alt="DB Schema"/>
</details>

<details>
<summary>Classes Diagram</summary>
<img src="docs/images/schemas/classes_shortener.png" alt="Classes Diagram"/>
</details>

<details>
<summary>Packages Diagram</summary>
<img src="docs/images/schemas/packages_shortener.png" alt="Packages Diagram"/>
</details>

<details>
<summary>System Diagram</summary>
<p>TODO: Add Excalidraw system diagram</p>
</details>

---

## Quick Start (Docker & Just)
1. Clone repo
```bash
  git clone git@github.com:mrKazzila/shortener_url_api.git
  cd shortener_url_api/backend
```

2. Configure env & pgbouncer (edit `env.env` and `backend/docker/compose/infra/pgbouncer/userlist.txt`)


3. Start infrastructure
```bash
  just infra-up
```

4. Run app (1 1 = partitions & replicas)
```bash
  just app-bootstrap 1 1
```

5. Optional monitoring stack
```bash
  just mon-up
```

6.  See all available commands
```bash
  just
````

---

## Local Load Testing (gRPC)

For local load testing, I use **ghz**.

### Example: CreateShortUrl

```bash
ghz --insecure \
  --proto ./proto/shortener_app/v1/shortener_app.proto \
  --call shortener_app.v1.ShortenerService.CreateShortUrl \
  -d '{"target_url":"https://example.com"}' \
  -c 50 \
  --duration 10m \
  --import-paths ./proto \
  localhost:50051
```

Example results:

* ~800k requests in 10 minutes
* ~1330 RPS
* Avg latency ~37ms
* P99 ~91ms
* Occasional `Unavailable` errors on the local network during aggressive competition

---

## ⚠️ Over-engineering Note

<details>
<summary>Why so many technologies?</summary>
This project intentionally uses advanced technologies (Kafka, Redis, DI, DDD, async ORM) for a simple URL shortener to showcase scalable, maintainable microservice design.
</details>

---

[![GitHub](https://img.shields.io/badge/github-mrKazzila-blue?logo=github)](https://github.com/mrKazzila)
[![Portfolio](https://img.shields.io/badge/portfolio-mrkazzila.com-orange)](https://mrkazzila.com)
[![LinkedIn](https://img.shields.io/badge/linkedin-i--kazakov-blue?logo=linkedin)](https://www.linkedin.com/in/i-kazakov/)
