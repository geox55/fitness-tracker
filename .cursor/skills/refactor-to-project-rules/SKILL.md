---
name: refactor-to-project-rules
description: Refactors a selected module to comply with project rules by reading .cursor/rules/** as a checklist and producing concrete code diffs instead of prose. Use when the user wants a specific file or module aligned with architecture, error handling, naming, and side-effect guidelines defined in project rules.
---

# Refactor to Project Rules

## Purpose

This skill takes **any module/file** in the Fitness Tracker project and **refactors it to match project rules**, focusing on:
- **Architecture** (layering, responsibilities, dependencies)
- **Error handling** (custom errors, API format, logging)
- **Naming & style** (consistent terminology, types, schema usage)
- **Side-effects & purity** (where side-effects live, how they are isolated)

It must:
- Read **project rules** from `.cursor/rules/**` and treat them as a **checklist**.
- Produce a **concrete diff** (patch-style changes) for the target module and any directly-related files.
- Avoid long essays; comments should be minimal and tied directly to code changes.

## Inputs

The skill expects:
- A **target module/file path** (or small set of files), e.g.:
  - `packages/backend/src/services/workout.service.ts`
  - `packages/frontend/src/features/workouts/ui/add-workout-form.tsx`
- Optionally, a short **refactor scope hint**, e.g.:
  - “Align with controller → service → repository”
  - “Fix error handling to use shared error format”
  - “Remove side-effects from selectors/hooks”

Before making suggestions, the assistant should **read and apply** all relevant rules from:
- `.cursor/rules/fitness-tracker-project.mdc`
- `.cursor/rules/backend-development.mdc` (for `packages/backend/**`)
- `.cursor/rules/frontend-development.mdc` (for `packages/frontend/**`)
- `.cursor/rules/api-specification.mdc` (for API-related code)
- `.cursor/rules/security-guidelines.mdc` (for backend or frontend)
- `.cursor/rules/testing-guidelines.mdc` (for tests)

## High-Level Workflow

1. **Identify applicable rules**
   - Based on the file path, select corresponding rule files:
     - Backend: `packages/backend/**` → backend + security + api + project + testing.
     - Frontend: `packages/frontend/**` → frontend + security + project + testing.
     - Shared: `packages/shared/**` → project + any shared/type/schema rules mentioned.
   - Read those `.mdc` files and extract:
     - Architecture constraints (layers, dirs, allowed dependencies).
     - Error-handling patterns (API shape, custom error types).
     - Naming/style rules (types, schemas, constants, domain terms).
     - Side-effect rules (where IO/async/network/dom manipulations must live).

2. **Scan the target module**
   - Read the full file.
   - Detect violations against the checklist of rules:
     - Wrong layer responsibilities (e.g. DB queries in controllers, business logic in routes).
     - Inconsistent error responses or missing error mapping.
     - Non-standard naming or bypassing shared schemas/types.
     - Side-effects scattered into pure layers or React components where they don’t belong.

3. **Plan concrete refactors**
   - For each violation, decide on:
     - **Minimal change** needed to comply with the rule.
     - Whether it requires:
       - Only local edits in the current file, or
       - Also touching a closely related file (e.g. moving DB logic to repository, moving schema to shared).
   - Group changes by **rule**:
     - “Architecture → Controller/Service split”
     - “Error handling → use shared error format”
     - “Naming → align with shared types/schemas”
     - “Side-effects → isolate into hooks/services”

4. **Generate diffs (not essays)**
   - For each affected file, produce a **patch-style diff** with:
     - Sufficient context (few lines around changes) to safely apply.
     - Code **before** (lines removed) and **after** (lines added).
   - Keep commentary lightweight:
     - Short inline comments or brief explanations near the diff as needed.
     - If a change is based on a specific rule, mention that rule name once near the diff.

## Checklist from Project Rules (Conceptual)

This section defines **what to check** in a typical module, based on `.cursor/rules/**`. It should be interpreted dynamically using the actual rule files, but the patterns are:

### Architecture & Layering

Check:
- Does the module respect the **intended layer responsibilities**? For example:
  - Backend:
    - `Controller`: HTTP + validation + mapping to services.
    - `Service`: business logic only (no HTTP, no DB, no direct IO).
    - `Repository`: DB queries only (no HTTP, minimal logic).
  - Frontend:
    - Feature `model/` handles data-fetching, state, side-effects.
    - Feature `ui/` components remain as **pure** as possible (mostly props/UI, minimal side-effects).
    - Shared `api/` holds API clients and query keys.
- Are modules placed in the right directories consistent with rules?

If violations are found:
- Propose moving code sections to correct layer/files, with explicit diffs for:
  - Removing the code from the wrong place.
  - Adding/rewriting it in the correct file.

### Error Handling

Check:
- Backend:
  - Are errors raised and mapped using **project error utilities** and **custom error types**?
  - Do API handlers return the unified error format:
    ```ts
    { error: string, code?: string, details?: object }
    ```
  - Are domain-specific errors mapped to consistent `code` values?
- Frontend:
  - Are API errors handled using shared helpers (if defined) and surfaced to UI in a consistent way?
  - Does UI avoid leaking raw technical details to end-users?

Refactors should:
- Replace ad-hoc throw/response patterns with standardized error-dispatching and mapping.
- Align error shapes with the API specification rules.

### Naming & Types

Check:
- Are types imported from `@fitness/shared` or shared schema modules where required?
- Are names consistent with:
  - Existing domain terms (e.g. workout, superset, session, exercise, set).
  - API spec naming for payloads/fields.
- Are schemas defined with the preferred library (likely Zod) in the correct shared location?

Refactors should:
- Rename variables/types/fields for consistency.
- Replace inline/duplicated types with imports from shared modules.

### Side-Effects & Purity

Check:
- Backend:
  - Side-effects (DB, network, file IO) belong in specific layers (repositories, infrastructure).
  - Services should be testable with minimal side-effects.
- Frontend:
  - Side-effects (network calls, timers, subscriptions) live in hooks / model layer, not in dumb components.
  - Components should ideally be pure given props and context.

Refactors should:
- Extract side-effectful logic from pure components/services into:
  - Custom hooks (frontend).
  - Dedicated service/repository functions (backend).

## Output Format

When this skill is applied, the assistant should output **only focused, actionable content**, namely:

1. **Short summary** (2–5 bullets) of what will change and which rules are being enforced.
2. **One or more code diffs**, grouped by file:

```markdown
### File: packages/backend/src/services/workout.service.ts

```diff
- // old code
+ // new code
```

### File: packages/backend/src/api/workouts/controller.ts

```diff
- // old code
+ // new code
```
```

Guidelines:
- Avoid long narrative explanations; focus on **code**.
- If a change is non-obvious, a **short comment** above/below the diff is acceptable:

```markdown
// Aligns error handling with security-guidelines.mdc and api-specification.mdc
```diff
...
```
```

3. If a rule suggests additional tests:
   - Briefly mention **which tests** should be added/updated.
   - Optionally include a minimal test diff as well.

## Scope & Limits

- Prefer **small, targeted refactors** that directly enforce rules, rather than complete rewrites.
- If a file is heavily out of compliance:
  - Start with the **highest-impact** issues (e.g. wrong layer, broken error handling).
  - Note that further follow-up refactors may be needed, but still provide concrete diffs for the most important problems first.

The primary goal is to ensure that after applying the diffs:
- The module is **closer to project standards**.
- The changes are **easy to review** because they are small and tied to explicit rules.

