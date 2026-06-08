# Birthday Gift Model Refactor Plan

Date: 2026-06-08
Scope: Lightweight product and UX refactor for AI product manager positioning and a short AI coding contest demo.

## New Product Angle

Bazi3D should shift from a broad "AI x 3D character generation" demo to a more concrete consumer product:

**Generate a personalized 3D printable birthday gift model from birth information, style preferences, and optional reference imagery.**

The product story becomes easier to understand:

- User problem: people want gifts that feel personal, but custom 3D gifts are expensive, hard to design, and require design skills.
- Product promise: turn a recipient's birth time, place, relationship context, and aesthetic preferences into a symbolic 3D model that can be previewed, downloaded, and eventually printed.
- AI value: translate abstract personal signals into visual semantics, then into GLB-ready 3D assets.
- Business value: connect AI generation, model asset storage, preview, download, and future printing/order flows.

## Target User Experience

The first demo should feel like a gift customization flow, not a technical generator.

Primary user:

- A friend, partner, family member, or classmate preparing a birthday or graduation gift.
- They know the recipient's birthday and rough style taste.
- They want something with emotional meaning, not only a cute avatar.

Core journey:

1. Choose gift occasion: birthday first; graduation, anniversary, and friendship can be future presets.
2. Enter recipient information: nickname, birthday or birth datetime, city/place, relationship, optional gender presentation.
3. Select style direction: cute keepsake, elegant collectible, cyber fantasy, oriental symbol, minimal desk ornament.
4. Add gift intent: blessing, personality keywords, favorite color, optional reference image.
5. Generate visual concept: character or symbolic guardian model plus short gift meaning.
6. Preview 3D model: rotate, zoom, inspect silhouette, see print-readiness notes.
7. Download or save: GLB first; STL/OBJ and print order are future extensions.

## Lightweight Refactor Principles

- Keep the existing backend, model adapters, task system, and Three.js viewer.
- Rename and reframe surfaces before changing deep architecture.
- Preserve the current `character` and `guardian_spirit` schema for now, but explain them as "gift figure" and "symbolic companion".
- Add gift metadata through existing `extra_payload` before changing database tables.
- Make the demo credible for AI product manager evaluation: clear user problem, product loop, AI workflow, cloud asset logic, and measurable acceptance criteria.

## Planned Changes

### Phase 0: Documentation and Resume Narrative

Status: current document.

Deliverables:

- Reposition Bazi3D as an AI-personalized 3D gift product.
- Keep technical claims grounded in current code: DeepSeek prompt planning, Hunyuan3D/Meshy adapter scaffolding, GLB assets, task records, works, gallery, viewer, and tests.
- Use the phrase "3D printable birthday gift model" in product-facing material, but avoid claiming full print-order integration until implemented.

Acceptance:

- README and product docs can explain the new angle in one paragraph.
- Resume project bullet points can map directly to code evidence.

### Phase 1: Input Flow Copy and Metadata

Goal: make the create flow read like gift customization while reusing current input payload.

Suggested payload mapping:

| Gift field | Existing storage path | Notes |
| --- | --- | --- |
| Recipient nickname | `display_name` | Keep current field. |
| Birthday / birth datetime | `birth_datetime` | Use datetime when available; birthday-only can map to date with default time. |
| Birth place / city | `birth_location` | Keep current field. |
| Occasion | `extra_payload.occasion` | Default `birthday`. |
| Relationship | `extra_payload.relationship` | Example: friend, partner, family, classmate. |
| Gift message | `extra_payload.gift_message` | Short blessing or emotional intent. |
| Personality tags | `extra_payload.personality_tags` | Already supported by prompt builder. |
| Favorite color | `extra_payload.favorite_color` | New optional prompt signal. |
| Style preset | `style_profile.fashion_style` / `style_profile.spirit_style` | Rename in UI copy only at first. |
| Reference image | `reference_image_url` | Already supported. |

Frontend copy changes:

- `create.html`: change page framing from character generation to birthday gift customization.
- `frontend/js/create-page.js`: keep API contract stable; add optional `occasion`, `relationship`, `gift_message`, and `favorite_color` to `extra_payload`.
- `viewer.html` / `work.html`: present generated assets as gift model previews.

Acceptance:

- User can complete a birthday gift form without seeing engineering terms such as provider, schema, or adapter.
- Existing task creation endpoint continues to accept old payloads.
- Tests that validate create page shell and task payload remain passable with minimal updates.

