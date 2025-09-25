# PlayPark FastAPI Backend

A modern FastAPI backend for the PlayPark POS system, migrated from Node.js/Express with enhanced performance, type safety, and developer experience.

## Features

- **FastAPI** with async/await support
- **MongoDB** via Motor (async driver)
- **Pydantic v2** for data validation
- **OAuth2 PKCE** authentication
- **JWT** tokens with refresh mechanism
- **RBAC** (Role-Based Access Control)
- **Redis** caching and rate limiting
- **OpenAPI** documentation
- **Docker** deployment ready

## Quick Start

```bash
# Start all services
docker-compose up -d

# Check health
curl http://localhost:48080/healthz

# View API docs
open http://localhost:48080/docs
```

## Environment Variables

See `.env.example` for all configuration options.

## API Documentation

- **Swagger UI**: http://localhost:48080/docs
- **ReDoc**: http://localhost:48080/redoc
- **OpenAPI JSON**: http://localhost:48080/openapi.json
