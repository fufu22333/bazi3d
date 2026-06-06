# Phase 3 Release Readiness Runbook

Date: 2026-06-06
Scope: Overseas beta / TestFlight preparation for the current web-first Bazi3D app.

## Deployment Topology

Recommended staging stack:

- Backend: Render Web Service or Railway service running `python backend/app.py`.
- Frontend: Flask static serving from the same backend for first beta. Decouple later only if CDN caching or separate deploy cadence becomes necessary.
- Database: Managed MySQL 8 on PlanetScale, Railway MySQL, or Aiven MySQL.
- Asset storage: Tencent COS for Hunyuan outputs, with public CDN or signed URL refresh policy.
- Monitoring: Platform logs plus uptime check against `/health`. Optional Sentry via `SENTRY_DSN`.

Initial URLs:

- Staging backend: `TBD_AFTER_PLATFORM_SELECTION`
- Staging app: `TBD_AFTER_PLATFORM_SELECTION/app`
- Production backend: `TBD_AFTER_STAGING_ACCEPTANCE`
- Production app: `TBD_AFTER_STAGING_ACCEPTANCE/app`

The URLs are intentionally not hardcoded in code. They must be supplied by the selected host and recorded here before external testers are invited.

## Environment Variables

Required for staging and production:

- `APP_ENV`
- `SQLALCHEMY_DATABASE_URI` or `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`
- `JWT_SECRET_KEY`
- `CORS_ALLOWED_ORIGINS`
- `LOG_LEVEL`
- `DEEPSEEK_API_KEY`
- `TENCENTCLOUD_SECRET_ID`
- `TENCENTCLOUD_SECRET_KEY`
- `TENCENTCLOUD_REGION`
- `HUNYUAN_ENDPOINT`
- `ASSET_STORAGE_BUCKET`
- `ASSET_STORAGE_REGION`
- `ASSET_STORAGE_PUBLIC_BASE_URL`
- `SENTRY_DSN` if Sentry is enabled

Production guardrails now require an explicit `JWT_SECRET_KEY` and explicit `CORS_ALLOWED_ORIGINS` when `APP_ENV=production`.

## Migration and Database Safety

Current schema path uses SQLAlchemy metadata through `init_db.py`.

Staging initialization:

```powershell
.venv\Scripts\python.exe init_db.py
.venv\Scripts\python.exe -m unittest tests.test_models_smoke -v
```

Before production, choose one migration path:

- Short beta path: keep `init_db.py` for empty staging only; do not run destructive schema changes against production.
- Production path: introduce Alembic, generate an initial migration from current models, and require reviewed migration files for every schema change.

Backup drill for managed MySQL:

```powershell
mysqldump --single-transaction --routines --triggers --set-gtid-purged=OFF -h <host> -P <port> -u <user> -p <database> > backup.sql
mysql -h <restore-host> -P <port> -u <user> -p <restore-database> < backup.sql
```

Rollback policy:

- Failed empty-staging migration: drop and recreate staging database, then rerun `init_db.py`.
- Failed production migration: stop deploy, restore from latest backup into a new database, repoint `SQLALCHEMY_DATABASE_URI`, and preserve failed database for investigation.
- Data-changing migrations require a backup and manual rollback notes before execution.

## Secrets and Rotation

Secrets must live in the platform secret store, not git.

Rotation steps:

1. Add the new secret value to staging.
2. Restart staging and run the smoke suite.
3. Add the new value to production during a quiet window.
4. Restart production workers/web process.
5. Revoke the old provider key or JWT secret after active sessions are considered expired.

For `JWT_SECRET_KEY`, rotation invalidates existing tokens. Announce beta re-login before rotation.

## Monitoring and Incident Signals

Minimum staging signals:

- `/health` returns 200 and includes `X-Request-Id`.
- API errors include a request id in guarded routes.
- Worker failures transition generation tasks to `failed`.
- Provider normalization failures are logged with request/task context.
- Platform log query can filter by request id, `task_id`, and error level.

Suggested uptime check:

```powershell
Invoke-WebRequest -Uri "<staging-backend-url>/health" -UseBasicParsing
```

Suggested local verification:

```powershell
.venv\Scripts\python.exe -m unittest tests.test_guardrails tests.test_generation_worker -v
```

## Performance and Stability

Expected beta load:

- 20 to 50 invited testers.
- Low concurrent task creation, with provider latency treated as the dominant bottleneck.
- Model generation failures must surface as understandable `failed` states.

Smoke checklist:

1. Open staging app.
2. Register or log in as beta tester.
3. Create a task.
4. Confirm task status page renders and polling behaves.
5. Open gallery.
6. Open work detail.
7. Open viewer.
8. Confirm failed provider states are understandable.

Known brittle paths:

- External provider latency and quota.
- Signed asset URL expiry.
- LocalStorage auth token persistence on shared devices.
- Static frontend remains web-first; native TestFlight packaging is a wrapper decision.

## TestFlight / Overseas Beta Package

Current decision: web-first beta first, TestFlight wrapper second.

If TestFlight is required, use a minimal iOS WebView wrapper that opens the staging or production app URL.

Required metadata:

- Bundle id: `com.bazi3d.beta` or final registered equivalent.
- App name: `Bazi3D`.
- Beta description: AI-assisted 3D character concept generation from structured profile input.
- Review notes: Web account login is required; generated 3D assets may take time because external AI providers are used.
- Screenshots: create page, task status, gallery, work detail, viewer, profile.
- Support URL: beta support channel from `phase3-beta-operations.md`.
- Privacy URL: staged privacy policy from `legal-readiness.md`.

## Exit Gate

Phase 3 local readiness is satisfied only after:

- Full local automated suite passes.
- Release docs in `docs/product` have no placeholder legal copy.
- Staging URLs replace the deployment placeholders above.
- Staging smoke checklist is completed and dated.
