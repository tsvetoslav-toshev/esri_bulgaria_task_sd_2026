# USA State Population Data System

A Python-based system that fetches county-level population data from the ArcGIS USA Census Counties API, aggregates it by state, stores it in a SQLite database, and provides a REST API for querying the data.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Project Structure](#project-structure)

## Features

- **Data Fetching**: Automatically retrieves county population data from ArcGIS REST API with pagination support
- **Data Aggregation**: Aggregates county-level data to state-level totals
- **Database Storage**: Stores aggregated data in SQLite database
- **REST API**: FastAPI-based API for querying state population data
- **Scheduled Updates**: Optional hourly data refresh
- **Comprehensive Testing**: Unit tests for both API and data processing
- **Type Hints**: Full type annotations for better code quality
- **Logging**: Detailed logging for monitoring and debugging

## Architecture

```
┌─────────────────┐
│  ArcGIS REST    │
│  API (Counties) │
└────────┬────────┘
         │ fetch_data.py
         ▼
┌─────────────────┐
│  Aggregation    │
│  (By State)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  SQLite DB      │
│  demographics.db│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI        │
│  REST API       │
└─────────────────┘
```

## Installation

### Prerequisites

- Python 3.12 or higher
- pip package manager

### Setup

1. **Clone or download the repository**
   ```bash
   git clone <repository-url>
   cd esri_bulgaria_task_sd_2026
   ```

2. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

   Or install packages individually:
   ```powershell
   pip install requests fastapi uvicorn schedule pytest httpx
   ```

## Usage

### 1. Fetch and Store Data

Run once to fetch data and populate the database:

```bash
python fetch_data.py
```

Run with automatic hourly updates:

```bash
python fetch_data.py --schedule
```

**Output:**
```
2026-01-16 10:30:00 - INFO - Starting data fetch...
2026-01-16 10:30:05 - INFO - Fetched 3144 counties
2026-01-16 10:30:05 - INFO - Aggregated data for 51 states
2026-01-16 10:30:05 - INFO - Database updated: 51 states saved
```

### 2. Start the API Server

```bash
python -m uvicorn api:app --reload
```

The API will be available at: **http://127.0.0.1:8000**

### 3. Access API Documentation

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## 🔌 API Documentation

### Endpoints

#### `GET /`
Health check endpoint.

**Response:**
```json
{
  "Hello": "World"
}
```

#### `GET /states`
Retrieve all states with population data.

**Response:**
```json
[
  {
    "state_name": "California",
    "population": 39538223
  },
  {
    "state_name": "Texas",
    "population": 29145505
  }
]
```

#### `GET /states/{state_name}`
Retrieve population data for a specific state.

**Parameters:**
- `state_name` (path): Name of the state (e.g., "California")

**Response (200):**
```json
{
  "state_name": "California",
  "population": 39538223
}
```

**Response (404):**
```json
{
  "detail": "State not found"
}
```

### Example Requests

Using curl:
```bash
# Get all states
curl http://127.0.0.1:8000/states

# Get specific state
curl http://127.0.0.1:8000/states/Texas
```

Using PowerShell:
```powershell
# Get all states
Invoke-RestMethod -Uri "http://127.0.0.1:8000/states"

# Get specific state
Invoke-RestMethod -Uri "http://127.0.0.1:8000/states/California"
```

## 🧪 Testing

Run all tests:

```bash
python -m pytest test_app.py -v
```

Run specific test:

```bash
python -m pytest test_app.py::test_aggregate_by_state -v
```

**Test Coverage:**
- ✅ API endpoint testing (GET /, GET /states, GET /states/{name})
- ✅ Error handling (404 for invalid states)
- ✅ Data aggregation logic
- ✅ Null/None value handling

## 📁 Project Structure

```
esri_bulgaria_task_sd_2026/
│
├── api.py                  # FastAPI REST API application
├── fetch_data.py           # Data fetching and processing
├── test_app.py             # Unit tests
├── requirements.txt        # Python dependencies
├── README.md               # This file
└── demographics.db         # SQLite database (created on first run)
```

### File Descriptions

**`api.py`**
- FastAPI application with 3 endpoints
- Database connection management
- Response models and error handling

**`fetch_data.py`**
- Fetches data from ArcGIS REST API with pagination
- Aggregates county data by state
- Saves to SQLite database
- Supports scheduled execution

**`test_app.py`**
- Unit tests for API endpoints
- Unit tests for aggregation logic
- Tests for edge cases (None values, invalid states)

**`requirements.txt`**
- Lists all Python package dependencies

## 🗄 Database Schema

**Table: `state_population`**

| Column      | Type    | Constraints    | Description           |
|-------------|---------|----------------|-----------------------|
| state_name  | TEXT    | PRIMARY KEY    | Name of the state     |
| population  | INTEGER |                | Total state population|

## 🔧 Configuration

### API Configuration

Edit [api.py](api.py#L18-L22):
```python
app = FastAPI(
    title="USA State Population API",
    description="API for querying aggregated US state population data",
    version="1.0.0"
)
```

### Logging Configuration

Edit [fetch_data.py](fetch_data.py#L23-L26):
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

### Schedule Configuration

Edit [fetch_data.py](fetch_data.py#L139):
```python
schedule.every(1).hour.do(main)  # Change interval here
```

## 🐛 Troubleshooting

### Issue: "uvicorn is not recognized" or "pytest is not recognized"
**Solution:** Use Python's module execution syntax:
```bash
python -m uvicorn api:app --reload
python -m pytest test_app.py -v
```

**Windows PowerShell Note:** If you have spaces in your Python path, use:
```powershell
& "C:/Path to Python/python.exe" -m uvicorn api:app --reload
```

### Issue: Database locked
**Solution:** Close any applications accessing `demographics.db` or restart the API server.

### Issue: API returns empty list
**Solution:** Run `fetch_data.py` first to populate the database.

## 📝 License

This project is created as a task assignment for Esri Bulgaria.

## 👤 Author

Created for Esri Bulgaria Task - January 2026