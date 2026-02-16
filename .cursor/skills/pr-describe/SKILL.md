---
name: pr-describe
description: Generate PR title (conventional commits) and description by analyzing branch changes. Use when creating or describing a pull/merge request.
disable-model-invocation: true
---

# /pr-describe — Generate Pull Request Description

Generate a PR title and description based on the current branch changes.

## Algorithm

### 1. Gather context

```bash
# Current branch
git branch --show-current

# Commit log from branch point
git log --oneline main..HEAD

# Scope of changes — understand what's affected first
git diff main...HEAD --stat

# Full diff — change details
git diff main...HEAD
```

### 2. Generate PR title

The title becomes the squash commit message, so strictly follow **Conventional Commits**:

```
<type>(<scope>): <short description>
```

**Types:**
- `feat` — new functionality
- `fix` — bug fix
- `refactor` — code change without behavior change
- `docs` — documentation
- `test` — tests
- `chore` — maintenance, dependencies, CI
- `perf` — performance improvement

**Rules:**
- Imperative mood: "add", not "added" or "adds"
- 72 characters max
- No period at the end
- scope — module or area affected by the changes (optional)
- Breaking change: `feat(api)!: restructure response format`

### 3. Generate PR description

Use this template:

```markdown
## Task
<!-- Link to issue (if found in commits or branch name) and description in own words -->
<Task description: what needed to be done and why>

## Changes
<!-- Key changes — solution logic, not a diff retelling -->
- <Change 1>
- <Change 2>
- ...

## Why this approach
<!-- Explain the chosen approach if non-obvious. Remove this section for trivial changes -->

## How to verify
<!-- Concrete steps for the reviewer -->
1. <Step 1>
2. <Step 2>
3. Expected result: ...
```

### 4. Output result

Output in this format:

```
### PR Title
<title>

### PR Description
<description using the template>
```

## Rules

- **Analyze ALL branch commits**, not just the latest — the PR describes the entire body of work
- **Title should reflect the outcome** for the user/system, not the process ("add user search" not "implement search functionality")
- **"Changes" section** — list logical changes (what the system can do now), not files
- **"How to verify"** — be specific: endpoint, command, UI button. The reviewer should be able to verify in 2 minutes
- **"Why this approach"** — include only when the choice is non-obvious or alternatives were considered. Remove for trivial changes
- If the branch name or commits contain an issue number (PROJ-123, #456) — include it in the "Task" section
