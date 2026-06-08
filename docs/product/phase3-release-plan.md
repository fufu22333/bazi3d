# Phase 3 Release Plan and Acceptance Standard

Date: 2026-06-05
Phase: Overseas release / TestFlight / production readiness
Startup gate: Phase 2 non-Reddit acceptance report is archived. Reddit saved links remain a blocked external dependency and do not block Phase 3 startup.

## Goal

Prepare Bazi3D for an overseas beta release path with a reproducible staging environment, production-grade configuration, TestFlight readiness, legal / policy coverage, controlled invites, exportability, monitoring, and stable performance.

## Release Tracks

| Track | Outcome | Acceptance Standard |
| --- | --- | --- |
| Deployment platform | Backend, frontend, database, and storage have selected staging and production targets | A documented deploy path can create a fresh staging environment from the repo and environment variables. |
| Database migrations | Schema changes are versioned and repeatable | A migration command can upgrade an empty staging database and a backup/restore drill is documented. |
| Production secrets | Secrets are removed from defaults and managed by platform secret storage | No production secret is stored in git; required env vars are documented in `.env.example` or release docs. |
| Monitoring | API, worker, provider, and frontend failures are observable | Staging emits health, error, latency, and worker status signals to the selected monitor/log sink. |
| Legal and policy | Public legal pages exist for overseas beta | Privacy policy, terms, AI content disclaimer, cookie/tracking note, and deletion/export contact path are available. |
| TestFlight / beta packaging | iOS beta path is defined even if current app remains web-first | TestFlight wrapper or web beta alternative is chosen, with account, bundle/app metadata, screenshots, and review notes listed. |
| Invite system | Beta access is controlled | Invite code, allowlist, or manual account approval flow is selected and tested. |
| Data export/deletion | Users have a basic data exit path | Export and deletion request process is documented; implementation task is created if not automated. |
| Performance and stability | Critical flows are usable under expected beta load | Health, auth, create task, task polling, gallery, work detail, and viewer pages pass smoke checks in staging. |
| Reddit saved links | External dependency | Kept as carryover until Reddit review approves OAuth / saved links scope. |

## Workstream 1: Deployment Platform

Deliverables:

- Choose backend hosting target.
- Choose frontend hosting target if decoupled from Flask static serving.
- Choose MySQL hosting target.
- Choose object/model asset storage target.
- Document staging and production URLs.

Acceptance:

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

```powershell
Invoke-WebRequest -Uri "<staging-backend-url>/health" -UseBasicParsing
```

Pass criteria:

- Test suite passes locally before deploy.
- Staging `/health` returns a successful response.
- Static entry point is reachable at the chosen staging app URL.

## Workstream 2: Migration and Data Safety

Deliverables:

- Select migration tooling or document the current schema initialization path.
- Add a staging migration runbook.
- Add backup and restore runbook for production database.
- Define rollback policy for failed migrations.

Acceptance:

```powershell
.venv\Scripts\python.exe init_db.py
.venv\Scripts\python.exe -m unittest tests.test_models_smoke -v
```

Pass criteria:

- Empty local/staging database can be initialized.
- Model smoke tests pass after initialization.
- Backup and restore commands are documented before production launch.

## Workstream 3: Secrets and Runtime Configuration

Deliverables:

- Audit required env vars: database URI, JWT secret, provider API keys, CORS origin, logging level, asset storage credentials.
- Remove or quarantine production-unsafe defaults from deployment configuration.
- Update `.env.example` with all required non-secret names.
- Document secret rotation steps.

Acceptance:

```powershell
rg -n "dev-secret-key|MYSQL_PASSWORD.*123456|CORS.*\*" backend README.md .env.example
```

Pass criteria:

- Production deployment does not rely on development fallback values.
- Any remaining development defaults are clearly marked local-only.
- Platform secret store contains required staging/production values.

## Workstream 4: Monitoring and Incident Signals

