# CostLens Windows Setup Guide

## Step 1: Install Microsoft Visual C++ Build Tools (Required)

Download and install from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

**Installation steps:**
1. Run the installer
2. Select "Desktop development with C++"
3. Click Install
4. Wait for completion (5-15 minutes)
5. **Restart your machine after installation**

## Step 2: Install Python Dependencies

After restarting, open PowerShell in the CostLens directory and run:

```powershell
cd c:\Users\P3INW57\Desktop\CostLens
.\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

This will take several minutes due to compilation of native modules.

## Step 3: Install PostgreSQL

Download from: https://www.postgresql.org/download/windows/

**Setup:**
1. Run installer, use default settings
2. Set password for postgres user: `costlens` (or note it down)
3. Port: 5432 (default)
4. Complete installation

**Create database:**

Open PowerShell and connect to PostgreSQL:
```powershell
psql -U postgres
```

Then in psql:
```sql
CREATE USER costlens WITH PASSWORD 'costlens';
CREATE DATABASE costlens OWNER costlens;
GRANT ALL PRIVILEGES ON DATABASE costlens TO costlens;
\q
```

## Step 4: Install Redis

Download from: https://github.com/microsoftarchive/redis/releases

Or use WSL2 + Docker (easier):
- Install Docker Desktop for Windows
- Run: `docker run -d -p 6379:6379 redis:latest`

## Step 5: Configure Environment

The `.env` file is already created from `.env.example`. Verify it has:

```env
DATABASE_URL=postgresql+asyncpg://costlens:costlens@localhost:5432/costlens
DATABASE_URL_SYNC=postgresql://costlens:costlens@localhost:5432/costlens
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-super-secret-key-change-in-production
ENVIRONMENT=development
LOG_LEVEL=INFO
```

## Step 6: Initialize Database

```powershell
.\.venv\Scripts\python.exe -m app.seed
```

This creates tables and seeds demo data.

## Step 7: Run the Application

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

You should see:
```
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete [took X.XXXs]
INFO:     Uvicorn running on http://127.0.0.1:8000
```

## Access the Application

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: localhost:5432 (psql)
- **Redis**: localhost:6379

## Troubleshooting

### "No module named uvicorn"
→ Rerun pip install: `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`

### "connection refused" on database
→ Make sure PostgreSQL is running (check Services)

### "connection refused" on Redis
→ Start Redis: `redis-server.exe` (if installed locally) or Docker

### Build tool errors
→ Restart Windows after installing Visual C++ Build Tools

## Optional: Using Docker for Databases

If you have Docker Desktop installed, create a `docker-compose.yml`:

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: costlens
      POSTGRES_PASSWORD: costlens
      POSTGRES_DB: costlens
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:latest
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

Then: `docker-compose up -d`
