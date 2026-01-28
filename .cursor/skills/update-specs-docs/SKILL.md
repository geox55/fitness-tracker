---
name: update-specs-docs
description: Keeps the master spec, quick reference / implementation summary, and feature changelog in sync with code changes by analyzing git diffs or lists of changed files and generating patch-ready markdown updates. Use after making code changes to propagate them into fitness_tracker_spec.md (or spec docs), QUICK_REFERENCE / IMPLEMENTATION_SUMMARY sections, and per-feature changelog entries.
---

# Update Specs & Docs

## Purpose

This skill keeps **architecture & product docs** in sync with **actual code changes** in the Fitness Tracker project.

Use it whenever:
- You have **changed code** (backend, frontend, shared, infra) and
- Need to **synchronize documentation**:
  - **Master spec**: `fitness_tracker_spec.md` (if present) or the spec files under `docs/spec/`.
  - **QUICK_REFERENCE / IMPLEMENTATION_SUMMARY**: short developer-facing reference and implementation notes (e.g. in `docs/quick-start-dev.md`, `docs/design-reference.md`, or dedicated sections).
  - **Feature changelog**: per-feature or general changelog for user-visible or API-visible changes.

The skill’s job is to:
1. **Read git diff / changed files**.
2. **Infer which features and APIs are affected**.
3. **Generate markdown patches** for the relevant docs, ready to apply via patch tools.

## Inputs

The skill expects:
- A **git diff** or equivalent:
  - Example: `git diff main...HEAD` or `git diff --cached`.
  - Or a **list of changed files** grouped by area (`packages/backend/...`, `packages/frontend/...`, `packages/shared/...`).
- Knowledge of **where docs live**:
  - Master spec:
    - Prefer a single `fitness_tracker_spec.md` if it exists.
    - Otherwise, use the existing structured spec files: `docs/spec/01-overview.md`, `02-architecture.md`, `03-api-specification.md`, `04-testing-strategy.md`, `05-ui-ux-guidelines.md`, `06-best-practices.md`, etc.
  - QUICK_REFERENCE / IMPLEMENTATION_SUMMARY:
    - Typically lives in `docs/quick-start-dev.md`, `docs/design-reference.md`, or similarly named “quick reference” / “implementation summary” sections.
  - Feature changelog:
    - A central `docs/changelog.md` or per-feature changelog section; if missing, the skill may propose creating/expanding one.

If some files do not exist yet:
- **Assume** they can be created in the most natural location (e.g. `docs/changelog.md` for aggregated changelog, `docs/fitness_tracker_spec.md` as a unified spec) and note this in the suggested patch.

## High-Level Workflow

When using this skill, follow this process:

1. **Collect code change context**
   - Run git commands (or receive their output) to gather:
     - Which files changed.
     - For each file: what was added/removed (at least at a high-level).
   - Group changes by **domain/feature**, using:
     - Folders (e.g. `packages/frontend/src/features/workouts`, `packages/backend/src/api/workouts`).
     - API paths in the code (e.g. `/api/workouts`, `/api/auth`).
     - Entities/tables in SQL/DB code.

2. **Identify documentation impact**
   - For each affected feature/domain, determine:
     - Does the **user-facing behavior** change? → Update **master spec** + **changelog**.
     - Does the **public API contract** change? (endpoint, payload, error codes) → Update **API spec** (e.g. `docs/spec/03-api-specification.md`) + **QUICK_REFERENCE**.
     - Does the **architecture / internal design** change? → Update **IMPLEMENTATION_SUMMARY** (e.g. in `docs/design-reference.md`).

3. **Plan doc updates per artifact**
   - **Master spec**:
     - Align high-level behavior and API surface.
     - Ensure user stories and acceptance criteria reflect the new behavior.
   - **QUICK_REFERENCE**:
     - Provide short, copy-paste-friendly examples for typical flows and important edge-cases.
   - **IMPLEMENTATION_SUMMARY**:
     - Document key internal decisions: modules touched, patterns used, non-obvious constraints, and testing strategy.
   - **Changelog**:
     - Record user-visible, API-visible, and breaking changes with dates and concise descriptions.

4. **Generate patch-ready markdown**
   - Read the current markdown file(s).
   - Locate the correct section (by heading / feature name); if not found, **add a new section** in a reasonable place.
   - Propose **minimal edits**:
     - Prefer updating existing bullets/sections over rewriting entire documents.
     - Maintain existing style, headings, and language (EN/RU mix) where possible.

5. **Output as a patch**
   - For each updated markdown file, propose:
     - The relevant **before/after** snippets, or
     - A patch that can be applied with a patch tool (one file at a time), with clear context.

## Master Spec Update Templates

Use these templates when modifying the master spec (`fitness_tracker_spec.md` or files under `docs/spec/`).

### Feature Section Template

For each affected feature, use or create a section like:

```markdown
### [Feature Name]

- Status: implemented | in-progress | deprecated
- User story: As a [user type], I want [goal], so that [value].
- Summary:
  - High-level behavior in 2–4 bullets.
- API overview:
  - `METHOD /api/...` — краткое назначение.
- Data model:
  - Main entities and key fields (high-level, not every column).
- Constraints:
  - Important validation / domain rules (ranges, invariants, dependencies).
```

