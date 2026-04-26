# 🌤️ Weather API — Web Services Implementation Assignment

A **secured REST API** built with Python + FastAPI that integrates with an **external web service** (Open-Meteo), demonstrating real service-to-service communication.

## Features
- ✅ JWT Authentication (Register / Login)
- ✅ Protected endpoints (Bearer token required)
- ✅ External API integration — calls **Open-Meteo** (geocoding + weather forecast)
- ✅ Query history stored in memory
- ✅ Auto-generated **Swagger UI** at `/docs`

## Tech Stack
| Layer | Technology |
|---|---|
| Framework | FastAPI (Python) |
| Auth | JWT via `python-jose` |
| Password | BCrypt via `passlib` |
| External API | Open-Meteo (free, no key needed) |
| HTTP Client | `httpx` |

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET  | `/` | ❌ | Service info |
| POST | `/auth/register` | ❌ | Register new user |
| POST | `/auth/login` | ❌ | Login, get JWT token |
| GET  | `/weather/{city}` | ✅ JWT | Get current weather |
| GET  | `/weather/history/mine` | ✅ JWT | My query history |
| GET  | `/weather/history/all` | ✅ JWT | Last 10 global queries |

## How to Run

### 1. Clone & Install
```bash
git clone https://github.com/YOUR_USERNAME/weather-api.git
cd weather-api
pip install -r requirements.txt
```

### 2. Start the server
```bash
python -m uvicorn main:app --reload
```

### 3. Open in browser
```
http://localhost:8000/docs
```

## How to Test (using Swagger UI at /docs)

1. **Register** — call `POST /auth/register` with `{"username": "yash", "password": "1234"}`
2. **Copy the token** from the response
3. Click **Authorize 🔒** at the top → enter: `Bearer <your_token>`
4. Call `GET /weather/Indore` — get live weather!

## External Service Integration

This API calls **two Open-Meteo endpoints** behind the scenes:

```
Step 1 — Geocoding:
  GET https://geocoding-api.open-meteo.com/v1/search?name=Indore

Step 2 — Forecast:
  GET https://api.open-meteo.com/v1/forecast?latitude=22.71&longitude=75.86&current_weather=true
```

> Open-Meteo is 100% free with no API key needed: https://open-meteo.com

## Project Structure
```
weather-api/
├── main.py           ← entire application (single file)
├── requirements.txt  ← dependencies
└── README.md
```
