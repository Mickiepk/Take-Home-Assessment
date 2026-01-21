.PHONY: help install dev-install test lint format type-check clean docker-build docker-up docker-down

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -e .

dev-install: ## Install development dependencies
	pip install -e ".[dev]"

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=computer_use_backend --cov-report=html

lint: ## Run linting
	flake8 computer_use_backend/
	flake8 tests/

format: ## Format code
	black computer_use_backend/ tests/
	isort computer_use_backend/ tests/

type-check: ## Run type checking
	mypy computer_use_backend/

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage

docker-build: ## Build Docker image
	docker compose build

docker-up: ## Start services with Docker
	docker compose up -d

docker-down: ## Stop Docker services
	docker compose down

docker-logs: ## View Docker logs
	docker compose logs -f

docker-test: ## Run tests in Docker
	docker compose exec backend pytest

dev: ## Start development environment
	docker compose up postgres redis -d
	python -m computer_use_backend.main