Where to place:
- If there’s already a section for this feature, **update** it (status, summary, API, constraints).
- If not, add the section under the most relevant chapter (e.g. Workouts, Auth, Analytics).

### API Spec Template

When API endpoints change, add/update entries in the API spec file (e.g. `docs/spec/03-api-specification.md`):

```markdown
#### [METHOD] /api/... — [Short name]

- Purpose: кратко, что делает эндпоинт.
- Auth: required | optional | none.
- Request:
  - Query params:
    - `param`: type — meaning, validation.
  - Body:
    - `field`: type — meaning, validation.
- Response:
  - Success:
    - Shape: `{ data: ..., total?: number, hasMore?: boolean }`
  - Errors:
    - `{ error: string, code?: string, details?: object }`
    - Main codes: `validation_error`, `not_found`, `unauthorized`, domain-specific codes.
```

Ensure:
- New/changed endpoints in code have corresponding **up-to-date spec entries**.
- Removed endpoints are marked as **deprecated** or removed, with a note in the changelog if user-visible.

## QUICK_REFERENCE / IMPLEMENTATION_SUMMARY Templates

Depending on how the project is structured, QUICK_REFERENCE and IMPLEMENTATION_SUMMARY can be:
- Separate headings in the same document, or
- Different documents.

### QUICK_REFERENCE Block

Use this to provide a concise, practical reference for developers:

```markdown
## [Feature Name] — QUICK_REFERENCE

- Typical flow:
  1. Step 1...
  2. Step 2...
- Key endpoints:
  - `METHOD /api/...` — one-line description.
  - `METHOD /api/...` — one-line description.
- Key constraints:
  - Ranges, invariants, permissions that are easy to forget.
- Examples:
  - Request:
    ```http
    POST /api/...
    Content-Type: application/json

    { ... }
    ```
  - Response:
    ```json
    {
      "data": { ... }
    }
    ```
```

### IMPLEMENTATION_SUMMARY Block

Use this to document internal design decisions:

```markdown
## [Feature Name] — IMPLEMENTATION_SUMMARY

- Modules:
  - Backend: `packages/backend/src/api/...`, `services/...`, `repositories/...`
  - Frontend: `packages/frontend/src/features/...`
  - Shared: `packages/shared/...` (schemas, types, constants)
- Important decisions:
  - Key architectural choices, patterns, and trade-offs.
- Data model:
  - Which tables/entities are involved and how they relate.
- Error handling:
  - Main error codes and how they surface to the client.
- Testing:
  - Unit: main service/repository tests.
  - Integration: API tests or E2E flows relevant to this feature.
```

If an IMPLEMENTATION_SUMMARY block for the feature doesn’t exist yet:
- Create it in an appropriate place (e.g. near related features in `docs/design-reference.md`).

## Feature Changelog Template

All user-visible / API-visible changes should be reflected in a **changelog**.

If `docs/changelog.md` (or equivalent) exists, use it; otherwise, propose creating it with entries like:

```markdown
## [YYYY-MM-DD] [Feature Name]

- Type: feature | fix | refactor | breaking
- Scope: backend | frontend | shared | infra
- Summary:
  - One-line description of the change.
- Details:
  - Bullet list of important behavior changes, new endpoints, or key refactors.
- Migration:
  - Notes on data migration, backwards compatibility, or required client changes.
```

Guidelines:
- **Group** related changes under the same date and feature when possible.
- For **breaking changes**, clearly mark them (`Type: breaking`) and describe:
  - What breaks.
  - How to migrate or adapt.

## Mapping Git Changes to Docs

When analyzing a git diff:

- **Backend changes (`packages/backend/...`)**:
  - Look for:
    - New or changed routes/controllers (`src/api/...`).
    - Schema changes in DB or repositories.
    - Business logic changes in services.
  - Update:
    - **API spec** for endpoints.
    - **Master spec** for behavior.
    - **IMPLEMENTATION_SUMMARY** for internal logic.
    - **Changelog** if user-facing/API-facing.

- **Frontend changes (`packages/frontend/...`)**:
  - Look for:
    - New/changed features in `src/features/...`.
    - New UI flows, validation rules, or error handling.
  - Update:
    - **Master spec** if user flows or UX change.
    - **QUICK_REFERENCE** for new flows and examples.
    - **Changelog** if user-visible.

- **Shared changes (`packages/shared/...`)**:
  - Look for:
    - New/changed types or schemas.
    - Constants that affect business rules.
  - Update:
    - **Master spec** for business rules.
    - **IMPLEMENTATION_SUMMARY** for where and how shared pieces are used.
    - **Changelog** if they affect API contracts or domain behavior.

## Output Expectations

When this skill is applied, the assistant should:

1. **Summarize** the impact of code changes in a few bullets per feature.
2. For each relevant doc file:
   - Identify the sections to change or create.
   - Propose **concrete markdown edits**, preserving existing style and language.
3. Present updates in a way that can be easily turned into patches, for example:
   - By showing “before → after” snippets, or
   - By describing the new/updated sections precisely enough to create a patch.

The focus is on:
- **Accuracy**: docs must reflect current behavior and contracts.
- **Minimality**: only change what’s needed.
- **Consistency**: use the same patterns across features and documents.

