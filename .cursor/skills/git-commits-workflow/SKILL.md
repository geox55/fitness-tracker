---
name: git-commits-workflow
description: Helps group current changes into logical commit sets and generate Conventional Commit messages using feat, build, refactor, and ci types without managing branches. Use when the user is ready to commit and push work in the Fitness Tracker repo.
---

# Git Commits Workflow

## Purpose

This skill helps create **clean, focused commits** from the current git changes by:
- **Analyzing the diff** and grouping files into logical sets.
- Mapping each set to one of the allowed Conventional Commit types: **feat**, **build**, **refactor**, **ci**.
- Generating **English commit messages** following Conventional Commits.
- Guiding through **commit + push** for each set (without branch switching).

The skill **must not**:
- Change branches.
- Use `git commit --amend` or `git push --force` unless the user explicitly asks.

## Allowed Commit Types

Only use these Conventional Commit types:
- **feat**: New user-visible functionality or behavior changes in app features or API.
- **build**: Changes that affect the build system, tooling, dependencies, configs (e.g. Vite, ESLint, TS config, CI config, package.json).
- **refactor**: Internal code changes that don't alter behavior (cleanup, restructuring, renaming, moving code, extracting helpers).
- **ci**: CI/CD related changes (workflows, pipelines, scripts used only in CI).

If a change clearly matches **none** of these types, ask the user which type to use for that group.

## High-Level Workflow

1. **Inspect current git state**
   - Run:
     - `git status --short`
     - `git diff` (for unstaged changes)
     - `git diff --cached` (for staged changes, if any)
   - Work in the **current branch** only.

2. **Group files by logical change and type**
   - Start from the list of changed files.
   - For each file, infer the primary type:
     - **feat**:
       - Frontend feature code under `packages/frontend/src/features/**` (pages, UI, hooks) that add or change behavior.
       - Backend API or service changes that alter behavior or add endpoints in `packages/backend/src/api/**`, `services/**`.
     - **build**:
       - `package.json`, `pnpm-lock.yaml`, `tsconfig*.json`, `vite.config.ts`, `.eslintrc*`, `eslint.config.js`, `.prettierrc*`, `.npmrc`, CI-related configs under `infra/` or `.github/` if used.
       - Tooling or configuration-only changes in `docs/quick-start-dev.md` if describing build/dev setup.
     - **refactor**:
       - Pure code cleanup or reorganization where behavior is intended to stay the same:
         - Moving functions between files.
         - Renaming variables/functions/components without changing logic.
         - Splitting large components/functions into smaller ones.
         - Removing dead code.
     - **ci**:
       - CI/CD configuration (e.g. `.github/workflows/**`, CI scripts under `infra/ci/**`).
   - Group files into **buckets** by type and intent, e.g.:
     - `feat` — workout feature changes in frontend and matching backend API.
     - `build` — dependency and config updates.
     - `refactor` — cleanup of existing workout components without behavioral change.
     - `ci` — GitHub Actions workflow tweaks.

3. **Propose commit plan**
   - For each non-empty bucket, create a plan entry:
     - **Type** (`feat`, `build`, `refactor`, `ci`).
     - **Short scope** in parentheses (e.g. `workouts`, `frontend`, `backend`, `deps`, `ci`).
     - **Files to include** (short list or glob-style summary).
   - Present the plan in a compact list, for example:

     ```markdown
     Planned commits:
     1) feat(workouts): implement workout creation flow
        - packages/frontend/src/features/workouts/**
        - packages/backend/src/api/workouts/**

+     2) refactor(workouts): clean up workout form structure
        - packages/frontend/src/features/workouts/ui/add-workout-form.tsx

     3) build(frontend): update frontend tooling and deps
        - packages/frontend/package.json
        - packages/frontend/vite.config.ts
     ```

   - Ask the user to confirm or adjust the plan **before** staging anything.

4. **Generate Conventional Commit messages**

