# Dasha Astro

Dasha Astro is a FastAPI + Next.js Vedic astrology workspace with Swiss Ephemeris chart calculation, D1/D9/D10 varga display, Vimshottari dasha timing, Indian location lookup, and Gemini-powered chart interpretation.

## Stack

- Frontend: Next.js, React, Tailwind, NextAuth, Prisma, SQLite
- Backend: FastAPI, SQLAlchemy, SQLite, geopy, timezonefinder, pyswisseph
- AI: Google Gemini through `GEMINI_API_KEY`

## Start The App

```powershell
.\DashaAstro.exe
```

The launcher starts FastAPI on `http://localhost:8000`, starts Next.js on `http://localhost:3000`, opens the browser, and writes runtime logs to `logs/`.

Useful checks:

```powershell
.\DashaAstro.exe --status
.\DashaAstro.exe --check-llm
```

## Backend Setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m app.init_db
python -m pytest
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Set your Gemini key in `backend/.env`:

```text
GEMINI_API_KEY=your-key-here
GEMINI_MODEL=gemini-2.5-flash
```

## Frontend Setup

```powershell
cd frontend
npm install
Copy-Item .env.local.example .env.local
npx prisma generate
npx prisma db push
npm run dev
```

Open `http://localhost:3000`.

## Key Endpoints

- `GET http://localhost:8000/health`
- `GET http://localhost:8000/api/location/search?query=Tanuku`
- `POST http://localhost:8000/api/chart`
- `POST http://localhost:8000/api/chart/stream`
- `GET http://localhost:8000/admin/logs`
- `DELETE http://localhost:8000/admin/logs`

## Calculation Notes

- Sidereal zodiac with Swiss Ephemeris.
- Ayanamsha: True Chitra Paksha Lahiri (`SIDM_TRUE_CITRA`).
- Rahu: True Node by default.
- Houses: Whole Sign.
- Varga display: D1 Rashi, D9 Navamsha, D10 Dashamsha.
- D10 follows the Parashari odd/even sign counting rule.

## Validation

The backend tests include a regression fixture from `C:\Users\Varun\Downloads\VarunJagannatha Astro.pdf` for the October 1, 1999 Tanuku chart. The fixture checks D1 longitudes and D9 signs for the main grahas within one arc minute. Rahu/Ketu are intentionally excluded from that PDF fixture because the PDF values match Mean Node while Dasha Astro is configured for True Node.
