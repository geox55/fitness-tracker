# Fitness Tracker — Documentation Index

## 📚 Specification Files

| File | Description |
|------|-------------|
| [01-overview.md](./01-overview.md) | Project overview, user stories, MVP scope |
| [02-architecture.md](./02-architecture.md) | Monorepo structure, backend/frontend/database architecture |
| [03-api-specification.md](./03-api-specification.md) | REST API endpoints, request/response formats |
| [04-testing-strategy.md](./04-testing-strategy.md) | TDD workflow, test patterns, coverage targets |
| [05-ui-ux-guidelines.md](./05-ui-ux-guidelines.md) | Design system, components, layouts |
| [06-best-practices.md](./06-best-practices.md) | Development patterns, anti-patterns |
| [07-risk-assessment.md](./07-risk-assessment.md) | Technical, testing, performance risks |
| [08-timeline.md](./08-timeline.md) | Implementation phases, milestones |

## 👥 Role-Specific Guides

| File | Role |
|------|------|
| [roles/backend-developer.md](./roles/backend-developer.md) | Backend developer TDD workflow, patterns |
| [roles/frontend-developer.md](./roles/frontend-developer.md) | Frontend developer FSD patterns, components |
| [roles/qa-engineer.md](./roles/qa-engineer.md) | QA test strategy, E2E scenarios |

## 🎯 Quick Start

### For Backend Development

1. Read [02-architecture.md](./02-architecture.md) — понять структуру
2. Read [03-api-specification.md](./03-api-specification.md) — API контракты
3. Read [roles/backend-developer.md](./roles/backend-developer.md) — workflow

### For Frontend Development

1. Read [02-architecture.md](./02-architecture.md) — FSD структура
2. Read [05-ui-ux-guidelines.md](./05-ui-ux-guidelines.md) — дизайн система
3. Read [roles/frontend-developer.md](./roles/frontend-developer.md) — workflow

### For Testing

1. Read [04-testing-strategy.md](./04-testing-strategy.md) — стратегия
2. Read [roles/qa-engineer.md](./roles/qa-engineer.md) — сценарии

## 🔗 Cursor Rules

Cursor rules автоматически применяются при работе с соответствующими файлами:

| Rule File | Applies To |
|-----------|-----------|
| `fitness-tracker-project.mdc` | All `packages/**/*` files |
| `backend-development.mdc` | `packages/backend/**/*` |
| `frontend-development.mdc` | `packages/frontend/**/*` |
| `testing-guidelines.mdc` | `**/*.test.ts`, `**/*.test.tsx`, `e2e/**/*` |
| `api-specification.mdc` | API routes and clients |

## 📝 Development Workflow

```
Architecture First → Tests Second → Code Third

1. Read spec documentation
2. Write/understand test cases
3. Run test → RED (fails)
4. Implement code → GREEN (passes)
5. Refactor → still GREEN
6. Repeat
```

## 🏗️ Tech Stack

- **Frontend:** React 18, Vite, TanStack Query, Zustand, Recharts, shadcn/ui
- **Backend:** Fastify, better-sqlite3, jose (JWT)
- **Shared:** Zod, TypeScript
- **Testing:** Vitest, Testing Library, Cypress
- **Infrastructure:** Docker, pnpm workspaces

