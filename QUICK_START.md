# 🚀 Quick Start Guide

Get your Vedic Astrology application running in minutes.

---

## 📋 Prerequisites

- ✅ Python 3.9+
- ✅ Node.js 18+
- ✅ Ollama running locally (`http://localhost:11434`)
- ✅ Internet connection (for city geolocation)

---

## ⚡ In 3 Steps

### Step 1: Start Backend

```bash
cd backend
python -m app.main
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Start Frontend

Open another terminal:

```bash
cd frontend
npm run dev
```

Expected output:
```
- Local:        http://localhost:3000
```

### Step 3: Use the Application

1. Open `http://localhost:3000`
2. Click **Login** → Enter `admin` / `admin`
3. Fill in:
   - **Date**: Pick your birth date
   - **Time**: Enter birth time (24-hour format)
   - **City**: Type your birth city
   - **Question**: Ask anything about the chart
4. Click **Generate Reading**

---

## 📊 What You'll See

### Left Panel (Your Input)
- Date and time selectors
- City field
- Question box
- Generate Reading button

### Right Panel (Results)
1. **Birth Chart** - Circular zodiac with planets
2. **Dasha Timeline** - Current astrological period
3. **AI Response** - Streaming interpretation

---

## 🔐 Login Credentials

```
Username: admin
Password: admin
```

---

## 📝 Example Birth Data

Try this to test:

```
Date of Birth:  1990-01-15
Time of Birth:  10:30
City:          New York
Question:      What does my chart reveal about my career?
```

---

## ✨ Features

✅ **Birth Chart Visualization** - 12 Rashis with planets  
✅ **Dasha Calculator** - Current & future periods  
✅ **AI Interpretation** - Real-time streaming  
✅ **Mobile Responsive** - Works on all devices  
✅ **Dark & Light Mode** - Automatic detection  

---

## 🧪 Test It Works

### Backend API
```bash
curl -X POST http://localhost:8000/api/chart \
  -H "Content-Type: application/json" \
  -d '{
    "date_of_birth": "1990-01-15",
    "time_of_birth": "10:30",
    "city_name": "New York"
  }'
```

Should return JSON with `planets`, `lagna`, `houses`, and `dasha`.

### Frontend
- Opens without errors
- Responds to form inputs
- Displays birth chart
- Streams AI response

---

## 🆘 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000
# Kill the process or use different port
```

### Frontend won't start
```bash
# Clear cache and reinstall
rm -r node_modules package-lock.json
npm install
npm run dev
```

### No AI response?
- Ensure Ollama is running: `ollama serve`
- Check Ollama is accessible: `curl http://localhost:11434`

### Chart shows "Error"?
- Verify city name is correct and spelled right
- Check internet connection (for geolocation)
- Review browser console for details (F12)

---

## 📚 Next Steps

### Ready to explore more?
See **TECHNICAL_REFERENCE.md** for:
- Architecture overview
- Component details
- API documentation
- Customization guide
- How Dasha works

### Want to understand the code?
- **backend/app/engine.py** - Chart calculations
- **backend/app/dasha.py** - Dasha system
- **frontend/components/chart-display.tsx** - Chart visualization
- **frontend/components/dasha-table.tsx** - Dasha display

---

## 🎯 Common Tasks

### Change the AI model
Edit `/backend/.env`:
```
MODEL_NAME=neural-chat  # or mistral, zephyr, etc.
```

### Customize colors
Edit `/frontend/components/dasha-table.tsx`:
```typescript
const PLANET_COLORS = {
  "Sun": "#your-color",
  "Moon": "#your-color",
  // ... etc
}
```

### Change port numbers
Backend: `-port 8001` in `app.main`  
Frontend: `PORT=3001 npm run dev`

---

## ✅ Quick Checklist

- [ ] Backend running (`http://localhost:8000`)
- [ ] Frontend running (`http://localhost:3000`)
- [ ] Can login with admin/admin
- [ ] Can enter birth data
- [ ] Chart displays correctly
- [ ] Dasha table shows periods
- [ ] AI response streams

All checked? **You're ready to go!** 🎉

---

## 💬 Need Help?

1. Check **TECHNICAL_REFERENCE.md** for detailed docs
2. Review browser console (F12 → Console tab)
3. Check backend logs in terminal
4. Verify all prerequisites are installed

---

## 🎓 Understand the System

### Data Flow
```
User Input → Backend API → 
  Chart Calculation → Dasha Calculation → 
  AI Streaming → Frontend Display
```

### Birth Chart Shows
- 12 Rashis (zodiac signs)
- 9 Planets (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu)
- 12 Houses (life areas)
- Lagna (Ascendant)

### Dasha Shows
- **Maha Dasha**: 9-year major period
- **Antara Dasha**: Monthly sub-period (within Maha)
- **Days remaining**: How long current period lasts
- **Progress bar**: Visual completion indicator

---

**Ready? Go to http://localhost:3000 and start exploring!** ✨
