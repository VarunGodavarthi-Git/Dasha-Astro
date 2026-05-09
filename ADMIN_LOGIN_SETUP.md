# Local Admin Login Setup Guide

## Overview
The project has been updated to support **local username/password authentication** for the admin user, in addition to Google and Facebook OAuth providers. This allows you to log in as an admin using:
- **Username:** `admin`
- **Password:** `admin`

## Changes Made

### 1. Frontend Authentication ([NextAuth Configuration](frontend/pages/api/auth/[...nextauth].ts))
- Added `CredentialsProvider` to support local username/password authentication
- Configured JWT-based session strategy to support both OAuth and credentials providers
- Added admin role assignment for local credentials-based login

### 2. UI Components ([Auth Buttons](frontend/components/auth-buttons.tsx))
- Added "Admin" login button to the authentication UI
- Implemented a modal login form with username/password inputs
- The form uses the NextAuth credentials provider for authentication

## Setup Instructions

### Frontend Setup

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Environment Configuration**
   Create a `.env.local` file in the `frontend` directory:
   ```env
   NEXTAUTH_URL=http://localhost:3000
   NEXTAUTH_SECRET=your-secret-key-here
   DATABASE_URL=file:../../data/vedic_astrology.db
   
   # OAuth Providers (optional)
   GOOGLE_CLIENT_ID=
   GOOGLE_CLIENT_SECRET=
   FACEBOOK_CLIENT_ID=
   FACEBOOK_CLIENT_SECRET=
   
   ADMIN_EMAIL=admin@localhost
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   ```

   **Important:** Generate a secure `NEXTAUTH_SECRET`:
   ```bash
   openssl rand -base64 32
   ```

3. **Database Setup**
   ```bash
   # Generate Prisma client
   npm run prisma:generate
   
   # Push schema to database
   npm run prisma:push
   ```

4. **Start Frontend Development Server**
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:3000`

### Backend Setup

1. **Install Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   Create a `.env` file in the `backend` directory:
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

3. **Start Backend Server**
   ```bash
   cd backend
   python -m app.main
   ```
   The API will be available at `http://localhost:8000`

## How to Use

### Logging In

1. Navigate to `http://localhost:3000` in your browser
2. Click the **"Admin"** button in the top-right corner
3. A login modal will appear
4. Enter the credentials:
   - **Username:** `admin`
   - **Password:** `admin`
5. Click **"Sign In"**

### After Login

- You'll be redirected to the main console
- Your user profile will show "Admin" as your role
- You'll have access to the **Admin** panel at the top right
- Click on the **Admin** link to access the **Interaction Logs** page where you can:
  - View all chat interactions with timestamps
  - See user queries and AI responses
  - Clear logs if needed

### Logging Out

- Click the **"Sign out"** button in the top-right corner

## Features

### Local Authentication
- ✅ Simple username/password login (admin/admin)
- ✅ No external OAuth provider required
- ✅ Perfect for local/development setup
- ✅ Admin role automatically assigned

### Admin Dashboard
- ✅ View all chat interactions
- ✅ See who chatted with the system and when
- ✅ View the exact prompts and responses
- ✅ Search and filter logs (expandable feature)
- ✅ Clear all logs

### OAuth Integration (Still Available)
- ✅ Google OAuth login (requires credentials setup)
- ✅ Facebook OAuth login (requires credentials setup)

## Security Notes

⚠️ **Important Security Considerations:**

1. **Development Use Only**: The hardcoded admin credentials (`admin/admin`) are suitable for local development only
2. **NEXTAUTH_SECRET**: Always set a strong `NEXTAUTH_SECRET` in production
3. **HTTPS**: Use HTTPS in production
4. **Environment Variables**: Never commit `.env` files or secrets to version control
5. **ADMIN_EMAIL**: The backend uses `ADMIN_EMAIL` environment variable to validate admin access. Ensure both frontend and backend have the same `ADMIN_EMAIL`

## Customizing Credentials

To change the admin username and password:

Edit [frontend/pages/api/auth/[...nextauth].ts](frontend/pages/api/auth/[...nextauth].ts):

```typescript
const ADMIN_USERNAME = "admin";      // Change username here
const ADMIN_PASSWORD = "admin";      // Change password here
```

Then restart the frontend development server.

## Troubleshooting

### Login Modal Doesn't Appear
- Check browser console for errors
- Ensure NextAuth is properly initialized

### Getting "Unauthorized" on Admin Page
- Verify you're logged in as admin user
- Check that your role shows "ADMIN" in the user profile
- Ensure `ADMIN_EMAIL` matches in both frontend and backend `.env` files

### Database Connection Issues
- Check that the data directory exists: `data/vedic_astrology.db`
- Ensure file permissions are correct
- Verify `DATABASE_URL` in `.env.local`

### Backend Admin Endpoint Returns 403
- The backend validates admin access using the `x-user-email` header
- Ensure the email from your login matches the `ADMIN_EMAIL` in the backend `.env`

## Architecture

```
Frontend (Next.js + NextAuth)
    ↓
    ├─ Local Admin Login (Credentials Provider)
    ├─ Google OAuth
    └─ Facebook OAuth
    ↓
Backend (FastAPI + SQLAlchemy)
    ↓
    ├─ Chart Calculation Engine
    ├─ Ollama AI Integration
    └─ Admin Logs Database
```

## Files Modified

- [frontend/pages/api/auth/[...nextauth].ts](frontend/pages/api/auth/[...nextauth].ts) - Added CredentialsProvider and JWT strategy
- [frontend/components/auth-buttons.tsx](frontend/components/auth-buttons.tsx) - Added admin login modal

## Next Steps

1. Complete the setup following the instructions above
2. Test the admin login with credentials `admin/admin`
3. Access the admin dashboard to view interaction logs
4. Customize credentials as needed for your deployment
