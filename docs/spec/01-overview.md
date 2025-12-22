# FITNESS TRACKER — OVERVIEW

**Дата:** Декабрь 2025  
**Версия:** 1.0  
**Статус:** APPROVED FOR DEVELOPMENT

---

## Executive Summary

Fitness Tracker — веб-приложение для логирования силовых тренировок с аналитикой прогресса. Система базируется на подходе **Architecture & Design First → Tests Second → Code Third**.

### Ключевые характеристики

- Быстрое логирование тренировок (дата, упражнение, подходы, вес, повторения)
- Визуальная аналитика прогресса (графики по упражнениям и периодам)
- REST API для мобильных приложений
- Стек: React + Vite (Frontend), Fastify (Backend), SQLite, Docker Compose
- **Разработка по циклу RED → GREEN → REFACTOR**

---

## Целевая аудитория

- **Возраст:** 18-50 лет
- **Опыт:** От новичков до опытных спортсменов
- **Поведение:** Активно занимаются в спортзале (2-5 раз в неделю)
- **Tech-savvy:** Готовы использовать веб-приложение + мобильные интеграции

---

## Метрики успеха (OKR)

| Метрика | Цель |
|---------|------|
| DAU | 1,000+ (1 мес), 5,000+ (3 мес) |
| 7-day Retention | ≥ 40% |
| 30-day Retention | ≥ 20% |
| Время логирования подхода | < 30 сек |
| API usage | ≥ 500 calls/день |
| NPS | ≥ 50 |

---

## MVP Scope (Phase 1)

### Включено в MVP

- ✅ Логирование тренировок (форма)
- ✅ График прогресса (последний месяц)
- ✅ Просмотр истории
- ✅ Базовый REST API
- ✅ Docker Compose setup

### Исключено из MVP

- ❌ Шаблоны тренировок
- ❌ Push-уведомления
- ❌ Социум (шеринг)
- ❌ Мобильное приложение

---

## User Stories (Core)

### Story 1: Логирование тренировки

```
As a gym user,
I want to quickly log my workout (exercise, weight, reps) during my session,
So that I don't interrupt my training and can track volume over time.

Acceptance Criteria:
- [ ] Form opens in < 2 sec
- [ ] Prefilled with last weight used
- [ ] Adding a set takes max 3 clicks
- [ ] Works offline (queues sync when online)
```

### Story 2: Просмотр прогресса

```
As a fitness enthusiast,
I want to see my progress on specific exercises (max weight, trends),
So that I can track strength gains and set new PRs.

Acceptance Criteria:
- [ ] Graph shows last 1/3/6/12 months
- [ ] Displays max, average, PR
- [ ] Loads in < 2 sec
- [ ] Responsive on mobile
```

### Story 3: API для интеграций

```
As a mobile app developer,
I want REST API to create/read workout logs,
So that I can build native iOS/Android apps on top of it.

Acceptance Criteria:
- [ ] JWT authentication
- [ ] POST /api/workouts (create)
- [ ] GET /api/workouts (list with filters)
- [ ] GET /api/analytics/progress
- [ ] Rate limit: 1000 req/hour per user
```

---

## Roadmap

| Phase | Сроки | Содержание |
|-------|-------|-----------|
| **Phase 1 (MVP)** | Week 1-3 | Core features, basic API |
| **Phase 2** | Week 4-6 | Templates, export, analytics |
| **Phase 3** | Week 7-10 | Notifications, social, ML |
| **Phase 4** | Future | Mobile app, wearables |

