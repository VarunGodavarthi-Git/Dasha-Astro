# Admin Login Testing Guide

## Prerequisites
- Node.js and npm installed
- Python 3.8+ installed
- SQLite database (created automatically)
- NEXTAUTH_SECRET generated

## Test Scenario: Complete Admin Workflow

### Phase 1: Environment Setup ✅

#### 1.1 Generate NEXTAUTH_SECRET
```powershell
# In PowerShell (Windows)
[Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetRandomBytes(32))
```

#### 1.2 Create Frontend `.env.local`
```env
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=<your-generated-secret>
DATABASE_URL=file:../../data/vedic_astrology.db

GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
FACEBOOK_CLIENT_ID=
FACEBOOK_CLIENT_SECRET=

ADMIN_EMAIL=admin@localhost
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

#### 1.3 Create Backend `.env`
```env
BACKEND_DATABASE_URL=sqlite:///../data/vedic_astrology.db
FRONTEND_ORIGIN=http://localhost:3000
ADMIN_EMAIL=admin@localhost
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:1b
OLLAMA_NUM_CTX=4096
OLLAMA_NUM_PREDICT=600
OLLAMA_KEEP_ALIVE=2m
NOMINATIM_USER_AGENT=vedic-astrology-local-fde
```

---

### Phase 2: Backend Setup & Testing ✅

#### 2.1 Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### 2.2 Start Backend Server
```bash
python -m app.main
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

#### 2.3 Verify Backend Health
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{"status": "ok", "ollama_model": "gemma3:1b"}
```

#### 2.4 Check Admin Endpoint (Should Fail - No Auth)
```bash
curl http://localhost:8000/admin/logs
```

**Expected Response:**
```json
{"detail": "Admin access required."}
```

---

### Phase 3: Frontend Setup & Testing ✅

#### 3.1 Install Frontend Dependencies
```bash
cd frontend
npm install
```

#### 3.2 Initialize Database
```bash
npm run prisma:generate
npm run prisma:push
```

**Expected behavior:** Database schema created without errors

#### 3.3 Start Frontend Development Server
```bash
npm run dev
```

**Expected Output:**
```
> local-vedic-astrology-frontend@0.1.0 dev
> powershell -ExecutionPolicy Bypass -File ./scripts/next.ps1 dev

> next dev
- ready started server on 0.0.0.0:3000, url: http://localhost:3000
```

---

### Phase 4: UI Login Testing ✅

#### Test 4.1: Check Initial UI State
1. Navigate to `http://localhost:3000`
2. **Expected:** See "Chart Console" page with three auth buttons:
   - "Admin" (dark)
   - "Google" (dark)
   - "Facebook" (light)

#### Test 4.2: Open Admin Login Modal
1. Click "Admin" button
2. **Expected:** Modal appears with:
   - Title: "Admin Login"
   - Username input field
   - Password input field
   - "Sign In" button (disabled if fields empty)
   - "Cancel" button

#### Test 4.3: Test Invalid Credentials
1. Enter wrong username: `user`
2. Enter any password
3. Click "Sign In"
4. **Expected:** Modal stays open, form still shows fields (login fails silently)

#### Test 4.4: Test Correct Credentials ✨
1. Enter username: `admin`
2. Enter password: `admin`
3. Click "Sign In"
4. **Expected Results:**
   - Modal closes
   - User profile appears showing "Admin" as role
   - "Admin" button visible in header
   - "Sign out" button appears

#### Test 4.5: Verify User Profile Display
```
Expected display in top-right:
┌─────────────────┐
│ Admin           │ <- Name
│ ADMIN           │ <- Role
│ [Sign out]      │ <- Button
└─────────────────┘
```

---

### Phase 5: Admin Dashboard Testing ✅

#### Test 5.1: Access Admin Dashboard
1. Click "Admin" link in top-right corner
2. **Expected:** 
   - Navigate to `/admin` page
   - See "Safety & Governance" header
   - See "Interaction Logs" title
   - See three buttons: "Console" (back), "Refresh", "Clear Logs"
   - Empty logs area shows "No logs yet."

#### Test 5.2: Refresh Logs Button
1. Click "Refresh" button
2. **Expected:** Loading state briefly shown, then "No logs yet." message

#### Test 5.3: Verify Auth Headers
- Frontend sends: `x-user-email: admin@localhost`
- Backend validates against `ADMIN_EMAIL` environment variable
- **Expected:** Request succeeds (200 OK)

---

### Phase 6: Chat Interaction Testing ✅

