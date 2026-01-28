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

## Project Tree

<details>
<summary>Backend folder</summary>

```shell
.
├── docker
│   ├── compose
│   │   ├── app
│   │   │   └── docker-compose.yml
│   │   ├── infra
│   │   │   ├── docker-compose.yml
│   │   │   └── pgbouncer
│   │   │       ├── pgbouncer.ini
│   │   │       └── userlist.txt
│   │   └── monitoring
│   │       ├── docker-compose.yml
│   │       ├── grafana
│   │       │   ├── dashboards
│   │       │   │   ├── fastapi-observability.json
│   │       │   │   └── logs.json
│   │       │   └── datasources
│   │       │       └── datasources.yml
│   │       ├── loki
│   │       │   └── config.yml
│   │       ├── prometheus
│   │       │   └── prometheus.yml
│   │       └── promtail
│   │           └── config.yml
│   └── dockerfiles
│       ├── Consumer.dockerfile
│       └── Dockerfile
├── env
├── just
│   ├── all.just
│   ├── convenience.just
│   ├── db.just
│   ├── docs.just
│   ├── env.just
│   ├── helpers.just
│   ├── kafka.just
│   ├── local.just
│   ├── main.just
│   ├── quality.just
│   ├── req.just
│   └── stacks.just
├── justfile
├── proto
│   ├── common
│   │   └── v1
│   │       └── common.proto
│   ├── shortener_app
│   │   └── v1
│   │       └── shortener_app.proto
│   └── user_urls
│       └── v1
│           └── user_urls.proto
├── pyproject.toml
├── scripts
│   ├── gen_grpc.sh
│   ├── gen_proto_doc.sh
│   ├── run_app.sh
│   ├── run_grpc.sh
│   └── run_tests.sh
├── src
│   ├── __init__.py
│   ├── application
│   │   ├── __init__.py
│   │   ├── dtos
│   │   │   ├── __init__.py
│   │   │   ├── urls.py
│   │   │   └── users.py
│   │   ├── exceptions
│   │   │   ├── __init__.py
│   │   │   └── base.py
│   │   ├── interfaces
│   │   │   ├── __init__.py
│   │   │   ├── broker.py
│   │   │   ├── cache.py
│   │   │   ├── repository.py
│   │   │   └── uow.py
│   │   ├── mappers
│   │   │   ├── __init__.py
│   │   │   └── url_mapper.py
│   │   └── use_cases
│   │       ├── __init__.py
│   │       ├── create_short_url.py
│   │       ├── delete_url.py
│   │       ├── get_user_urls.py
│   │       ├── internal
│   │       │   ├── __init__.py
│   │       │   ├── add_new_url_to_cache.py
│   │       │   ├── check_key_in_cache.py
│   │       │   ├── create_uniq_key_in_cache.py
│   │       │   ├── get_target_url_by_key.py
│   │       │   ├── process_new_url.py
│   │       │   ├── process_url_state_update.py
│   │       │   ├── publish_data_to_broker.py
│   │       │   └── publish_to_broker_for_update.py
│   │       ├── redirect_to_original_url.py
│   │       └── update_url.py
│   ├── config
│   │   ├── __init__.py
│   │   ├── app_setup.py
│   │   ├── ioc
│   │   │   ├── __init__.py
│   │   │   ├── consumer_providers.py
│   │   │   ├── di.py
│   │   │   └── providers.py
│   │   └── settings
│   │       ├── __init__.py
│   │       ├── app.py
│   │       ├── base.py
│   │       ├── broker.py
│   │       ├── cors.py
│   │       ├── database.py
│   │       ├── loader.py
│   │       ├── logging.py
│   │       └── redis.py
│   ├── domain
│   │   ├── __init__.py
│   │   ├── entities
│   │   │   ├── __init__.py
│   │   │   └── url.py
│   │   ├── exceptions
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   └── domain.py
│   │   └── services
│   │       ├── __init__.py
│   │       └── key_generator.py
│   ├── generated
│   │   ├── __init__.py
│   │   ├── common
│   │   │   ├── __init__.py
│   │   │   └── v1
│   │   │       ├── __init__.py
│   │   │       ├── common_pb2.py
│   │   │       ├── common_pb2.pyi
│   │   │       └── common_pb2_grpc.py
│   │   ├── shortener_app
│   │   │   ├── __init__.py
│   │   │   └── v1
│   │   │       ├── __init__.py
│   │   │       ├── shortener_pb2.py
│   │   │       ├── shortener_pb2.pyi
│   │   │       └── shortener_pb2_grpc.py
│   │   └── user_urls
│   │       ├── __init__.py
│   │       └── v1
│   │           ├── __init__.py
│   │           ├── user_urls_pb2.py
│   │           ├── user_urls_pb2.pyi
│   │           └── user_urls_pb2_grpc.py
│   ├── infrastructures
│   │   ├── __init__.py
│   │   ├── broker
│   │   │   ├── __init__.py
│   │   │   ├── consumers
│   │   │   │   ├── __init__.py
│   │   │   │   ├── common.py
│   │   │   │   ├── consumer_new_url.py
│   │   │   │   └── consumer_update_url.py
│   │   │   ├── new_url_publish_queue.py
│   │   │   └── publisher.py
│   │   ├── cache
│   │   │   ├── __init__.py
│   │   │   └── redis_client.py
│   │   ├── db
│   │   │   ├── __init__.py
│   │   │   ├── models
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py
│   │   │   │   ├── click_inbox.py
│   │   │   │   └── urls.py
│   │   │   ├── repository.py
│   │   │   ├── session.py
│   │   │   └── uow.py
│   │   ├── exceptions
│   │   │   ├── __init__.py
│   │   │   └── base.py
│   │   └── mappers
│   │       ├── __init__.py
│   │       └── url_db_mapper.py
│   ├── main.py
│   ├── main.py
│   └── presentation
│       ├── __init__.py
│       ├── api
│       │   ├── __init__.py
│       │   ├── middleware
│       │   │   ├── __init__.py
│       │   │   └── error_middleware.py
│       │   ├── rest
│       │   │   ├── __init__.py
│       │   │   └── routers
│       │   │       ├── __init__.py
│       │   │       ├── healthcheck
│       │   │       │   ├── __init__.py
│       │   │       │   └── routers.py
│       │   │       ├── urls
│       │   │       │   ├── __init__.py
│       │   │       │   ├── _types.py
│       │   │       │   └── routers.py
│       │   │       └── users
│       │   │           ├── __init__.py
│       │   │           └── routers.py
│       │   └── schemas
│       │       ├── __init__.py
│       │       ├── healthcheck.py
│       │       ├── pagination.py
│       │       ├── urls.py
│       │       └── users.py
│       ├── exceptions
│       │   ├── __init__.py
│       │   ├── auth.py
│       │   ├── base.py
│       │   └── urls.py
│       ├── grpc
│       │   ├── __init__.py
│       │   ├── interceptors
│       │   │   ├── __init__.py
│       │   │   └── reflection_v1_compat.py
│       │   ├── server.py
│       │   └── services
│       │       ├── __init__.py
│       │       ├── shortener_app.py
│       │       └── user_urls.py
│       └── mappers
│           ├── __init__.py
│           ├── url_mapper.py
│           └── user_mapper.py
├── tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── e2e
│   │   └── __init__.py
│   ├── fixtures
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── environment.py
│   ├── integration
│   │   └── __init__.py
│   └── unit
│       └── __init__.py
└── uv.lock

73 directories, 168 files
```

</details>

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
