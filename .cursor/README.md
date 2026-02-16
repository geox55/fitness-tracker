# Cursor Config — Fitness Tracker

Конфигурация Cursor для Fitness Tracker: agents, skills и rules для AI-ассистированной разработки.

## Prerequisites

### Terminal

- [kitty](https://sw.kovidgoyal.net/kitty/) или [ghostty](https://ghostty.org/)

Рекомендуется:
- [fzf](https://github.com/junegunn/fzf) — fuzzy search
- [bat](https://github.com/sharkdp/bat) — cat с подсветкой синтаксиса

### CLI tools

Подробнее: [rules/CLI.md](./rules/CLI.md)

| tool | replaces | usage |
|------|----------|-------|
| `rg` (ripgrep) | grep | `rg "pattern"` — быстрый regex search |
| `fd` | find | `fd "*.py"` — быстрый поиск файлов |
| `ast-grep` | - | `ast-grep --pattern '$FUNC($$$)' --lang py` — поиск по AST |
| `shellcheck` | - | `shellcheck script.sh` — линтер для shell |
| `shfmt` | - | `shfmt -i 2 -w script.sh` — форматирование shell |
| `wt` | git worktree | `wt switch branch` — управление parallel worktrees |

Для поиска структуры кода предпочитай `ast-grep`; ripgrep — для literal strings и логов.

## Agents

| Agent | Описание |
|-------|----------|
| **tdd-orchestrator** | TDD-оркестратор: red-green-refactor, координация workflow, pytest/FastAPI, Flutter testing |

## Skills

### Discovery & Planning

- **brainstorm** — Socratic dialogue, requirements discovery, multi-persona analysis
- **design** — архитектура, API, БД, компоненты (Mermaid)
- **solution-architect** — требования → архитектура, tech stack, deployment
- **estimation** — T-shirt sizing, bottom-up/top-down оценка

### Implementation

- **implement** — feature/code implementation с personas (architect, frontend, backend, security)
- **test-driven-development-tdd** — pytest, FIRST, AAA, anti-patterns
- **python-fastapi-developer** — FastAPI, Pydantic, SQLAlchemy async, uv

### Infrastructure & Design

- **database-designer** — схемы БД, DrawDB, SQL scripts
- **mcp-builder** — MCP-серверы (Python/Node)

### Workflow & Handoff

- **handover** — сохранение контекста в HANDOVER.md
- **git-commit-message** — Conventional Commits
- **pr-describe** — заголовок и описание PR

### Indexing

- **index-repo** — PROJECT_INDEX.md для 94% token reduction
- **index-repo-py** — индекс для Python/FastAPI проектов

## Rules

### Глобальные

- [CLI.md](./rules/CLI.md) — инструменты командной строки
- [PRINCIPLES.md](./rules/PRINCIPLES.md) — SOLID, DRY, KISS, YAGNI, risk management
- [STANDARDS.md](./rules/STANDARDS.md) — code quality, zero warnings, testing philosophy

### Проектные (agent-requestable)

- [fitness-tracker-project.mdc](./rules/fitness-tracker-project.mdc) — спецификация Fitness Tracker
- [api-specification.mdc](./rules/api-specification.mdc)
- [testing-guidelines.mdc](./rules/testing-guidelines.mdc)
- [security-guidelines.mdc](./rules/security-guidelines.mdc)
- [backend-development.mdc](./rules/backend-development.mdc)
- [frontend-development.mdc](./rules/frontend-development.mdc)
