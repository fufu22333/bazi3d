# Legal Readiness Copy

Date: 2026-06-06
Audience: Overseas beta testers and TestFlight reviewers.

This document is product copy for staging placement. It is not legal advice; before a paid or public launch, have counsel review it.

## Privacy Policy

Bazi3D collects account information, profile inputs, generation task data, generated asset references, and basic technical logs needed to operate the beta.

Information we collect:

- Account details: email, username, password hash, and account creation time.
- Profile inputs: display name, gender, birth date/time if provided, birth location, style preferences, extra form payloads, and optional reference image URL.
- Generated content records: task status, provider name, generated model asset URLs, thumbnails, metadata, works, favorites, and evaluation logs.
- Technical logs: request id, endpoint, error state, provider failure context, and timing or status details needed for debugging.

How we use information:

- Create and authenticate beta accounts.
- Generate AI-assisted 3D character and guardian-spirit concepts.
- Display tasks, gallery items, works, profiles, and viewer pages.
- Diagnose provider, API, worker, and frontend failures.
- Respond to support, export, deletion, and abuse reports.

We do not sell beta tester personal information. We do not use beta data for third-party advertising.

Third-party services may process data needed for the product:

- AI text or model generation providers such as DeepSeek, Tencent Hunyuan 3D, or Meshy when enabled.
- Managed hosting, database, object storage, logging, and monitoring providers selected for staging or production.

Data retention:

- Active beta account data is kept while the account exists.
- Deleted account records are removed from the application database as implemented by `DELETE /api/auth/me`.
- Platform backups and provider logs may persist for a limited operational retention window controlled by the hosting/provider platform.

Export and deletion:

- Users can request or perform export through `GET /api/auth/export`.
- Users can delete their account through `DELETE /api/auth/me`.
- Manual requests can be sent to the beta support contact listed in `phase3-beta-operations.md`.

## Terms of Service

Bazi3D is a beta product. The service may change, fail, or become unavailable while the product is being tested.

Users agree to:

- Provide only information they are allowed to submit.
- Avoid illegal, harmful, hateful, sexual, or infringing content.
- Avoid trying to bypass access controls, abuse provider quotas, scrape private data, or disrupt the service.
- Use generated content responsibly and review it before publication.

Bazi3D may suspend or remove beta accounts that abuse the service, violate these terms, or create operational or legal risk.

Generated outputs are provided as-is. Because the system uses AI providers, outputs may be inaccurate, unexpected, incomplete, or visually flawed. Bazi3D does not guarantee that generated assets are unique, production-ready, or free from third-party rights concerns.

## AI-Generated Content Disclaimer

Bazi3D uses AI-assisted generation to turn structured profile inputs and style preferences into character concepts, prompts, and 3D model assets.

AI-generated results may contain mistakes, artifacts, biased associations, or content that does not match the user intent. Testers should review outputs before sharing or relying on them. The product is exploratory and does not provide professional, cultural, religious, legal, medical, or financial advice.

## Cookie and Tracking Note

The current web beta uses local browser storage for authentication state and basic app behavior. If analytics, cookies, or third-party tracking are added later, this note must be updated before external testers are invited.

## Provider Attribution and Third-Party Services

Bazi3D may call third-party AI and infrastructure providers to generate text, generate or host 3D assets, store data, and monitor service health. Provider availability, latency, quota, and content policies can affect the beta experience.

## TestFlight Review Notes

Reviewer account: create a dedicated staging reviewer account before submission.

Review flow:

1. Log in with the reviewer account.
2. Open create page and submit a simple profile.
3. Open task status page.
4. Open gallery, work detail, viewer, and profile pages.
5. If provider generation is disabled for review, use seeded demo assets and explain this in the review note.

Beta note:

Bazi3D is a web-first beta for AI-assisted 3D character concept generation. Some generation steps depend on external AI providers and may take longer than normal app interactions.
