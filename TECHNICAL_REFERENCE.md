# 🔧 Technical Reference Guide

Complete technical documentation for the Vedic Astrology application.

---

## 📑 Table of Contents

1. [Architecture](#architecture)
2. [Components](#components)
3. [API Endpoints](#api-endpoints)
4. [Database Schema](#database-schema)
5. [Dasha System](#dasha-system)
6. [Customization](#customization)
7. [Troubleshooting](#troubleshooting)

---

## Architecture

### Tech Stack

**Frontend**
- Next.js 14.2 (React 18)
- TypeScript
- Tailwind CSS 3.4
- NextAuth.js 4.24
- SVG for charting

**Backend**
- FastAPI (Python web framework)
- SQLAlchemy ORM
- Swiss Ephemeris (pyswisseph)
- Ollama (local LLM)
- Geopy + TimezoneFinder

**Database**
- SQLite
- JSON field storage
- Prisma schema (frontend)
- SQLAlchemy models (backend)

### System Flow

```
┌─────────────────────────────────────────────────────────┐
│ Frontend (Next.js @ localhost:3000)                    │
│  ├─ Auth (NextAuth with admin/admin credentials)      │
│  ├─ Form (Date, Time, City, Question)                 │
│  ├─ Components:                                         │
│  │  ├─ chart-chat.tsx (main UI)                        │
│  │  ├─ chart-display.tsx (SVG chart)                   │
│  │  ├─ dasha-table.tsx (timeline)                      │
│  │  └─ auth-buttons.tsx (login/logout)               │
│  └─ Styles (Tailwind CSS)                              │
└──────────┬──────────────────────────────────────────────┘
           │
           │ HTTP/JSON
           │
┌──────────▼──────────────────────────────────────────────┐
│ Backend (FastAPI @ localhost:8000)                     │
│  ├─ API Endpoints:                                      │
│  │  ├─ GET  /api/health                                │
│  │  ├─ POST /api/chart (chart + dasha)                │
│  │  ├─ POST /api/chart/stream (chart + AI stream)    │
│  │  └─ POST /api/auth/login (credentials)             │
│  ├─ Services:                                           │
│  │  ├─ engine.py (chart calculations)                  │
│  │  ├─ dasha.py (Dasha timing)                         │
│  │  ├─ database.py (data persistence)                 │
│  │  └─ models.py (data models)                         │
│  └─ External APIs:                                      │
│     ├─ Nominatim (city → coordinates)                 │
│     ├─ Swiss Ephemeris (planetary data)               │
│     └─ Ollama (AI streaming)                           │
└──────────┬──────────────────────────────────────────────┘
           │
           │
┌──────────▼──────────────────────────────────────────────┐
│ Data Layer                                              │
│  ├─ SQLite Database (data/vedic_astrology.db)          │
│  ├─ Tables:                                             │
│  │  ├─ User (auth info)                                │
│  │  ├─ SavedChart (chart history)                      │
│  │  └─ ChatLog (responses)                             │
│  └─ JSON Fields:                                        │
│     ├─ chart_json (full planet data + dasha)           │
│     └─ response_text (AI interpretation)               │
└──────────────────────────────────────────────────────────┘
```

---

## Components

### Frontend Components

#### `chart-chat.tsx`
**Purpose**: Main UI container for chart input and results

**Key Features**:
- Form with date/time/city/question (side-by-side layout)
- Responsive grid layout
- State management for chart, answer, status
- Calls `/api/chart/stream` for combined response

**State Variables**:
```typescript
dateOfBirth: string     // ISO format (YYYY-MM-DD)
timeOfBirth: string     // 24-hour format (HH:MM)
cityName: string        // City name
question: string        // User question
answer: string          // Streamed AI response
status: Status          // idle | streaming | error | done
chart: Chart | null     // Birth chart data
```

**Props**: None (uses next-auth session)

**Methods**:
- `handleSubmit()` - POST to `/api/chart/stream`
- `fetchChart()` - POST to `/api/chart` separately
- Extracts card JSON from first response chunk

#### `chart-display.tsx`
**Purpose**: SVG visualization of birth chart

**Key Features**:
- Circular zodiac wheel (290x290px)
- 12 Rashis with symbols
- Grid lines for houses
- Planets positioned at calculated degrees
- Retrograde indicators (R badge)
- Detail table below chart

**Props**:
```typescript
interface Props {
  planets: Planet[]
  lagna: { rashi: string; degree: number }
  houses: House[]
}
```

**Calculations**:
```
Angle on chart = (degree / 30) * 30 degrees
                // Maps zodiac to 360° circle
Radius for planet = 70px from center
```

**Planet Symbols**:
```typescript
Sun: ☉ (130, 183)
Moon: ☽ (130, 183)
Mars: ♂ (255, 0)
Mercury: ☿ (0, 128)
Jupiter: ♃ (0, 128)
Venus: ♀ (0, 128)
Saturn: ♄ (128, 128)
Rahu: ☊
Ketu: ☋
```

**Rashi Symbols** (12 zodiac signs):
```
♈ Mesha (Aries)
♉ Vrishabha (Taurus)
♊ Mithuna (Gemini)
♋ Kataka (Cancer)
♌ Simha (Leo)
♍ Kanya (Virgo)
♎ Tula (Libra)
♏ Vrishchika (Scorpio)
♐ Dhanus (Sagittarius)
♑ Makara (Capricorn)
♒ Kumbha (Aquarius)
♓ Meenai (Pisces)
```

#### `dasha-table.tsx`
**Purpose**: Display dasha timeline and current period

**Key Features**:
- Current Maha Dasha card (planet, duration, dates)
- Progress bar with percentage
- Antara Dashas list (all 9 sub-periods)
- Next Maha Dasha preview
- Upcoming 5 Dashas timeline

**Props**:
```typescript
interface DashaData {
  current_maha_dasha: {
    planet: string
    start_date: string
    end_date: string
    duration_years: number
    is_current: boolean
    remaining_days: number
  }
  antara_dashas: AntaraDasha[]
  next_maha_dasha: Dasha
  upcoming_maha_dashas: Dasha[]
}
```

**Functions**:
```typescript
formatDate(isoDate: string): string
// Converts "2024-01-15" to "Jan 15, 2024"

getProgressPercentage(start: string, end: string): number
// Calculates 0-100 progress of current period

PLANET_COLORS: Record<string, string>
// Visual differentiation for each planet
```

#### `auth-buttons.tsx`
**Purpose**: Login/logout interface

**Features**:
- Uses NextAuth session
- Shows username when logged in
- Logout button with redirect
- Login modal (CredentialsProvider)

---

### Backend Components

#### `engine.py`
**Purpose**: Chart calculations and ephemeris

**Key Functions**:

```python
build_chart_from_coordinates(
    local_dt: datetime,
    lat: float,
    lon: float,
    timezone_name: str
) -> dict
```
Returns:
```python
{
  'planets': [
    {'name': 'Sun', 'rashi': 'Capricorn', 'degree': 23.45, 
     'nakshatra': 'Uttarashada', 'pada': 2, 'retrograde': False},
    # ... 8 more planets
  ],
  'lagna': {'rashi': 'Leo', 'degree': 15.20},
  'houses': [{'number': 1, 'rashi': 'Leo'}, ...],
  'dasha': { /* see Dasha section */ }
}
```

**Process**:
1. Create ephemeris coordinates
2. Calculate all 9 planets
3. Calculate Lagna (ascendant)
4. Calculate 12 houses
5. Extract Moon's Nakshatra
6. Calculate Dasha data
7. Return combined result

#### `dasha.py`
**Purpose**: Vimsottari Dasha calculations

**Key Functions**:

```python
calculate_dasha(
    birth_date: date,
    moon_nakshatra: str,
    moon_nakshatra_pada: int
) -> dict
```

**Returns**:
```python
{
  'current_maha_dasha': {
    'planet': 'Jupiter',
    'start_date': '2023-06-15',
    'end_date': '2039-06-15',
    'duration_years': 16,
    'remaining_days': 2847,
    'is_current': True
  },
  'antara_dashas': [
    {
      'planet': 'Jupiter',
      'start_date': '2023-06-15',
      'end_date': '2024-04-15',
      'duration': '10m 0d',
      'is_current': True,
      'remaining_days': 286
    },
    # ... 8 more antara dashas
  ],
  'next_maha_dasha': {...},
  'upcoming_maha_dashas': [...]
}
```

**Dasha Sequence** (9 periods):
```python
MAHA_DASHA_ORDER = [
  "Ketu", "Venus", "Sun", "Moon", "Mars",
  "Rahu", "Jupiter", "Saturn", "Mercury"
]

MAHA_DASHA_DURATION = {
  "Ketu": 7,     # years
  "Venus": 20,
  "Sun": 6,
  "Moon": 10,
  "Mars": 7,
  "Rahu": 18,
  "Jupiter": 16,
  "Saturn": 19,
  "Mercury": 17
}  # Total: 120-year cycle
```

**Nakshatra Mapping** (27 lunar mansions):
```
Ketu:     0-13.33°
Venus:   13.33-26.67°
Sun:     26.67-40°
Moon:    40-53.33°
Mars:    53.33-66.67°
Rahu:    66.67-80°
Jupiter: 80-93.33°
Saturn:  93.33-106.67°
Mercury: 106.67-120°
```

**Antara Dasha Calculation**:
- Divides Maha Dasha into 9 sub-periods
- Each planet gets portion based on its duration ratio
- Example: Jupiter (16y) Maha Dasha × Venus (20/120) = 2.67 years Venus Antara

#### `main.py`
**Purpose**: FastAPI application setup

**Endpoints**:
```
GET  /api/health         - Server status
POST /api/chart          - Get chart + dasha (no streaming)
POST /api/chart/stream   - Get chart + stream AI response
POST /api/auth/login     - Authenticate user
```

#### `models.py`
**Purpose**: SQLAlchemy data models

**Tables**:
```python
class User(Base):
    id: int
    email: str
    password_hash: str

class SavedChart(Base):
    id: int
    user_id: int
    date_of_birth: string
    time_of_birth: string
    city_name: string
    chart_json: dict      # Stores full chart + dasha

class ChatLog(Base):
    id: int
    user_id: int
    chart_id: int
    question: string
    response_text: string
    chart_json: dict      # Chart reference
```

---

## API Endpoints

### POST /api/chart
**Get birth chart + Dasha (no streaming)**

**Request**:
```json
{
  "date_of_birth": "1990-01-15",
  "time_of_birth": "10:30:00",
  "city_name": "New York",
  "user_email": "admin@localhost",
  "user_name": "Admin",
  "question": ""
}
```

**Response** (200):
```json
{
  "calculation": {...},
  "planets": [...],
  "lagna": {...},
  "houses": [...],
  "dasha": {
    "current_maha_dasha": {...},
    "antara_dashas": [...],
    "next_maha_dasha": {...},
    "upcoming_maha_dashas": [...]
  }
}
```

**Errors**:
- 400: Invalid date/time format
- 404: City not found
- 500: Calculation error

---

### POST /api/chart/stream
**Get chart + stream AI interpretation**

**Request** (same as /api/chart, but with question)

**Response** (200):
Streams Server-Sent Events:
```
event: message
data: {"planets": [...], "dasha": {...}}

event: message
data: Jupiter in your chart suggests expansion...

event: message
data: This period will bring opportunities...
```

**Process**:
1. Calculate chart
2. Send JSON first
3. Stream AI response token by token
4. Save to database

---

### POST /api/auth/login
**Authenticate with credentials**

**Request**:
```json
{
  "username": "admin",
  "password": "admin"
}
```

**Response** (200):
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

---

## Database Schema

### Users
```sql
CREATE TABLE user (
  id INTEGER PRIMARY KEY,
  email VARCHAR UNIQUE NOT NULL,
  password_hash VARCHAR NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### SavedCharts
```sql
CREATE TABLE saved_chart (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  date_of_birth VARCHAR NOT NULL,
  time_of_birth VARCHAR NOT NULL,
  city_name VARCHAR NOT NULL,
  chart_json JSON,           -- Full chart + dasha
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(user_id) REFERENCES user(id)
);
```

### ChatLogs
```sql
CREATE TABLE chat_log (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  chart_id INTEGER,
  question VARCHAR NOT NULL,
  response_text TEXT,
  chart_json JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(user_id) REFERENCES user(id),
  FOREIGN KEY(chart_id) REFERENCES saved_chart(id)
);
```

---

## Dasha System

### What is Dasha?

Dasha is a major timing system in Vedic astrology. It divides life into periods ruled by different planets, helping predict life events and timings.

### Vimsottari Dasha (120-year cycle)

**Key Concept**:
- 9 planets rule specific periods
- Sequence repeats every 120 years
- Moon's Nakshatra (lunar mansion) determines your starting planet

### How It Works

1. **Find Moon's Nakshatra** (27 lunar mansions)
   ```
   Nakshatra = Moon's ecliptic longitude / 13.33°
   Range: 0-27
   ```

2. **Map to Dasha Planet**
   ```
   Nakshatra 0-2 → Ketu Dasha (7 years)
   Nakshatra 3-5 → Venus Dasha (20 years)
   Nakshatra 6-8 → Sun Dasha (6 years)
   ... etc
   ```

3. **Calculate Current Period**
   ```
   Elapsed years since birth → Which Dasha are we in?
   Remaining = End date - Today
   ```

4. **Calculate Sub-periods (Antara Dasha)**
   ```
   Maha Dasha duration = Dasha Year 1 to Start
   Antara Dasha = Maha Dasha / 9 periods
   Each period gets duration based on planet's ratio
   ```

### Example: Birth Jan 15, 1990 @ 10:30 AM

```
Moon Position: 260° (Scorpio, Scales constellation)
Moon Nakshatra: 260 / 13.33 ≈ 19.5 → Nakshatra 20 (Purvashadha)

Nakshatra 20 → Jupiter Dasha starts
Jupiter Dasha: 16 years
Current age: 34 years
Status: In Jupiter Dasha started 2008, ends 2024

Antara Dashas in Jupiter:
- Jupiter (1.78 years): 2008-2009
- Saturn (1.90 years): 2009-2010
- Mercury (1.70 years): 2010-2011
- ... etc
```

### Dasha Predictions

Each Dasha brings different energy:
- **Ketu**: Spiritual, introspective, losses
- **Venus**: Relationships, wealth, comfort
- **Sun**: Authority, confidence, leadership
- **Moon**: Emotions, family, travel
- **Mars**: Energy, aggression, conflicts
- **Rahu**: Growth, desires, material gains
- **Jupiter**: Expansion, luck, success
- **Saturn**: Challenges, discipline, karma
- **Mercury**: Communication, intellect, business

---

## Customization

### Change Admin Password

Edit `backend/app/main.py`:
```python
# Change in NextAuth config
credentials = {
    "admin": {
        "password": "your-new-password"
    }
}
```

### Change AI Model

Edit `backend/.env`:
```
MODEL_NAME=neural-chat
# or: mistral, zephyr, orca, llama2, phi
```

### Customize Colors

Edit `frontend/components/dasha-table.tsx`:
```typescript
const PLANET_COLORS: Record<string, string> = {
  "Sun": "#ff9500",      // Orange
  "Moon": "#9ca3af",     // Gray
  "Mars": "#dc2626",     // Red
  "Mercury": "#06b6d4",  // Cyan
  "Jupiter": "#eab308",  // Yellow
  "Venus": "#ec4899",    // Pink
  "Saturn": "#8b5cf6",   // Purple
  "Rahu": "#10b981",     // Green
  "Ketu": "#f59e0b"      // Amber
};
```

### Change Chart Size

Edit `frontend/components/chart-display.tsx`:
```typescript
// Current: 290x290px
const chartSize = 350; // Make it bigger
```

### Add More Birth Details

Edit `frontend/components/chart-chat.tsx`:
```typescript
// Add new fields
const [fatherName, setFatherName] = useState("");
const [motherName, setMotherName] = useState("");

// Update form
<input
  placeholder="Father's name (optional)"
  value={fatherName}
  onChange={(e) => setFatherName(e.target.value)}
/>
```

---

## Troubleshooting

### Issue: "City not found"

**Cause**: Nominatim geolocation service doesn't recognize the city

**Solution**:
1. Use full city name: "New York City" instead of "NYC"
2. Add state/country: "Delhi, India"
3. Check internet connection
4. Retry with different spelling

**Debug**:
```bash
# Test nominatim directly
curl "https://nominatim.openstreetmap.org/search?city=NewYork&format=json"
```

---

### Issue: No AI response (hangs)

**Cause**: Ollama not running or unreachable

**Solution**:
1. Start Ollama: `ollama serve`
2. Check it's running: `curl http://localhost:11434/api/tags`
3. Pull model if needed: `ollama pull neural-chat`
4. Check firewall allows localhost:11434

**Debug**:
```bash
# Verify connection
netstat -ano | findstr :11434  # Windows
lsof -i :11434                 # macOS/Linux

# Test API directly
curl http://localhost:11434/api/tags
```

---

### Issue: Birth date gives wrong chart

**Cause**: Time zone conversion error or incorrect entry

**Solution**:
1. Verify time zone auto-detection
2. Convert to local time if using UTC
3. Use 24-hour format (15:30 not 3:30 PM)
4. Check calendar date is correct

**Debug**:
```bash
# Check what timezone was detected
# Look in backend logs for: "Timezone: Asia/Kolkata"
```

---

### Issue: Frontend port already in use

**Solution**:
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :3000
kill -9 <PID>

# Or use different port
PORT=3001 npm run dev
```

---

### Issue: Database locked error

**Cause**: Multiple FastAPI instances writing simultaneously

**Solution**:
1. Restart backend: Kill process and restart
2. Check for `.db-journal` file and delete it
3. Use single backend instance

```bash
# Find all Python processes
tasklist | findstr python

# Kill specific process
taskkill /PID <PID> /F
```

---

### Issue: Chart displays but no Dasha table

**Cause**: Dasha calculation failed silently

**Debug**:
1. Check browser console (F12)
2. Check `chart.dasha` exists in response
3. Verify Moon Nakshatra was extracted

**Backend log**:
```python
# Add this in engine.py to debug
print(f"Moon Nakshatra: {moon_nakshatra}")
print(f"Dasha calculation result: {dasha_data}")
```

---

### Issue: Responsive design broken on mobile

**Solution**:
1. Check viewport meta tag in `frontend/app/layout.tsx`
2. Test with Chrome DevTools (F12 → Device Toolbar)
3. Verify Tailwind breakpoints

Edit `frontend/components/chart-chat.tsx`:
```typescript
// Change grid breakpoint
<div className="grid gap-5 lg:grid-cols-[390px_minmax(0,1fr)]">
//                  ^^ Mobile: stacks, Desktop: side-by-side
```

---

## Performance Optimization

### Chart Calculation: 200-500ms
- Ephemeris lookup (fastest)
- Coordinate conversion (fast)
- Dasha calculation (medium)

### AI Streaming: 5-30 seconds
- Depends on Ollama model
- Network latency
- Response length

### Frontend Rendering: 100-300ms
- SVG chart rendering
- React re-renders
- CSS animations

**Optimization Tips**:
1. Use smaller AI model (phi vs neural-chat)
2. Cache calculations if same inputs
3. Pre-generate common charts
4. Optimize SVG rendering (simplify paths)

---

## Security

### Authentication
- NextAuth.js with CredentialsProvider
- JWT tokens (no database session)
- Admin/admin default (change for production)

### Data Protection
- SQLite with no encryption (add in production)
- JSON fields store sensitive data
- No rate limiting (add for production)

### Environment Variables
```
DATABASE_URL=sqlite:///data/vedic_astrology.db
NEXTAUTH_SECRET=your-secret-key
NEXTAUTH_URL=http://localhost:3000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
MODEL_NAME=neural-chat
```

### Production Checklist
- [ ] Change admin password
- [ ] Set NEXTAUTH_SECRET to random value
- [ ] Enable HTTPS (not HTTP)
- [ ] Add database encryption
- [ ] Set up rate limiting
- [ ] Add input validation
- [ ] Sanitize user inputs
- [ ] Set up logging/monitoring

---

## File Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app + endpoints
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── engine.py            # Chart calculation
│   ├── dasha.py             # Dasha calculation
│   ├── prompts.py           # AI prompts
│   └── init_db.py           # Database initialization
├── tests/
│   └── test_engine.py
├── requirements.txt
└── .env

frontend/
├── app/
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Home page
│   └── admin/
│       └── page.tsx         # Admin page
├── components/
│   ├── chart-chat.tsx       # Main UI
│   ├── chart-display.tsx    # Chart visualization
│   ├── dasha-table.tsx      # Dasha display
│   └── auth-buttons.tsx     # Login/logout
├── lib/
│   └── prisma.ts            # Prisma client
├── pages/
│   └── api/
│       └── auth/
│           └── [...nextauth].ts
├── prisma/
│   └── schema.prisma
├── package.json
├── tsconfig.json
└── tailwind.config.ts

data/
└── vedic_astrology.db       # SQLite database

logs/
└── (log files)
```

---

## Additional Resources

### Learning More
- Vedic Astrology basics: [QUICK_START.md](QUICK_START.md)
- Swiss Ephemeris docs: https://www.astro.com/swisseph/
- NextAuth.js docs: https://next-auth.js.org/
- FastAPI docs: https://fastapi.tiangolo.com/
- Tailwind CSS: https://tailwindcss.com/

### API Testing
Use Postman or curl:
```bash
# Get chart
curl -X POST http://localhost:8000/api/chart \
  -H "Content-Type: application/json" \
  -d '{"date_of_birth":"1990-01-15","time_of_birth":"10:30","city_name":"NY"}'

# Check health
curl http://localhost:8000/api/health
```

---

**Last Updated**: April 29, 2026  
**Version**: 1.0.0
