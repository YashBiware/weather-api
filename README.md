# Weather XML API — Web Services Implementation Assignment

A **secured REST API using XML** built with Python + FastAPI that integrates with an external weather service (Open-Meteo), demonstrating real service-to-service communication.
 GIT-REPO : https://github.com/YashBiware/weather-api
## Features
- JWT Authentication (Register / Login)
- All requests and responses in **XML format**
- Protected endpoints (Bearer token required)
- External API integration — calls **Open-Meteo** (geocoding + weather forecast)
- Query history stored in memory

## Tech Stack
| Layer | Technology |
|---|---|
| Framework | FastAPI (Python) |
| Auth | JWT via `python-jose` |
| Password | BCrypt via `passlib` |
| Format | XML (request & response) |
| External API | Open-Meteo (free, no API key needed) |
| HTTP Client | `httpx` |

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET  | `/` | No | Service info |
| POST | `/auth/register` | No | Register new user (XML body) |
| POST | `/auth/login` | No | Login, get JWT token (XML body) |
| GET  | `/weather/{city}` | JWT | Get current weather (XML response) |
| GET  | `/weather/history/mine` | JWT | My query history (XML response) |

## How to Run Locally

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the server
```bash
python -m uvicorn main:app --reload
```

### 3. Open Swagger UI
```
http://localhost:8000/docs
```

## Postman Testing

### Register
- Method: `POST`
- URL: `http://localhost:8000/auth/register`
- Body → raw → XML:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<credentials>
    <username>yash</username>
    <password>1234</password>
</credentials>
```

### Response
```xml
<?xml version="1.0" encoding="UTF-8"?>
<response>
    <status>success</status>
    <message>Registration successful</message>
    <username>yash</username>
    <token>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...</token>
</response>
```

### Login
- Method: `POST`
- URL: `http://localhost:8000/auth/login`
- Same XML body as register

### Get Weather
- Method: `GET`
- URL: `http://localhost:8000/weather/Indore`
- Headers: `Authorization: Bearer <your_token>`

### Response
```xml
<?xml version="1.0" encoding="UTF-8"?>
<response>
    <status>success</status>
    <city>Indore</city>
    <country>India</country>
    <temperature_c>32.4</temperature_c>
    <windspeed_kmh>12.1</windspeed_kmh>
    <condition>Clear sky</condition>
    <queried_by>yash</queried_by>
    <source>Open-Meteo (open-meteo.com)</source>
</response>
```

### History
- Method: `GET`
- URL: `http://localhost:8000/weather/history/mine`
- Headers: `Authorization: Bearer <your_token>`

## External Service Integration

This API chains two Open-Meteo API calls behind the scenes:

Step 1 — Geocoding API:
  GET https://geocoding-api.open-meteo.com/v1/search?name=Indore
  returns latitude and longitude

Step 2 — Forecast API:
  GET https://api.open-meteo.com/v1/forecast?latitude=22.71&longitude=75.86&current_weather=true
  returns live weather data

## Project Structure
```
weather-api/
├── main.py           ← entire application
├── requirements.txt  ← dependencies
├── render.yaml       ← Render deployment config
└── README.md
```

## Live URL
Deployed on Render: https://weather-api-p3wd.onrender.com/
