# Qing Phased Plan

Date: 2026-06-05
Current phase: Phase 3 preparation

## Current Decision

The project no longer follows a "short term only advances Phase 1" posture. The current operating state is:

- Phase 2 non-Reddit scope is ready for acceptance closure and is archived in `docs/reports/2026-06-05-phase2-acceptance.md`.
- Phase 3 preparation can start now.
- Reddit saved links are a separate external dependency waiting on Reddit review / approval.
- Reddit must not block TestFlight, deployment, production configuration, legal readiness, monitoring, invite, export, or performance work.

## Phase Status

| Phase | Status | Notes |
| --- | --- | --- |
| Phase 1 | Complete for current planning purposes | Earlier prototype and core flow foundation are no longer the active planning constraint. |
| Phase 2 | Non-Reddit scope accepted for closure | See the Phase 2 acceptance report for evidence and remaining production blockers. |
| Phase 2 Reddit saved links | Carryover / blocked external dependency | Wait for Reddit review before OAuth and saved links implementation. |
| Phase 3 | Active preparation | Use `docs/product/phase3-release-plan.md` as the execution and acceptance standard. |

## Near-Term Route

1. Archive Phase 2 non-Reddit acceptance.
2. Execute Phase 3 deployment, migration, secrets, monitoring, legal, invite, export, TestFlight, and performance preparation.
3. Keep Reddit saved links parked as carryover until external approval arrives.
4. After Reddit approval, open a small dedicated plan for OAuth and saved links, then merge the finished feature into the release track after staging acceptance.

## Phase 3 Preparation Plan

| Order | Work | Output | Gate |
| --- | --- | --- | --- |
| 1 | Deployment target selection | Staging/production topology and URLs | `/health` reachable in staging. |
| 2 | Database migration and backup | Migration/init runbook plus backup/restore runbook | Empty database can be initialized and smoke-tested. |
| 3 | Production secrets | Env var inventory and platform secret setup | No production secret or unsafe default is required from git. |
| 4 | Monitoring | Logs, health check, worker/provider failure visibility | Staging errors and health checks are queryable. |
| 5 | Legal readiness | Privacy, terms, AI disclaimer, deletion/export path | Public copy is ready for staging/TestFlight metadata. |
| 6 | Invite and beta operations | Invite/allowlist/support/feedback process | External testers can be onboarded and removed deliberately. |
| 7 | Data export/deletion | Manual or automated user data exit path | Export/deletion handling is approved before beta invite. |
| 8 | Stability and performance | Automated test run plus manual staging smoke | Critical flows work in staging. |
| 9 | TestFlight / overseas beta package | App metadata, screenshots, review notes, tester instructions | Beta submission package is ready. |

## Verification Baseline

Run before and after material Phase 3 changes:

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

Current observed baseline on 2026-06-05:

```text
Ran 105 tests in 9.859s
OK
```
