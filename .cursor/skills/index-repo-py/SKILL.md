---
name: index-repo-py
description: Create or update PROJECT_INDEX.md for python fastapi project
disable-model-invocation: true
---

# Repository Index Creator

Create or update `PROJECT_INDEX.md` — a compact markdown index that gives the LLM full codebase navigation without reading every file.

## Why

- Reading all files costs ~58,000 tokens per session
- Reading the index costs ~1,000 tokens (98% reduction)
- Exports in the index save additional Read tool calls during discovery

## How to Run

**Create index**: `/index-repo`
**Update index**: `/index-repo update`

## Process

1. **Glob** all source and test files in parallel:
   - `src/**/*.py`, `tests/**/*.py`
   - `*.toml`, `Makefile`

2. **Read** each file, extract:
   - Purpose (1-line description)
   - Exports (public classes, functions, constants)
   - Status (only mark stubs — implemented is the default)
   - Endpoints (for routers)
   - Fixtures (for test conftest files)

3. **Write** `PROJECT_INDEX.md` using the compact format below.

## Output Format

Single file: `PROJECT_INDEX.md` (target: <3KB)

```
# {Project Name} | {Framework} | {Python version} | {Package manager}

## Commands
run: {command}
test: {command}
lint: {command}
fix: {command}

## Architecture
- key: value (one line per architectural decision)

## Modules

path/to/file.py — one-line purpose
  exports: Class1, Class2, function1

### path/to/package/ [STUB if not implemented]

file.py — purpose
  exports: ExportedName

## Tests ({count} total, {status})

conftest.py — fixtures: fixture1, fixture2
test_file.py ({count}), test_other.py ({count})
```

## Rules

- **One line per module**: `path — purpose`
- **Exports on indented line below**: `  exports: Name1, Name2`
- **Only mark exceptions**: stubs get `[STUB]`, implemented is assumed
- **Group by directory** with `###` headers to avoid repeating paths
- **Tests are compact**: `test_file.py (count)` on shared lines
- **No duplicated data**: skip deps (in pyproject.toml), CI config, test class names
- **Keep under 3KB**