### Phase 2: Prompt Reframe

Goal: make generated prompts optimize for a meaningful physical gift object.

Prompt direction:

- Treat the main asset as a "personalized 3D keepsake figure" instead of a generic character.
- Treat the companion asset as a "symbolic guardian ornament" that represents blessing, personality, or birth symbolism.
- Add print-aware constraints to the prompt language without claiming full manufacturability:
  - complete silhouette
  - stable standing pose
  - readable large forms
  - avoid ultra-thin floating details
  - clean GLB-ready geometry

Files likely affected:

- `backend/prompt/templates/prompt_template.txt`
- `backend/prompt/builder.py`
- `backend/services/generation_worker.py`
- `tests/test_prompt_builder.py`
- `tests/test_prompt_regression.py`
- `tests/test_generation_worker.py`

Acceptance:

- Prompt output still validates against `PromptOutput`.
- Generated asset prompt includes occasion, relationship, gift message, and physical keepsake constraints when supplied.
- Fallback behavior remains intact.

### Phase 3: Result and Gallery Reframe

Goal: make the result feel like a gift artifact, not a raw AI output.

Lightweight changes:

- Work title format: `{display_name} 的生日纪念模型` for birthday occasion.
- Work description: include a short generated or template-based gift meaning.
- Viewer labels: "礼物模型", "守护摆件", "预览", "下载 GLB".
- Gallery cards: show occasion and style preset when available.

Files likely affected:

- `backend/services/generation_worker.py`
- `backend/services/work_service.py`
- `frontend/js/viewer-page.js`
- `frontend/js/gallery.js`
- `frontend/js/work.js`
- related shell tests under `tests/`

Acceptance:

- Generated works are understandable as personalized gifts.
- Existing gallery and work-detail navigation remains unchanged.
- No new database migration is required for the first pass.

### Phase 4: Demo Packaging for AI Coding Contest

Goal: prepare a three-day demo story that is easy for recruiters and judges to evaluate.

Demo script:

1. "I want to make a birthday gift for a friend."
2. Fill in recipient, birthday, city, relationship, style, blessing.
3. Submit task.
4. Show AI semantic planning and generated 3D prompts.
5. Show GLB preview and saved work.
6. Explain cloud product extension: object storage, CDN delivery, model preview, media processing, and future print-order integration.

Demo metrics:

- Form completion time.
- Prompt JSON success rate.
- Task status transition correctness.
- GLB asset availability.
- Viewer render success.
- User-perceived match score for "personal meaning" and "gift suitability".

Acceptance:

- The demo can be explained in under 3 minutes.
- It connects product need, AI workflow, 3D asset handling, and cloud infrastructure.
- It does not overpromise a complete e-commerce or print fulfillment system.

## Non-Goals for This Lightweight Refactor

- No full e-commerce checkout.
- No production print vendor integration.
- No mandatory STL conversion in the first pass.
- No large database migration unless the gift fields become core analytics dimensions.
- No rewrite of the adapter architecture.
- No replacement of the current static frontend stack.

## Product Risks and Mitigations

| Risk | Mitigation |
| --- | --- |
| Birth information may feel too "fortune-telling" for some users. | Present it as symbolic personalization and aesthetic input, not deterministic fate analysis. |
| 3D generated models may not be truly printable. | Use "print-aware" and "GLB download" wording until STL validation or print vendor checks exist. |
| Gift story may sound gimmicky. | Emphasize recipient emotion, occasion, and keepsake value over metaphysical claims. |
| Prompt quality may vary. | Keep fallback schema, debug artifacts, and regression tests. |
| Scope may grow into marketplace/e-commerce. | Keep first version focused on preview, save, download, and product narrative. |

## Recommended Next Implementation Order

1. Update README and frontend visible copy to the gift customization angle.
2. Add gift fields to the create payload through `extra_payload`.
3. Update prompt template and asset prompt builder with gift intent and print-aware constraints.
4. Update generated work title/description.
5. Update tests for prompt builder, task payload, frontend shell text, and generation worker.
6. Run the full test suite.
7. Capture screenshots for resume, submission, and demo explanation.

## Resume-Ready Summary

Bazi3D is being repositioned as an AI-personalized 3D gift customization product: users enter birthday/birth context, relationship, style preferences, and blessing intent; the system uses LLM semantic planning and 3D generation adapters to produce GLB-previewable keepsake models and symbolic companion ornaments, with future expansion into object storage, CDN delivery, media processing, and print-order workflows.
