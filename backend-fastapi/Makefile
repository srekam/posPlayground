# PlayPark FastAPI Backend Makefile

.PHONY: help install dev test lint format clean build run docker-build docker-up docker-down seed

# Default target
help:
	@echo "PlayPark FastAPI Backend - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  install     Install dependencies"
	@echo "  dev         Run development server"
	@echo "  test        Run tests"
	@echo "  lint        Run linting"
	@echo "  format      Format code"
	@echo "  clean       Clean cache files"
	@echo ""
	@echo "Docker:"
	@echo "  build       Build Docker image"
	@echo "  docker-up   Start services with Docker Compose"
	@echo "  docker-down Stop Docker Compose services"
	@echo ""
	@echo "Database:"
	@echo "  seed        Seed database with demo data"
	@echo ""
	@echo "Utilities:"
	@echo "  gen-sdk     Generate client SDK from OpenAPI"
	@echo "  docs        Generate documentation"

# Development commands
install:
	pip install --upgrade pip setuptools wheel
	pip install -e ".[dev]"
	pre-commit install

dev:
	uvicorn app.main:app --host 0.0.0.0 --port 48080 --reload

test:
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term

lint:
	flake8 app/ tests/
	mypy app/
	black --check app/ tests/
	isort --check-only app/ tests/

format:
	black app/ tests/
	isort app/ tests/

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/

# Docker commands
build:
	docker build -t playpark-api .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f api

docker-shell:
	docker-compose exec api bash

# Database commands
seed:
	python -m app.scripts.seed_database

# Utility commands
gen-sdk:
	@echo "Generating client SDK from OpenAPI spec..."
	# Add SDK generation commands here

docs:
	@echo "Generating documentation..."
	# Add documentation generation commands here

# Production commands
run:
	uvicorn app.main:app --host 0.0.0.0 --port 48080 --workers 4

# Health check
health:
	curl -f http://localhost:48080/healthz || exit 1

# Quick setup for development
setup: install docker-up
	@echo "Waiting for services to be ready..."
	sleep 30
	$(MAKE) seed
	@echo "Setup complete! Run 'make dev' to start development server."
