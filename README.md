# Project Samarth

An AI-driven question-answering platform for Indian government datasets from data.gov.in, focusing on agricultural economy and climate patterns.

## Architecture Overview

Project Samarth combines:
- Automated ETL pipelines for government datasets
- PostgreSQL data warehouse with metadata layer
- Large Language Model (LLM) for intelligent reasoning
- Streamlit frontend for intuitive data exploration

## System Components

1. **Data Ingestion**: ETL pipelines that fetch datasets from data.gov.in
2. **Data Warehouse**: PostgreSQL database storing structured government data
3. **Query Engine**: LLM-powered natural language processing and SQL generation
4. **API Layer**: FastAPI backend serving the query interface
5. **Frontend**: Streamlit application for user interaction

## Setup Instructions

### Prerequisites
- Python 3.9+
- PostgreSQL (or Neon PostgreSQL)
- Docker (optional, for containerized deployment)
- API keys for OpenAI and data.gov.in

### Local Development Setup

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv samarth-env
   source samarth-env/bin/activate  # On Windows: samarth-env\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```bash
   cp samarth/.env.example samarth/.env
   # Edit .env with your actual API keys and database credentials
   ```
5. Initialize the database:
   ```bash
   python samarth/data/initialize_db.py
   ```
6. Run the ETL pipeline to populate initial data:
   ```bash
   python samarth/data/etl_pipeline.py
   ```
7. Start the API server:
   ```bash
   uvicorn samarth.main:app --reload
   ```
8. In a new terminal, start the Streamlit frontend:
   ```bash
   streamlit run samarth/frontend/app.py
   ```

## API Endpoints

- `POST /api/v1/query/ask` - Ask a question and get an AI-generated answer
- `GET /api/v1/query/datasets` - List all available datasets

## Project Structure

```
samarth/
├── api/              # FastAPI routes
├── data/             # Database and ETL components
├── frontend/         # Streamlit application
├── models/           # Data models
├── services/         # Business logic
├── utils/            # Utility functions
├── main.py           # Application entry point
└── __init__.py       # Package initializer
```

## License

This project is licensed under the MIT License.