Deliverables:

- Request ID logging policy.
- API error logging sink.
- Worker job status metrics.
- Provider failure and latency logging.
- Basic uptime check for `/health`.

Acceptance:

```powershell
.venv\Scripts\python.exe -m unittest tests.test_guardrails tests.test_generation_worker -v
```

Pass criteria:

- Guardrail/API error paths remain covered.
- Worker failure transitions remain covered.
- Staging dashboard or log query can show recent health checks and errors.

## Workstream 5: Legal, Policy, and Store Review

Deliverables:

- Privacy policy.
- Terms of service.
- AI-generated content disclaimer.
- Data deletion/export contact path.
- Provider attribution / third-party service note.
- TestFlight review notes and beta tester instructions.

Acceptance:

```powershell
Test-Path docs\product\legal-readiness.md
rg -n "Privacy|Terms|AI-generated|deletion|export|third-party|TestFlight" docs\product
```

Pass criteria:

- Legal readiness document exists.
- Public-facing legal copy is ready for staging placement.
- TestFlight review metadata has no placeholder copy.

## Workstream 6: Invite and Beta Operations

Deliverables:

- Decide invite mechanism: invite code, allowlist, or manual approval.
- Define tester onboarding and support channel.
- Define beta feedback intake.
- Define abuse and account removal process.

Acceptance:

```powershell
rg -n "invite|allowlist|beta|feedback|support|delete account|deletion" docs backend frontend tests
```

Pass criteria:

- Beta access model is documented.
- Account removal / tester offboarding path is documented.
- Feedback intake is linked from tester instructions.

## Workstream 7: Data Export and Deletion

Deliverables:

- Define export format for user profile, tasks, works, and generated asset references.
- Define deletion scope and retention policy.
- Decide whether Phase 3 beta uses manual operations or self-serve endpoints.

Acceptance:

```powershell
rg -n "export|delete|deletion|retention|profile|works|tasks" docs backend tests
```

Pass criteria:

- Export/deletion scope is documented.
- Manual or automated process is approved before inviting external testers.
- Future automation tasks are tracked if not implemented for first beta.

## Workstream 8: Performance and Stability

Deliverables:

- Define smoke-flow checklist for auth, create task, polling, gallery, work detail, viewer.
- Define provider timeout and retry posture.
- Define staging beta load expectation.
- Capture known slow or brittle paths.

Acceptance:

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

Manual staging smoke:

```text
1. Open staging app.
2. Register or log in as beta tester.
3. Create a task.
4. Confirm task status page renders and polling behaves.
5. Open gallery.
6. Open work detail.
7. Open viewer.
8. Confirm failed provider states are understandable.
```

Pass criteria:

- Automated suite passes.
- Manual staging smoke completes without broken navigation or blank critical pages.
- Known provider failures show recoverable status, not silent failure.

## Blocked External Dependency: Reddit Saved Links

Reddit remains outside the Phase 3 startup gate.

Resume this work only after Reddit app / OAuth review is approved:

- Create Reddit OAuth integration plan.
- Implement OAuth callback and token storage.
- Implement saved links import.
- Add tests for revoked token, rate limit, empty saved list, and import deduplication.
- Add user-facing settings and disconnect flow.

## Phase 3 Exit Criteria

Phase 3 can be considered ready for overseas beta / TestFlight only when:

- Phase 2 acceptance report is archived.
- Staging deploy is reproducible.
- Production secrets are managed outside git.
- Database migration and backup/restore runbooks exist.
- Monitoring/logging is active in staging.
- Legal readiness copy exists and is linked from staging or release notes.
- Invite/beta operation model is documented and tested.
- Data export/deletion path is documented or implemented.
- Full local automated test suite passes.
- Staging smoke checklist passes.

Reddit saved links are merged later as a separate approved feature and are not required for Phase 3 exit unless the release scope is explicitly changed.
