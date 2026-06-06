# Phase 3 Beta Operations

Date: 2026-06-06

## Invite Model

Phase 3 uses manual approval for the first overseas beta.

Reason:

- The current app already supports account registration and login.
- Manual approval is enough for the first small tester group.
- Invite-code enforcement can be added later without blocking staging readiness.

Operating rule:

- Keep the public staging URL private.
- Add testers in small batches.
- Record tester email, invite date, support channel, and offboarding status in an external beta tracker.
- Remove abusive or inactive testers through account deletion or database admin action if self-serve deletion is unavailable to the operator.

Future automation task:

- Add invite codes or an allowlist gate to `/api/auth/register`.
- Add tests for valid code, invalid code, reused code, and allowlisted email.

## Tester Onboarding

Tester instructions:

1. Open the staging app URL.
2. Register with the invited email.
3. Create one simple profile and one style-focused profile.
4. Review task status, gallery, work detail, viewer, and profile pages.
5. Report any blank page, failed provider state, confusing output, or broken navigation.

Support channel:

- Primary: project owner email or private Discord/Slack channel selected before invite.
- Emergency: pause new invites and disable provider keys if abuse or unexpected cost appears.

## Feedback Intake

Feedback template:

- Tester email.
- Browser and device.
- Page or flow.
- What happened.
- What was expected.
- Screenshot or request id if available.

Tags:

- `auth`
- `create`
- `task-polling`
- `provider`
- `gallery`
- `work-detail`
- `viewer`
- `profile`
- `legal`
- `performance`

## Abuse and Account Removal

Remove or suspend a tester when:

- They submit illegal, harmful, hateful, sexual, infringing, or abusive content.
- They try to bypass access control.
- They create excessive provider cost.
- They scrape private data or attack the service.

Removal process:

1. Export the account record if needed for audit.
2. Delete the account through `DELETE /api/auth/me` when user-confirmed or through an admin database operation when operator-initiated.
3. Revoke shared staging credentials or rotate provider keys if exposed.
4. Mark the tester as removed in the beta tracker.

## Data Export, Deletion, and Retention

Self-serve data exit endpoints:

- `GET /api/auth/export` returns user profile, tasks, works, and generated asset references.
- `DELETE /api/auth/me` deletes the authenticated user and owned application records.

Manual request path:

- If a tester cannot access their account, verify the request through the invited email and run an operator-assisted export or deletion.

Retention:

- Application records are removed when account deletion is performed.
- Platform backups, provider logs, and object storage lifecycle rules must be checked before external beta launch.

## Staging Smoke Record

Before each tester batch, record:

- Date and commit.
- Staging URL.
- Test account.
- `/health` result.
- Full automated test result.
- Manual smoke result for auth, create task, polling, gallery, work detail, viewer, failed provider state.
