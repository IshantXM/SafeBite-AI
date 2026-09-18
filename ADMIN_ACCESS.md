# SafetyBite-AI Admin Access

## Local URLs

- Web dashboard: http://localhost:5174/
- Core API health: http://localhost:8000/health
- API documentation: http://localhost:8000/docs

## Role Credentials

The local development API accepts these usernames. Passwords are accepted by the current development authentication endpoint and should be replaced with database-backed password hashes before production deployment.

| Role | Username | Password | API role |
|---|---|---|---|
| Admin | `doca_admin` | any non-empty password | `Admin` |
| Inspector | `inspector_sharma` | any non-empty password | `Inspector` |
| Consumer | `consumer_user` | any non-empty password | `Consumer` |

## Inspector Access Key

Use the mobile login screen's **Admin inspector access key** option:

`SB-INSPECTOR-2026`

This key returns an Inspector JWT through:

`POST /api/v1/auth/inspector-key`

For production, set `INSPECTOR_ACCESS_KEY` in the backend environment and never commit the production key.

## Email OTP

1. Select Admin, Inspector, or Consumer.
2. Enter an email address.
3. Tap **Email me a SafetyBite-AI OTP**.
4. Enter the six-digit code and tap **Verify and sign in**.

For real email delivery, set these backend variables in `.env`:

```env
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your-smtp-user
SMTP_PASSWORD=your-smtp-password
SMTP_FROM=SafetyBite-AI <no-reply@example.com>
AUTH_DEV_OTP_ENABLED=false
```

When SMTP is not configured for local development, the API returns a development OTP and the mobile app fills it automatically. Do not enable that behavior in production.

## Start Backend

```powershell
cd services/core-api
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

MinIO warnings are non-fatal for local login and OCR checks. Start Docker Compose when object storage and the full production stack are required:

```powershell
docker compose -f deploy/docker-compose.yml up --build
```

## Start Web Dashboard

```powershell
cd apps/web-dashboard
npm install
npm run dev -- --host 0.0.0.0
```

## USB Mobile App

The Android app uses USB port forwarding for the local API. Keep the device connected and run:

```powershell
adb reverse tcp:8000 tcp:8000
cd apps/mobile
flutter run -d 8c1e8ec8
```