#### Test 6.1: Create Chat Log
1. Return to main console (click "Console" button or navigate to `/`)
2. Fill in birth chart data:
   - Date: e.g., "1990-01-15"
   - Time: e.g., "10:30"
   - City: e.g., "New York"
   - Question: e.g., "What does my chart reveal?"
3. Click "Calculate & Ask"
4. **Expected:** Chat response received

#### Test 6.2: Check Admin Logs Updated
1. Return to Admin page
2. Click "Refresh"
3. **Expected:** New log entry appears with:
   - ID (auto-incremented)
   - User email/name
   - City name
   - Timestamp
   - Expandable prompt/response sections

#### Test 6.3: View Log Details
1. Click on any log entry
2. **Expected:** Expands to show:
   - Full prompt text in left panel
   - Full AI response in right panel
   - Both with scrollable content

---

### Phase 7: Admin Functions Testing ✅

#### Test 7.1: Clear Logs
1. Ensure at least one log exists (from Phase 6)
2. Click "Clear Logs" button
3. **Expected:**
   - Red confirmation action
   - Message shows: "Cleared X log entries."
   - Logs table becomes empty

#### Test 7.2: Refresh After Clear
1. Click "Refresh"
2. **Expected:** Still shows "No logs yet."

---

### Phase 8: Session & Logout Testing ✅

#### Test 8.1: Sign Out
1. Click "Sign out" button
2. **Expected:**
   - User profile disappears
   - Auth buttons reappear (Admin, Google, Facebook)
   - Redirected to home page

#### Test 8.2: Verify Admin Access Denied
1. Try to access `/admin` while logged out
2. **Expected:** "Admin Access Required" page with:
   - Shield icon
   - Message: "Sign in with the configured admin email."
   - "Return" button

---

### Phase 9: Security Testing ✅

#### Test 9.1: JWT Token in Browser
1. Log in as admin
2. Open Browser DevTools (F12)
3. Go to "Application" → "Cookies"
4. Look for `next-auth.token` or similar JWT cookie
5. **Expected:** Encrypted session token present

#### Test 9.2: Direct Backend API Test (With Auth)
```bash
curl -H "x-user-email: admin@localhost" http://localhost:8000/admin/logs
```

**Expected Response:** JSON array of logs (or empty array)

#### Test 9.3: Backend Rejects Invalid Admin
```bash
curl -H "x-user-email: notadmin@example.com" http://localhost:8000/admin/logs
```

**Expected Response:**
```json
{"detail": "Admin access required."}
```

---

## Test Results Checklist

- [ ] Backend health check passes
- [ ] Admin endpoint rejects unauthenticated requests
- [ ] Frontend loads without errors
- [ ] Admin button visible in UI
- [ ] Admin login modal appears
- [ ] Wrong credentials rejected
- [ ] Correct credentials (admin/admin) accepted
- [ ] User profile shows "Admin" role
- [ ] Admin dashboard accessible when logged in
- [ ] Admin dashboard blocked when logged out
- [ ] Chat logs recorded in database
- [ ] Logs visible in admin dashboard
- [ ] Clear logs function works
- [ ] Sign out function works
- [ ] Session persists on page reload
- [ ] JWT cookie created on login

---

## Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| "Admin Access Required" on admin page | Not logged in or wrong role | Log in with `admin/admin` |
| Backend returns 403 | Email mismatch between frontend/backend | Check `ADMIN_EMAIL` in both `.env` files |
| Modal won't submit | JavaScript error | Check browser console (F12) |
| Database locked | Prisma/SQLite contention | Restart servers, delete `.db-journal` |
| CORS errors | Backend URL mismatch | Verify `NEXT_PUBLIC_API_BASE_URL` in frontend |
| "NEXTAUTH_SECRET" error | Missing env variable | Generate and add to `.env.local` |

---

## Performance Baseline

Expected response times:
- Admin login: < 500ms
- Load logs: < 1s (first time), < 200ms (cached)
- Clear logs: < 500ms
- Sign out: < 200ms

---

## Success Criteria

✅ **Full implementation is successful when:**

1. User can log in with `admin/admin` credentials
2. User sees "ADMIN" role displayed in profile
3. User can access `/admin` page and view logs
4. Each chat creates a log entry visible in admin panel
5. Admin can clear all logs
6. User can sign out
7. Backend validates admin requests using `x-user-email` header
8. Unauthenticated requests to admin endpoints return 403

---

## Next Steps

After successful testing:
1. ✅ Customize admin credentials (if needed)
2. ✅ Set up production environment variables
3. ✅ Deploy frontend and backend
4. ✅ Configure SSL/HTTPS
5. ✅ Set up monitoring and logging