For each bucket, generate a **single-line summary** and an optional **body**:

- **Header format**:
  - `type(scope): summary`
  - `type` ∈ {`feat`, `build`, `refactor`, `ci`}.
  - `scope`: short, lowercase, no spaces, describes area:
    - examples: `auth`, `workouts`, `backend`, `frontend`, `deps`, `ci`.
  - `summary`: English, imperative, max ~72 chars, describes what, not how.

- **Examples**:
  - `feat(workouts): add workout creation page`
  - `build(frontend): configure vite aliases for features`
  - `refactor(auth): simplify login form validation`
  - `ci(pipeline): speed up test workflow`

- **Body (optional)**:
  - Use when:
    - There are non-obvious decisions.
    - The change spans many files.
  - Short paragraphs or bullet points, for example:

    ```text
    - Extract shared workout form component
    - Keep existing validation schema behavior
    ```

## Detailed Step-by-Step Workflow

### Step 1 — Analyze changes

1. Run:
   - `git status --short`
   - `git diff`
2. From the diff and file paths, categorize each file into one of:
   - `feat`, `build`, `refactor`, `ci`.
3. If a file clearly belongs to multiple types, choose the **dominant intent**:
   - E.g. new feature + small cleanup in same files → treat as **feat**.
4. If a file mixes unrelated changes (e.g. feature + refactor in same file), suggest splitting via **additional edits** where possible, but default to a **single, honest type**.

### Step 2 — Build commit groups

1. For each type, group files by **feature/area**:
   - Common areas in this repo:
     - `auth`, `workouts`, `exercises`, `supersets`, `workout-sessions`.
     - `frontend`, `backend`, `shared`, `deps`, `ci`.
2. Try to keep each commit:
   - **Cohesive**: one behavioral change or one refactor theme.
   - **Reviewable**: avoid huge mixed commits if they can be split.
3. If multiple small related changes exist, group them into a single commit per area and type.

### Step 3 — Propose and refine commit messages

For each planned commit:
1. Draft a header: `type(scope): summary`.
2. Ensure:
   - `summary` describes the **user-facing/behavioral** change for `feat`.
   - `summary` describes the **internal purpose** for `refactor`, `build`, `ci`.
3. Optionally draft a short body listing key points.
4. Show the full proposed message to the user for confirmation.

### Step 4 — Stage and commit per group

For each confirmed commit group (one by one):

1. **Stage files** only for this group:
   - Use explicit paths:
     - `git add path/to/file1 path/to/file2 ...`
   - Or narrow globs (`git add packages/frontend/src/features/workouts/**`) but prefer explicit paths from the plan.
2. Verify staged content:
   - `git diff --cached`
   - Ensure only the intended files/changes are staged.
3. Create the commit:
   - `git commit`
   - Use the generated Conventional Commit header and optional body.
4. Repeat for all groups until:
   - `git status` shows **no staged changes** and only expected untracked files (if any).

### Step 5 — Push changes

1. Ensure the working tree is clean:
   - `git status` → no unstaged/staged changes.
2. Push to the current branch **without** changing branches:
   - `git push`
3. If push is rejected due to remote updates:
   - Do **not** use `--force` automatically.
   - Suggest:
     - `git pull --rebase` or `git fetch` + `git rebase origin/<branch>` depending on the team practice.
   - Only proceed with `--force-with-lease` if the user explicitly requests.

## Output Format When Using This Skill

When applying this skill, structure the response as:

1. **Commit plan overview**
   - Short list of planned commits with type, scope, and included paths.
2. **Suggested commit messages**
   - One header (and optional body) per planned commit.
3. **Staging & push instructions**
   - Exact `git add`, `git commit`, and `git push` commands for each commit in order.

Keep explanations concise and focused on:
- Why a change belongs to `feat`, `build`, `refactor`, or `ci`.
- How to execute the commit and push sequence safely.

