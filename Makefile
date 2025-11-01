# Makefile for Project Samarth

# Variables
PYTHON := python3
PIP := pip
DOCKER := docker
DOCKER_COMPOSE := docker-compose

# Default target
.PHONY: help
help:
	@echo "Project Samarth - Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make install           Install dependencies"
	@echo "  make run-api           Run the API server"
	@echo "  make run-frontend      Run the frontend"
	@echo "  make run-etl           Run the ETL pipeline"
	@echo "  make init-db           Initialize the database"
	@echo "  make test              Run tests"
	@echo "  make demo              Run the demo"
	@echo "  make docker-build      Build Docker images"
	@echo "  make docker-up         Start services with Docker Compose"
	@echo "  make docker-down       Stop Docker Compose services"
	@echo "  make clean             Clean Python cache files"

# Install dependencies
.PHONY: install
install:
	$(PIP) install -r requirements.txt

# Run API server
.PHONY: run-api
run-api:
	$(PYTHON) -m uvicorn samarth.main:app --reload

# Run frontend
.PHONY: run-frontend
run-frontend:
	$(PYTHON) -m streamlit run samarth/frontend/app.py

# Run ETL pipeline
.PHONY: run-etl
run-etl:
	$(PYTHON) samarth/data/etl_pipeline.py

# Initialize database
.PHONY: init-db
init-db:
	$(PYTHON) samarth/data/initialize_db.py

# Run tests
.PHONY: test
test:
	$(PYTHON) -m unittest samarth/tests/test_samarth.py

# Run demo
.PHONY: demo
demo:
	$(PYTHON) samarth/demo.py

# Build Docker images
.PHONY: docker-build
docker-build:
	$(DOCKER) build -t samarth-api .
	$(DOCKER) build -f Dockerfile.frontend -t samarth-frontend .

# Start services with Docker Compose
.PHONY: docker-up
docker-up:
	$(DOCKER_COMPOSE) up --build

# Stop Docker Compose services
.PHONY: docker-down
docker-down:
	$(DOCKER_COMPOSE) down

# Clean Python cache files
.PHONY: clean
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*~" -delete
	find . -type f -name ".DS_Store" -delete