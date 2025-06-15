# Backend Service

FastAPI-based backend for the TravelPal application.

## Development

### Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

### Running the Application

```bash
uvicorn app.main:app --reload
```

### Testing

```bash
pytest tests/
```

### API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
