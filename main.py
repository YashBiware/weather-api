"""
Web Services Implementation Assignment
Secured REST API with XML + External Service Integration
External API: Open-Meteo (free, no key needed) — https://open-meteo.com
"""

from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import httpx

# ── Config ─────────────────────────────────────────────────────────────────────
SECRET_KEY = "my-super-secret-key-change-in-production"
ALGORITHM  = "HS256"
TOKEN_EXPIRY_HOURS = 24

# ── In-memory stores ───────────────────────────────────────────────────────────
users_db: dict = {}
history_db: list = []

# ── Auth helpers ───────────────────────────────────────────────────────────────
pwd    = CryptContext(schemes=["bcrypt"])
bearer = HTTPBearer()

def hash_password(plain): return pwd.hash(plain)
def verify_password(plain, hashed): return pwd.verify(plain, hashed)

def create_token(username):
    payload = {"sub": username, "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        payload  = jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None or username not in users_db:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# ── XML helpers ────────────────────────────────────────────────────────────────
def xml_response(data: dict, root_tag="response"):
    root = ET.Element(root_tag)
    for key, value in data.items():
        ET.SubElement(root, key).text = str(value)
    xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode")
    return Response(content=xml_str, media_type="application/xml")

def parse_xml_body(body: bytes):
    try:
        root = ET.fromstring(body.decode("utf-8"))
        return {child.tag: child.text for child in root}
    except ET.ParseError:
        raise HTTPException(status_code=400, detail="Invalid XML body")

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(title="Weather XML API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ── Auth ───────────────────────────────────────────────────────────────────────
@app.post("/auth/register", tags=["Auth"])
async def register(request: Request):
    data     = parse_xml_body(await request.body())
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    if not username or not password:
        return xml_response({"status": "error", "message": "Username and password required"})
    if username in users_db:
        return xml_response({"status": "error", "message": "Username already taken"})
    if len(password) < 4:
        return xml_response({"status": "error", "message": "Password must be at least 4 characters"})
    users_db[username] = hash_password(password)
    return xml_response({"status": "success", "message": "Registration successful", "username": username, "token": create_token(username)})

@app.post("/auth/login", tags=["Auth"])
async def login(request: Request):
    data     = parse_xml_body(await request.body())
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    hashed   = users_db.get(username)
    if not hashed or not verify_password(password, hashed):
        return xml_response({"status": "error", "message": "Invalid username or password"})
    return xml_response({"status": "success", "message": "Login successful", "username": username, "token": create_token(username)})

# ── Weather ────────────────────────────────────────────────────────────────────
@app.get("/weather/history/mine", tags=["Weather"])
def my_history(username: str = Depends(get_current_user)):
    mine = [h for h in history_db if h["queried_by"] == username]
    root = ET.Element("response")
    ET.SubElement(root, "username").text = username
    ET.SubElement(root, "total").text    = str(len(mine))
    hist_el = ET.SubElement(root, "history")
    for h in mine:
        entry = ET.SubElement(hist_el, "entry")
        for k, v in h.items():
            ET.SubElement(entry, k).text = str(v)
    xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode")
    return Response(content=xml_str, media_type="application/xml")

@app.get("/weather/{city}", tags=["Weather"])
def get_weather(city: str, username: str = Depends(get_current_user)):
    geo = httpx.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json", timeout=10)
    results = geo.json().get("results")
    if not results:
        return xml_response({"status": "error", "message": f"City '{city}' not found"})
    loc      = results[0]
    lat, lon = loc["latitude"], loc["longitude"]
    cityname = loc["name"]
    country  = loc.get("country", "")

    w = httpx.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&temperature_unit=celsius", timeout=10)
    current   = w.json()["current_weather"]
    condition = weather_code_to_text(current["weathercode"])

    history_db.append({"queried_by": username, "city": cityname, "country": country,
                        "temperature_c": current["temperature"], "windspeed_kmh": current["windspeed"],
                        "condition": condition, "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")})

    return xml_response({"status": "success", "city": cityname, "country": country,
                         "latitude": lat, "longitude": lon, "temperature_c": current["temperature"],
                         "windspeed_kmh": current["windspeed"], "condition": condition,
                         "queried_by": username, "source": "Open-Meteo (open-meteo.com)"})

@app.get("/", tags=["Info"])
def root():
    return xml_response({"message": "Weather XML API is running", "docs": "/docs"})

def weather_code_to_text(code):
    if code == 0:  return "Clear sky"
    if code <= 2:  return "Partly cloudy"
    if code == 3:  return "Overcast"
    if code <= 49: return "Foggy"
    if code <= 59: return "Drizzle"
    if code <= 69: return "Rain"
    if code <= 79: return "Snow"
    if code <= 84: return "Rain showers"
    return "Thunderstorm"