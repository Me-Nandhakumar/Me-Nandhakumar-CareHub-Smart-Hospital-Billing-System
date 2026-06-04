# 🏥 CareHub — Flask Web App

A complete hospital billing system converted from Python Tkinter to Flask web app.

## Features
- Admin login
- Patient registration with symptom-based medicine suggestions
- Automatic bill generation with print support
- GPay QR code generation
- Patient search
- Dashboard with stats

## Local Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up MySQL
# Create database: CREATE DATABASE hospital;
# Update DB_PASSWORD in app.py or use .env

# 3. Run
python app.py
# Visit http://localhost:5000
# Login: admin / 1234
```

## Deploy to Railway.app (FREE)

1. Push this folder to a new GitHub repo
2. Go to https://railway.app → New Project → Deploy from GitHub
3. Add a MySQL plugin: + New → Database → MySQL
4. Set these Environment Variables in Railway:
   - DB_HOST = (from MySQL plugin)
   - DB_PORT = (from MySQL plugin)
   - DB_USER = (from MySQL plugin)
   - DB_PASSWORD = (from MySQL plugin)
   - DB_NAME = railway
   - ADMIN_USER = admin
   - ADMIN_PASS = your_secure_password
5. Deploy → Railway gives you a public URL!

## Deploy to Render.com (FREE)

1. Push to GitHub
2. Go to https://render.com → New Web Service → Connect GitHub repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Add a free PostgreSQL or use PlanetScale for MySQL
6. Set environment variables same as above

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| DB_HOST | localhost | MySQL host |
| DB_PORT | 3306 | MySQL port |
| DB_USER | root | MySQL user |
| DB_PASSWORD | nandhu@1112 | MySQL password |
| DB_NAME | hospital | Database name |
| ADMIN_USER | admin | Login username |
| ADMIN_PASS | 1234 | Login password |
