# Fitness Tracker

Monorepo для Fitness Tracker приложения.

## Структура

```
fitness-tracker/
├── packages/
│   ├── backend/      # Fastify REST API
│   ├── frontend/     # Next.js UI
│   └── shared/       # Shared types, schemas
├── docs/             # Документация
└── e2e/              # E2E тесты (Cypress)
```

## Быстрый старт

### Установка

```bash
# Установить pnpm (если еще не установлен)
npm install -g pnpm

# Установить зависимости
pnpm install

# Настроить окружение
cp .env.example .env
# Отредактировать .env файл
```

### Запуск

```bash
# Запустить все сервисы
pnpm dev

# Или отдельно:
pnpm dev:backend   # Backend на http://localhost:4000
pnpm dev:frontend # Frontend на http://localhost:3000
```

### База данных

```bash
# Создать миграции
pnpm --filter @fitness/backend db:migrate

# Заполнить тестовыми данными
pnpm --filter @fitness/backend db:seed
```

### Тестирование

```bash
# Собрать shared-пакет (обязательно перед тестами)
pnpm --filter @fitness/shared build

# Все тесты
pnpm test

# С покрытием
pnpm test:coverage

# Если возникает ошибка "Could not locate the bindings file":
# Пересобрать better-sqlite3 нативный модуль
pnpm --filter @fitness/backend rebuild better-sqlite3
```

**Примечание:** Если тесты не запускаются из-за better-sqlite3, см. раздел [Troubleshooting](./docs/quick-start-dev.md#common-issues--solutions) в документации.

## Документация

Полная документация в папке `docs/`:
- [Спецификация](./docs/spec/README.md)
- [Quick Start для разработчиков](./docs/quick-start-dev.md)
- [Чеклист задач](./docs/deliverables-checklist.md)

## Текущий прогресс

### ✅ Завершено (Backend)
1. ✅ Monorepo структура создана
2. ✅ Auth endpoints (POST /api/auth/login, register, refresh)
3. ✅ Workout endpoints (POST /api/workouts, GET /api/workouts, PATCH /api/workouts/:id, DELETE /api/workouts/:id)
4. ✅ Exercise endpoints (GET /api/exercises с фильтрацией)
5. ✅ Fastify schema validation для всех endpoints
6. ✅ Custom error classes (InvalidWeightError, InvalidRepsError, InvalidSetsError, WorkoutNotFoundError, WorkoutAccessDeniedError)
7. ✅ 31 integration тестов проходят успешно

### 🚧 В процессе
- Backend: Analytics API (GET /api/analytics/progress)
- Backend: Export API (GET /api/analytics/export)
- Frontend: Компоненты и страницы

### ⏭️ Следующие шаги
1. ⏭️ Реализовать Analytics endpoints
2. ⏭️ Реализовать Frontend компоненты (WorkoutForm, ProgressChart)
3. ⏭️ Реализовать Offline support (Service Worker + IndexedDB)

См. [deliverables-checklist.md](./docs/deliverables-checklist.md) для детального плана.

