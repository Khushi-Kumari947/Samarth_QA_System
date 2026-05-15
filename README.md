# Project Samarth

Project Samarth is an AI-driven question-answering platform for Indian agriculture and climate data. It enables users to ask natural language questions such as:

> "What was the crop production trend in Andhra Pradesh from 2010 to 2013?"

The system responds with:

- AI-generated answers
- SQL queries
- Dataset references
- Confidence metadata
- Visualization-ready data

The project combines a FastAPI backend, Streamlit frontend, PostgreSQL database, ETL utilities, and a Gemini-powered query pipeline.

---

# Features

- Natural language Q&A for:
  - Agricultural datasets
  - Weather datasets
  - Climate datasets
- FastAPI backend for querying and dataset discovery
- Streamlit frontend for interactive analysis
- PostgreSQL schema for:
  - Agricultural production
  - Weather data
  - Climate change records
  - Dataset metadata
  - Query logs
- ETL pipeline for importing:
  - data.gov.in resources
  - Local climate CSV files
- AI-powered:
  - SQL generation
  - Query execution
  - Answer synthesis
  - Confidence scoring
  - Visualization preparation
- Example API client
- Demo script
- Unit testing support

---

# Tech Stack

| Area | Technology |
|---|---|
| Backend API | FastAPI, Uvicorn |
| Frontend | Streamlit |
| Database | PostgreSQL |
| LLM | Google Gemini 2.5 Flash |
| ORM / DB Access | psycopg2-binary |
| Data Processing | Pandas, Matplotlib |
| Environment Management | python-dotenv |
| Validation | Pydantic |
| API Requests | Requests |

---

# Project Structure

```text
samarth/
│
├── api/                  # FastAPI routers
├── data/                 # Database connection, ETL, schema setup
├── examples/             # Example API client
├── frontend/             # Streamlit frontend
├── models/               # Pydantic models
├── services/             # LLM + query orchestration
├── tests/                # Unit tests
├── utils/                # Validation and visualization helpers
│
├── demo.py               # End-to-end demo script
├── main.py               # FastAPI entry point
└── .env.example          # Example environment variables
```

---

# How It Works

1. A user submits a question through the API or Streamlit app
2. `LLMService` identifies relevant datasets
3. The service generates PostgreSQL queries
4. `QueryService` executes the SQL queries
5. Gemini synthesizes a readable answer
6. The response includes:
   - Final answer
   - SQL queries
   - Data sources
   - Confidence score
   - Execution time
   - Visualization data

---

# Requirements

- Python 3.10+
- PostgreSQL
- Gemini API Key
- data.gov.in API Key (optional for ETL)

---

# Required Python Packages

```text
fastapi
uvicorn
streamlit
requests
pandas
matplotlib
python-dotenv
psycopg2-binary
pydantic
google-generativeai
```

---

# Setup

## Clone the Repository

```bash
cd samarth
```

---

## Create Virtual Environment

```bash
python -m venv .venv
```

### Activate Environment (Windows)

```bash
.venv\Scripts\activate
```

---

## Install Dependencies

```bash
pip install fastapi uvicorn streamlit requests pandas matplotlib python-dotenv psycopg2-binary pydantic google-generativeai
```

---

# Environment Configuration

Create a `.env` file:

```bash
copy .env.example .env
```

Update `.env` with your local configuration.

---

# Environment Variables

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/samarth

DB_HOST=localhost
DB_PORT=5432
DB_NAME=samarth
DB_USER=postgres
DB_PASSWORD=password

GEMINI_API_KEY=your_gemini_api_key_here
LLM_MODEL=gemini-2.5-flash

DATA_GOV_IN_API_KEY=your_data_gov_in_api_key_here

APP_ENV=development
DEBUG=True

API_BASE_URL=http://localhost:8000
```

---

# Database Initialization

Create a PostgreSQL database named:

```text
samarth
```

Initialize the database tables:

```bash
python data/initialize_db.py
```

---

# Database Tables

The initialization script creates:

- agricultural_production
- weather_data
- climate_change_data
- dataset_metadata
- user_queries

---

# Running the Backend

From the parent directory of the `samarth` package:

```bash
uvicorn samarth.main:app --reload
```

---

# Backend URLs

| Service | URL |
|---|---|
| API Root | http://localhost:8000 |
| Health Check | http://localhost:8000/health |
| Test Endpoint | http://localhost:8000/test |

---

# API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Welcome message |
| GET | `/health` | Health check |
| GET | `/test` | Basic API test |
| POST | `/api/v1/query/ask` | Ask a natural language question |
| GET | `/api/v1/query/datasets` | List available datasets |

---

# Example API Request

```bash
curl -X POST http://localhost:8000/api/v1/query/ask ^
  -H "Content-Type: application/json" ^
  -d "{\"question\":\"What was the crop production trend in Andhra Pradesh from 2010 to 2013?\"}"
```

---

# Running the Frontend

## From Parent Directory

```bash
streamlit run samarth/frontend/app.py
```

## From Inside the samarth Directory

```bash
streamlit run frontend/app.py
```

The frontend connects to:

```text
http://localhost:8000
```

by default using `API_BASE_URL`.

---

# Running the Demo

Run the demo script:

```bash
python demo.py
```

Ensure:

- PostgreSQL is running
- `.env` is configured
- `GEMINI_API_KEY` is valid

---

# ETL Pipeline

The ETL pipeline in:

```text
data/etl_pipeline.py
```

supports importing and transforming data from:

- data.gov.in APIs
- Local CSV climate datasets

---

# Run Complete ETL Pipeline

```bash
python data/etl_pipeline.py
```

---

# Optional ETL Environment Variables

```env
AGRICULTURE_RESOURCE_ID=your_agriculture_resource_id
WEATHER_RESOURCE_ID=your_weather_resource_id
```

The ETL module also supports:

```text
run_climate_etl_from_csv
```

for importing climate datasets from CSV files.

---

# Testing

Run unit tests:

```bash
python -m unittest discover tests
```

> Some tests instantiate the Gemini service, so ensure `GEMINI_API_KEY` is configured before running the full suite.

---

# Example API Client

An example API client is available at:

```text
examples/api_client.py
```

Run the client:

```bash
python examples/api_client.py
```

By default, it points to a deployed Railway backend URL.

For local testing, change:

```python
base_url = "http://localhost:8000"
```

---

# Data Scope

The current system supports:

- Agricultural production data for Indian states
- Weather and rainfall datasets
- Climate change records
- Station-level temperature statistics
- Rainfall statistics

The Streamlit frontend currently notes that available local data may include:

- Agricultural production records (2009–2015)
- Weather datasets for 2020

depending on the data loaded into PostgreSQL.

---

# Notes

- The query engine is designed for read-oriented SQL workflows
- Validation utilities are available in:
  
```text
utils/validation.py
```

- Generated SQL should be reviewed before production use
- Keep secrets and credentials inside `.env`
- Do not commit API keys or database credentials

---

# Future Improvements

- Better SQL safety validation
- Advanced chart generation
- Multi-language query support
- Conversation memory
- Dataset upload interface
- Role-based authentication
- Query history dashboard
- Hybrid vector + SQL retrieval
- Improved confidence evaluation pipeline

---
