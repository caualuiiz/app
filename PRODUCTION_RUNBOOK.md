# Production Runbook

## 1. Required external infrastructure

- MongoDB Atlas database and connection string.
- Render account with Blueprint access.
- OpenAI API key.
- Stripe account, webhook endpoint and recurring Prices for STARTER and PRO.
- Meta WhatsApp Cloud API app, phone number ID, access token, app secret and approved message templates.
- DNS access for the application domain and each customer custom domain.
- A transactional email provider and reset-email template for password recovery.

## 2. Render Blueprint

Apply `render.yaml` from `main`.

Services created:
- `saas-api`: FastAPI
- `saas-frontend`: React static site
- `saas-whatsapp-reminders`: 10-minute reminder cron

The frontend service uses `rootDir: frontend` and publishes `build`.

## 3. API environment variables

Required:
`MONGO_URL`, `DB_NAME`, `JWT_SECRET`, `FRONTEND_URL`, `PASSWORD_RESET_URL_BASE`, `OPENAI_API_KEY`, `FIELD_ENCRYPTION_KEY`.

Commercial:
`STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_STARTER`, `STRIPE_PRICE_PRO`.

WhatsApp:
`WHATSAPP_API_VERSION`, `WHATSAPP_VERIFY_TOKEN`, `WHATSAPP_APP_SECRET`,
`WHATSAPP_TEMPLATE_NEW_BOOKING`, `WHATSAPP_TEMPLATE_BOOKING_CONFIRMED`,
`WHATSAPP_TEMPLATE_BOOKING_REJECTED`, `WHATSAPP_TEMPLATE_LANGUAGE`.

Domain automation:
`RENDER_API_KEY`, `RENDER_FRONTEND_SERVICE_ID`.

Production sets `ENVIRONMENT=production`.

Password reset links must be delivered by the configured transactional email
provider. The API returns a reset token only outside production; it never
returns or logs the secret token in production.

## 4. Frontend environment

Set:
`REACT_APP_BACKEND_URL=https://<api-host>`

Optional:
`REACT_APP_APP_HOST=https://<frontend-host>`

## 5. First smoke test

1. Open the frontend and register an owner.
2. Complete onboarding and create the first company.
3. Configure services, professionals and availability.
4. Generate the landing preview, run critique, refine if necessary and publish.
5. Open `/<slug>` and `/<slug>/agendar`.
6. Create a PENDING booking.
7. Confirm/reject it from the authenticated agenda.
8. Verify WhatsApp notification delivery when configured.
9. Configure Stripe and verify checkout, webhook and plan limits.
10. Add a custom domain, publish the TXT record, verify and test landing + booking on the custom domain.

## 6. Production acceptance criteria

- CI green on `main`.
- API health returns HTTP 200 when MongoDB is available and HTTP 503 when it is not.
- No production wildcard CORS.
- Auth refresh sessions are persisted, rotated and revocable.
- Password reset tokens are stored only as hashes.
- Uploads use MongoDB GridFS; legacy files remain readable during migration.
- No real secrets are committed to Git.
- Public booking remains tenant-scoped by slug/domain.
- Backend installs use `backend/requirements.lock`; frontend installs use
  `frontend/package-lock.json` with `npm ci --legacy-peer-deps`.
