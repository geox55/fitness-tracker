# COMPREHENSIVE SPECIFICATION: FITNESS TRACKER WITH ANALYTICS
## Architecture First → Tests Second → Development Third

**Дата:** Декабрь 2025  
**Версия:** 1.0  
**Статус:** APPROVED FOR DEVELOPMENT  

---

## EXECUTIVE SUMMARY

Fitness Tracker — веб-приложение для логирования силовых тренировок с аналитикой прогресса. Система базируется на подходе **Architecture & Design First → Tests Second → Code Third**, что гарантирует высокое качество и согласованность между компонентами.

**Ключевые характеристики:**
- Быстрое логирование тренировок (дата, упражнение, подходы, вес, повторения)
- Визуальная аналитика прогресса (графики по упражнениям и периодам)
- REST API для мобильных приложений
- Стек: Next.js (Frontend/Backend), SQLite, Docker Compose
- **Разработка по циклу RED → GREEN → REFACTOR с опорой на предварительно определённые тест-кейсы**

---

## ФАЗА 1: АНАЛИЗ КОНКУРЕНТОВ

### 1.1 Краткое описание конкурентов

| Приложение | Core Features | UI/UX подход | API | Монетизация | Основной недостаток |
|-----------|---------------|-------------|-----|------------|-------------------|
| **Strong** | Шаблоны тренировок, история, charts, Apple Watch синк | Быстрое логирование, календарь истории, charts по упражнениям | Нет публичного API | Freemium ($3.99/мес) | Датированный UI, нет экспорта данных |
| **JEFIT** | 1400+ упражнений, прогресс-трекинг, социум, Apple Health | Большая база упражнений с видео, удобный прогресс-трекер | Закрытый API | Freemium ($8.99/мес) | Интерфейс перегружен, медленнее Strong |
| **Fitbod** | AI-рекомендации тренировок, heatmaps мышц, аналитика | Фокус на рекомендациях, умная подборка упражнений | Нет API (запрашивают) | Freemium ($9.99/мес) | Нет открытого API, зависит от AI |
| **MyFitnessPal** | Nutrion tracking, калории, кардио | Фокус на питании + кардио, слабее в силовых | REST API v2 (OAuth2) | Freemium ($12.99/мес) | Сложный UX для силовых, премиум дорого |
| **Gymnotebook / GymNotes** | Тренировки, notes, heatmaps мышц, export CSV/XML | Простой и минималистичный, быстрое логирование | Нет API | Freemium ($2.99/мес) | Нет облака, только экспорт файлов |

### 1.2 Сравнительная таблица features

| Feature | Strong | JEFIT | Fitbod | MFP | GymNotes |
|---------|--------|-------|--------|-----|----------|
| Быстрое логирование на тренировке | ✅ | ✅ | ✅ | ⚠️ | ✅ |
| Charts прогресса (вес за время) | ✅ | ✅ | ✅ | ⚠️ | ✅ |
| REST API для интеграций | ❌ | ❌ | ❌ | ✅ | ❌ |
| Smartwatch интеграция | ✅ | ✅ | ❌ | ⚠️ | ❌ |
| Упражнения с видео-формой | ✅ | ✅ | ⚠️ | ⚠️ | ⚠️ |
| Социум и шеринг | ⚠️ | ✅ | ❌ | ✅ | ❌ |
| Export данных | ✅ | ⚠️ | ❌ | ✅ | ✅ |
| Автоматизация рекомендаций | ❌ | ❌ | ✅ | ❌ | ❌ |
| Heat maps мышц | ❌ | ⚠️ | ✅ | ❌ | ✅ |
| Notes и журнал | ⚠️ | ✅ | ❌ | ⚠️ | ✅ |

### 1.3 Архитектурные insights из конкурентов

1. **Strong** — минималистичный подход, быстрая регистрация, локальное хранилище (SQLite/Realm), синхронизация на облако
2. **JEFIT** — большая БД упражнений, социальные графики, фокус на сообществе
3. **Fitbod** — AI для подборки, сложная аналитика на бэкенде
4. **MyFitnessPal** — полноценный REST API (OAuth2), интеграции через API
5. **GymNotes** — локальное хранилище, export CSV/XML, нет облака

**Вывод:** Наиболее успешные приложения (Strong, JEFIT) обеспечивают:
- Быстрое добавление тренировки (< 30 сек на подход)
- Четкие графики прогресса за день/неделю/месяц
- Периодическое хранилище (локальное + облако синк)
- REST API для расширяемости (особенно важно)

---

## ФАЗА 2: BEST PRACTICES

### Best Practice #1: One-Tap Logging
**Product:** Пользователь логирует подход за < 30 секунд, не отвлекаясь на тренировке  
**UX/UI:** 
- Предзаполненные поля (вес из прошлого раза, количество повторений по умолчанию)
- Крупные кнопки для ввода (спроектировано для тренировочных перчаток)
- Быстрое переключение между подходами (наверх/вниз, не нужно скролить)

**Technical (Next.js + SQLite):**
```
- Client-side validation (мгновенная feedback)
- Оптимистичное обновление UI (updateLog optimistically, затем sync с сервером)
- IndexedDB для кэша последних логов (offline-first)
```

### Best Practice #2: Contextual Progress Visualization
**Product:** Пользователь видит тренд прогресса (максимум за период, среднее, PR)  
**UX/UI:**
- График линии (вес по времени)
- Маркер PR (Personal Record) на графике
- Переключатель периода (день/неделя/месяц/год) над графиком
- Средний/максимальный вес в заголовке

**Technical (Next.js):**
```
- Выбрать Recharts (легче интегрируется с React, лучше performance)
- Server-side агрегация (POST /api/analytics с фильтрами date_from/date_to)
- Кэширование на клиенте (React Query, stale-while-revalidate)
```

### Best Practice #3: Pre-populated Templates
**Product:** Пользователь повторяет последнюю тренировку одним кликом (экономит 2-3 минуты)  
**UX/UI:**
- Кнопка "Повторить последнюю" в начале логирования
- Быстрые шаблоны (PPL split, Upper/Lower и т.д.)
- Сохранение custom шаблонов

**Technical:**
```
- Таблица workout_templates (user_id, name, exercises JSON)
- GET /api/templates вернёт список шаблонов
- Быстрое копирование с increment по дате
```

### Best Practice #4: Real-time Sync & Offline Capability
**Product:** Данные синхронизируются между устройствами, работает оффлайн  
**UX/UI:**
- Иконка синхронизации (статус: синхронизирован, в процессе, ошибка)
- Очередь локальных изменений (если нет интернета)

**Technical:**
```
- Service Worker для offline-first
- Queue in IndexedDB for offline writes
- Background sync API для отправки очереди при восстановлении соединения
```

### Best Practice #5: Structured Exercise Master Data
**Product:** Пользователь выбирает упражнение из структурированного списка (автодополнение, категории)  
**UX/UI:**
- Поле со списком + autosuggest (типа "Приседание со штангой", фильтруется по типу)
- Категории (ноги, спина, грудь и т.д.) для быстрого поиска
- "Недавние" упражнения первыми

**Technical:**
```
- Таблица exercises (id, name, muscle_group, category)
- GET /api/exercises?search=присед вернёт отфильтрованный список
- Индекс на name для поиска
```

### Best Practice #6: Granular Analytics & Export
**Product:** Пользователь может экспортировать свои данные (CSV, JSON), интегрировать с другими системами  
**UX/UI:**
- Кнопка "Export" в меню
- Выбор периода и упражнений
- Скачивание файла

**Technical:**
```
- Генерация CSV на лету (stream response)
- POST /api/export?format=csv&from=2025-01-01&to=2025-12-31
- Или предагрегированные отчёты в БД для больших данных
```

### Best Practice #7: Smart Notifications & Reminders
**Product:** Пользователь получает напоминание о тренировке (если настроил)  
**UX/UI:**
- Настройки: время тренировок (по дням недели)
- Push-уведомления (браузер, если PWA)
- Email-отчёты (еженедельный прогресс)

**Technical:**
```
- Таблица user_preferences (user_id, reminder_time, reminder_days)
- Background job (cron) для отправки напоминаний
- Могно через node-cron в Next.js
```

---

## ФАЗА 3: UX/UI АНАЛИЗ И УЛУЧШЕНИЯ

### 3.1 User Journey: Основные сценарии

#### Сценарий 1: Логирование тренировки (на тренировке)
```
1. Открыть приложение (быстрый доступ, offline mode)
2. Выбрать упражнение из истории или шаблона
3. Ввести: подходы, вес, повторения, RPE (опционально)
4. Нажать "Добавить подход" (повторить x3-5)
5. Нажать "Завершить упражнение"
6. Перейти к следующему упражнению
7. Нажать "Завершить тренировку"
8. Синхронизация с сервером
Time: 30-60 секунд на упражнение
```

#### Сценарий 2: Просмотр прогресса (дома, анализ)
```
1. Открыть приложение
2. Перейти на вкладку "Прогресс"
3. Выбрать упражнение (присед, жим и т.д.)
4. Выбрать период (неделя/месяц/год)
5. Увидеть график (вес по времени)
6. Увидеть статистику (макс, средний, PR)
7. Опционально: экспортировать или поделиться
```

#### Сценарий 3: Планирование тренировки (вечер перед тренировкой)
```
1. Открыть приложение
2. Перейти на вкладку "Планы"
3. Выбрать или создать шаблон (PPL, Upper/Lower)
4. Добавить упражнения
5. Сохранить шаблон
6. На тренировке: использовать шаблон + логировать данные
```

### 3.2 Pain Points в существующих приложениях

| Pain Point | Как это проявляется | Наше решение |
|-----------|-------------------|-------------|
| Слишком много кликов для логирования | Strong требует 5-6 кликов на подход | Максимум 2-3 клика, enter для ввода |
| Медленная загрузка графиков | JEFIT иногда зависает при построении графика | Клиент-сайд агрегация (React Query + Recharts) |
| Потеря данных при офлайне | MFP не синхронизирует без интернета | Service Worker + Queue in IndexedDB |
| Сложный поиск упражнения | JEFIT требует много скроллинга | Autosuggest + недавние + категории |
| Нет API для интеграций | Fitbod, Strong, JEFIT — закрытые API | REST API (OAuth2) для всех операций |
| Экспорт данных недостаточно гибкий | только CSV или proprietary format | JSON, CSV, с фильтром по периодам |

### 3.3 UI-компоненты (Design System)

**Цветовая схема (на основе персональной предпочтений):**
```
Primary: #2180 8D (Teal)         — Active buttons, links
Secondary: #5E5240 (Brown)        — Secondary actions
Background: #FCFCF9 (Cream light) — Main background
Surface: #FFFFFD (Cream)          — Card background
Text: #134252 (Dark slate)        — Primary text
Text-secondary: #626C71 (Slate)   — Helper text
Success: #218081 (Teal)           — PR, achievements
Warning: #A84B2F (Orange)         — Warnings, validations
Error: #C0152F (Red)              — Errors
```

**Компоненты:**
1. **WorkoutForm** — Форма логирования (упражнение, подходы, вес, повторения)
2. **WorkoutCard** — Карточка истории тренировки
3. **ProgressChart** — График прогресса (Recharts)
4. **ExerciseSelect** — Dropdown/autosuggest выбора упражнения
5. **FilterBar** — Фильтр по дате, упражнению
6. **StatsBadge** — Знак статистики (макс, средний, PR)
7. **Header** — Заголовок с навигацией
8. **BottomNav** — Нижняя навигация (Логирование, История, Прогресс, Профиль)

**Типографика:**
```
Heading 1: 30px, weight 600, letter-spacing -0.01em
Heading 2: 24px, weight 600
Heading 3: 18px, weight 550
Body: 14px, weight 400, line-height 1.5
Small: 12px, weight 400
Label: 12px, weight 500
```

**Spacing:**
```
xs: 4px, sm: 8px, md: 16px, lg: 24px, xl: 32px
```

**Radius:**
```
sm: 6px, md: 8px, lg: 12px, full: 9999px
```

### 3.4 UX-флоу: Детальные экраны

#### Экран 1: Логирование тренировки
```
┌─────────────────────────────┐
│ Новая тренировка  [×]       │  ← Header
├─────────────────────────────┤
│ 🏋️ Упражнение              │
│ ┌──────────────────────────┐│
│ │ Поиск или выбрать...     ││ ← ExerciseSelect с autosuggest
│ └──────────────────────────┘│
├─────────────────────────────┤
│ Текущий подход: 1 / 5      │
├─────────────────────────────┤
│ Вес (кг)                   │
│ ┌──────────────────────────┐│
│ │ 100                      ││ ← Input, prefilled from history
│ └──────────────────────────┘│
│ Повторения                 │
│ ┌──────────────────────────┐│
│ │ 5                        ││ ← Input, prefilled
│ └──────────────────────────┘│
│ RPE (опционально)         │
│ ┌──────────────────────────┐│
│ │ 7 / 10                   ││ ← Slider or input
│ └──────────────────────────┘│
├─────────────────────────────┤
│ [Добавить подход] [↓ Минус] │ ← Большие кнопки
├─────────────────────────────┤
│ Сохранённые подходы:      │
│ 100 x 5 | 100 x 5 | ...   │ ← История подходов для быстрого просмотра
├─────────────────────────────┤
│ [Завершить] [Отмена]       │
└─────────────────────────────┘
```

#### Экран 2: Просмотр прогресса
```
┌─────────────────────────────┐
│ Прогресс                   │ ← Header
├─────────────────────────────┤
│ Фильтр:                    │
│ [Все упражнения ▼]  [Период ▼] │
├─────────────────────────────┤
│ Упражнение: Присед        │
│ Период: Последний месяц   │
├─────────────────────────────┤
│ Макс: 150 кг | Средний: 120 кг │ ← StatsBadge
│ PR: 155 кг (2024-12-01)    │
├─────────────────────────────┤
│                            │
│    150 ┼─────────┐          │
│       │         │          │
│  125  ┼─┐       ├─────┐    │ ← Recharts LineCh art
│       │ │       │     │    │
│  100  ┼─┤       │     ├──┐ │
│       │ │       │     │  │ │
│   75  ┼─┤       │     │  └─┤
│       └─┴───────┴─────┴────┘
│  01.12  05.12  10.12  15.12 20.12
│
├─────────────────────────────┤
│ Данные по датам:           │
│ 2024-12-20: 150 кг x 3     │
│ 2024-12-18: 145 кг x 5     │
│ 2024-12-15: 145 кг x 3     │ ← Список с детальными данными
├─────────────────────────────┤
│ [Export] [Share]           │
└─────────────────────────────┘
```

#### Экран 3: История тренировок
```
┌─────────────────────────────┐
│ История                    │
├─────────────────────────────┤
│ Фильтр:                    │
│ [Дата ▼] [Упражнение ▼]   │
├─────────────────────────────┤
│ 2024-12-20                 │ ← WorkoutCard
│ Верхняя часть тела          │
│ • Жим лежа: 100 кг x 5x3    │
│ • Тяга штанги: 120 кг x 5x4 │
│ Длительность: 45 мин        │
├─────────────────────────────┤
│ 2024-12-18                 │
│ Нижняя часть тела          │
│ • Присед: 150 кг x 3x5      │
│ • Становая: 180 кг x 1x3    │
│ Длительность: 50 мин        │
├─────────────────────────────┤
│ 2024-12-15                 │
│ Верхняя часть тела          │
│ • Жим лежа: 95 кг x 5x3     │ ← Вес ниже, видна тенденция
│ ...
└─────────────────────────────┘
```

### 3.5 Responsive Design
- **Mobile (< 640px):** Bottom navigation, full-width forms, vertical charts
- **Tablet (640px - 1024px):** Side navigation, grid layout (2-column)
- **Desktop (> 1024px):** Side navigation, full analytics dashboard (3-column)

### 3.6 Accessibility
- **Keyboard navigation:** Tab между полями, Enter для submit
- **ARIA labels:** Все кнопки и инпуты имеют aria-label
- **Color contrast:** 4.5:1 для текста, 3:1 для крупных элементов
- **Focus indicators:** Visible outline on keyboard navigation

### 3.7 Performance
- **Chart rendering:** Recharts на клиенте, но с виртуализацией (max 6 месяцев на экран)
- **Form validation:** Client-side (instant feedback)
- **Image optimization:** Lazy loading для карточек истории
- **Caching:** React Query с stale-while-revalidate стратегией

---

## ФАЗА 4: АРХИТЕКТУРА СИСТЕМЫ

### 4.1 Frontend Architecture (Next.js)

#### Структура папок
```
fitness-tracker/
├── app/
│   ├── page.tsx                    # Home / Dashboard
│   ├── layout.tsx                  # Root layout
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   ├── register/page.tsx
│   │   └── layout.tsx
│   ├── (protected)/
│   │   ├── dashboard/page.tsx      # Main app
│   │   ├── progress/page.tsx       # Analytics
│   │   ├── history/page.tsx        # Workout history
│   │   ├── profile/page.tsx
│   │   └── layout.tsx              # Protected layout (with sidebar)
│   └── api/                        # API routes (backend)
├── components/
│   ├── ui/
│   │   ├── Button.tsx              # Primitive components
│   │   ├── Input.tsx
│   │   ├── Card.tsx
│   │   ├── Select.tsx
│   │   └── ...
│   ├── forms/
│   │   ├── WorkoutForm.tsx         # Domain components
│   │   ├── ExerciseSelect.tsx
│   │   └── DateFilter.tsx
│   ├── charts/
│   │   ├── ProgressChart.tsx       # Recharts wrapper
│   │   └── ProgressStats.tsx
│   ├── layout/
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   ├── BottomNav.tsx
│   │   └── Layout.tsx
│   └── workouts/
│       ├── WorkoutCard.tsx         # Feature-specific
│       ├── WorkoutList.tsx
│       └── WorkoutTemplate.tsx
├── lib/
│   ├── api/
│   │   ├── client.ts               # Fetch wrapper with auth
│   │   ├── workouts.ts             # API methods
│   │   ├── analytics.ts
│   │   └── exercises.ts
│   ├── db/
│   │   ├── schema.ts               # Zod schemas
│   │   └── validators.ts
│   ├── utils/
│   │   ├── format.ts               # Date, weight formatting
│   │   ├── calculations.ts         # Progress calc
│   │   └── constants.ts
│   └── hooks/
│       ├── useWorkouts.ts          # Custom hooks
│       ├── useAnalytics.ts
│       ├── useLocalStorage.ts
│       └── useOfflineQueue.ts
├── store/
│   ├── workouts.ts                 # Zustand stores
│   ├── ui.ts
│   └── auth.ts
├── public/
│   └── ...
├── styles/
│   ├── globals.css                 # Design system variables
│   └── ...
└── types/
    ├── workout.ts                  # TypeScript interfaces
    ├── exercise.ts
    ├── analytics.ts
    └── api.ts
```

#### State Management: Zustand
```typescript
// store/workouts.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface WorkoutLog {
  id: string;
  exerciseId: string;
  weight: number;
  reps: number;
  sets: number;
  date: Date;
  rpe?: number;
}

interface WorkoutStore {
  logs: WorkoutLog[];
  pendingLogs: WorkoutLog[]; // Offline queue
  addLog: (log: WorkoutLog) => void;
  removeLog: (id: string) => void;
  syncPending: () => Promise<void>;
}

export const useWorkoutStore = create<WorkoutStore>()(
  persist(
    (set) => ({
      logs: [],
      pendingLogs: [],
      addLog: (log) => set((state) => ({
        logs: [log, ...state.logs],
        pendingLogs: [log, ...state.pendingLogs] // Add to offline queue
      })),
      removeLog: (id) => set((state) => ({
        logs: state.logs.filter(l => l.id !== id)
      })),
      syncPending: async () => {
        // Sync offline logs to server
      }
    }),
    { name: 'workout-store' }
  )
);
```

#### Data Fetching: React Query (TanStack Query)
```typescript
// lib/api/workouts.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export const useWorkouts = (filters?: WorkoutFilters) => {
  return useQuery({
    queryKey: ['workouts', filters],
    queryFn: async () => {
      const res = await fetch(`/api/workouts?${new URLSearchParams(filters)}`);
      return res.json();
    },
    staleTime: 1000 * 60 * 5, // 5 min
    gcTime: 1000 * 60 * 30, // 30 min
  });
};

export const useAddWorkout = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (log: WorkoutLog) => {
      const res = await fetch('/api/workouts', {
        method: 'POST',
        body: JSON.stringify(log)
      });
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workouts'] });
    }
  });
};
```

#### Charts: Recharts
```typescript
// components/charts/ProgressChart.tsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from 'recharts';

interface ChartData {
  date: string;
  weight: number;
  reps: number;
}

export const ProgressChart: React.FC<{ data: ChartData[] }> = ({ data }) => {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis />
        <Line 
          type="monotone" 
          dataKey="weight" 
          stroke="#218081" 
          dot={false}
          isAnimationActive={true}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};
```

#### Offline Support: Service Worker
```typescript
// lib/offline/service-worker.ts
// Service Worker for caching and offline support
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');
}

// IndexedDB for offline queue
export const addToOfflineQueue = async (log: WorkoutLog) => {
  const db = await openDB('fitness-tracker');
  await db.add('offline-queue', log);
};

export const syncQueue = async () => {
  const db = await openDB('fitness-tracker');
  const logs = await db.getAll('offline-queue');
  
  for (const log of logs) {
    try {
      await fetch('/api/workouts', {
        method: 'POST',
        body: JSON.stringify(log)
      });
      await db.delete('offline-queue', log.id);
    } catch (err) {
      console.error('Sync failed', err);
    }
  }
};
```

### 4.2 Backend Architecture (Next.js API Routes)

#### API Routes Structure
```
api/
├── auth/
│   ├── login.ts                    # POST /api/auth/login
│   ├── register.ts                 # POST /api/auth/register
│   ├── logout.ts                   # POST /api/auth/logout
│   └── refresh.ts                  # POST /api/auth/refresh
├── workouts/
│   ├── route.ts                    # GET /api/workouts, POST /api/workouts
│   ├── [id]/route.ts               # GET, PATCH, DELETE /api/workouts/:id
│   └── bulk.ts                     # POST /api/workouts/bulk (sync)
├── exercises/
│   ├── route.ts                    # GET /api/exercises?search=...
│   └── index.ts                    # GET /api/exercises/index (full list)
├── analytics/
│   ├── progress.ts                 # GET /api/analytics/progress
│   ├── summary.ts                  # GET /api/analytics/summary
│   └── export.ts                   # GET /api/analytics/export?format=csv
├── templates/
│   ├── route.ts                    # GET /api/templates, POST /api/templates
│   └── [id]/route.ts               # PATCH, DELETE
└── health.ts                       # GET /api/health (ping)
```

#### Middleware & Auth
```typescript
// lib/middleware.ts
import { jwtVerify } from 'jose';

const secret = new TextEncoder().encode(process.env.JWT_SECRET!);

export async function authMiddleware(req: Request) {
  const token = req.headers.get('authorization')?.split(' ')[1];
  if (!token) throw new Error('Unauthorized');
  
  try {
    const { payload } = await jwtVerify(token, secret);
    return payload as { userId: string; email: string };
  } catch (err) {
    throw new Error('Invalid token');
  }
}
```

#### API Implementation Pattern: Handler → Service → Repository
```typescript
// api/workouts/route.ts (Controller/Handler)
import { NextRequest, NextResponse } from 'next/server';
import { authMiddleware } from '@/lib/middleware';
import { WorkoutService } from '@/server/services/workout.service';

export async function POST(req: NextRequest) {
  try {
    const user = await authMiddleware(req);
    const body = await req.json();
    
    // Validate input
    const validated = workoutSchema.parse(body);
    
    // Call service
    const service = new WorkoutService();
    const result = await service.createWorkout(user.userId, validated);
    
    return NextResponse.json(result, { status: 201 });
  } catch (err) {
    return NextResponse.json({ error: err.message }, { status: 400 });
  }
}

export async function GET(req: NextRequest) {
  try {
    const user = await authMiddleware(req);
    const { searchParams } = new URL(req.url);
    
    const filters = {
      exerciseId: searchParams.get('exerciseId'),
      from: searchParams.get('from'),
      to: searchParams.get('to'),
      limit: parseInt(searchParams.get('limit') || '100'),
      offset: parseInt(searchParams.get('offset') || '0'),
    };
    
    const service = new WorkoutService();
    const result = await service.getWorkouts(user.userId, filters);
    
    return NextResponse.json(result);
  } catch (err) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
```

#### Service Layer
```typescript
// server/services/workout.service.ts
import { WorkoutRepository } from '../repositories/workout.repository';
import { AnalyticsService } from './analytics.service';

export class WorkoutService {
  private repo = new WorkoutRepository();
  private analytics = new AnalyticsService();
  
  async createWorkout(userId: string, data: WorkoutInput) {
    // Validate business logic
    if (data.weight <= 0) throw new Error('Weight must be positive');
    if (data.reps < 1 || data.reps > 100) throw new Error('Invalid reps');
    
    // Create record
    const workout = await this.repo.create(userId, data);
    
    // Update aggregated analytics
    await this.analytics.updateAggregates(userId, data.exerciseId);
    
    return workout;
  }
  
  async getWorkouts(userId: string, filters: WorkoutFilters) {
    return this.repo.find(userId, filters);
  }
  
  async deleteWorkout(userId: string, workoutId: string) {
    const workout = await this.repo.findOne(userId, workoutId);
    if (!workout) throw new Error('Not found');
    
    await this.repo.delete(workoutId);
    await this.analytics.updateAggregates(userId, workout.exerciseId);
    
    return { success: true };
  }
}
```

#### Repository Layer
```typescript
// server/repositories/workout.repository.ts
import { Database } from '@/server/db/database';

export class WorkoutRepository {
  private db = Database.getInstance();
  
  async create(userId: string, data: WorkoutInput) {
    const stmt = this.db.prepare(`
      INSERT INTO workout_logs (
        user_id, exercise_id, weight, reps, sets, date, rpe
      ) VALUES (?, ?, ?, ?, ?, ?, ?)
    `);
    
    const result = stmt.run(
      userId,
      data.exerciseId,
      data.weight,
      data.reps,
      data.sets || 1,
      new Date().toISOString(),
      data.rpe || null
    );
    
    return { id: result.lastInsertRowid, ...data };
  }
  
  async find(userId: string, filters: WorkoutFilters) {
    let query = `
      SELECT * FROM workout_logs 
      WHERE user_id = ?
    `;
    const params: any[] = [userId];
    
    if (filters.exerciseId) {
      query += ` AND exercise_id = ?`;
      params.push(filters.exerciseId);
    }
    
    if (filters.from) {
      query += ` AND date >= ?`;
      params.push(filters.from);
    }
    
    if (filters.to) {
      query += ` AND date <= ?`;
      params.push(filters.to);
    }
    
    query += ` ORDER BY date DESC LIMIT ? OFFSET ?`;
    params.push(filters.limit, filters.offset);
    
    const stmt = this.db.prepare(query);
    return stmt.all(...params);
  }
}
```

### 4.3 Database Architecture (SQLite)

#### Database Schema
```sql
-- Users table
CREATE TABLE users (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Exercises master data
CREATE TABLE exercises (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  muscle_group TEXT NOT NULL,      -- 'chest', 'back', 'legs', etc.
  category TEXT,                    -- 'compound', 'isolation'
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_exercises_name ON exercises(name);
CREATE INDEX idx_exercises_muscle_group ON exercises(muscle_group);

-- Workout logs (main data)
CREATE TABLE workout_logs (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  exercise_id TEXT NOT NULL,
  weight DECIMAL(10, 2) NOT NULL,   -- in kg
  reps INTEGER NOT NULL CHECK (reps > 0),
  sets INTEGER DEFAULT 1 CHECK (sets > 0),
  rpe DECIMAL(3, 1),                -- Rate of Perceived Exertion (1-10)
  duration INTEGER,                 -- in seconds
  notes TEXT,
  date DATETIME NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE RESTRICT
);
CREATE INDEX idx_workout_logs_user_date ON workout_logs(user_id, date DESC);
CREATE INDEX idx_workout_logs_user_exercise ON workout_logs(user_id, exercise_id);
CREATE INDEX idx_workout_logs_date ON workout_logs(date);

-- Aggregated analytics (pre-calculated for performance)
CREATE TABLE analytics_aggregates (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  exercise_id TEXT NOT NULL,
  period_date DATE NOT NULL,        -- Start of period (YYYY-MM-DD for day/week/month)
  max_weight DECIMAL(10, 2),
  avg_weight DECIMAL(10, 2),
  total_volume DECIMAL(15, 2),      -- sum(weight * reps * sets)
  total_reps INTEGER,
  workout_count INTEGER,
  personal_record DECIMAL(10, 2),
  personal_record_date DATETIME,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE CASCADE,
  UNIQUE (user_id, exercise_id, period_date)
);
CREATE INDEX idx_analytics_user_exercise ON analytics_aggregates(user_id, exercise_id);

-- Workout templates (for quick repeating workouts)
CREATE TABLE workout_templates (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  name TEXT NOT NULL,               -- 'PPL Upper', 'Lower Body'
  description TEXT,
  exercises_json TEXT NOT NULL,     -- JSON array of exercise configs
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE INDEX idx_templates_user ON workout_templates(user_id);

-- User preferences
CREATE TABLE user_preferences (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL UNIQUE,
  reminder_enabled BOOLEAN DEFAULT 1,
  reminder_time TEXT,               -- 'HH:MM' format
  reminder_days TEXT,               -- JSON array ['MON', 'WED', 'FRI']
  units TEXT DEFAULT 'kg',          -- 'kg' or 'lbs'
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

#### Migration System
```typescript
// server/db/migrations.ts
export const migrations = [
  {
    version: 1,
    up: (db) => {
      db.exec(`
        CREATE TABLE users (...);
        CREATE TABLE exercises (...);
        CREATE TABLE workout_logs (...);
      `);
    }
  },
  {
    version: 2,
    up: (db) => {
      db.exec(`
        CREATE TABLE analytics_aggregates (...);
        CREATE INDEX idx_analytics_user_exercise ON analytics_aggregates(...);
      `);
    }
  }
];
```

#### Database Singleton (Connection Pooling)
```typescript
// server/db/database.ts
import Database from 'better-sqlite3';

export class Database {
  private static instance: Database.Database;
  
  static getInstance(): Database.Database {
    if (!Database.instance) {
      Database.instance = new Database('./data/fitness.db');
      Database.instance.pragma('journal_mode = WAL');
      Database.instance.pragma('foreign_keys = ON');
      Database.instance.pragma('busy_timeout = 5000');
    }
    return Database.instance;
  }
  
  static runMigrations() {
    const db = this.getInstance();
    let currentVersion = 0;
    
    try {
      const result = db.prepare('PRAGMA user_version').get() as any;
      currentVersion = result.user_version;
    } catch (e) {
      // Table doesn't exist, start fresh
    }
    
    for (const migration of migrations) {
      if (migration.version > currentVersion) {
        migration.up(db);
        db.prepare(`PRAGMA user_version = ${migration.version}`).run();
      }
    }
  }
}
```

#### Analytics Aggregation (Background Job)
```typescript
// server/jobs/aggregate-analytics.ts
import { Database } from '@/server/db/database';

export async function aggregateAnalytics(userId: string, exerciseId: string) {
  const db = Database.getInstance();
  
  // Get all logs for this user & exercise
  const logs = db.prepare(`
    SELECT * FROM workout_logs 
    WHERE user_id = ? AND exercise_id = ?
    ORDER BY date DESC
  `).all(userId, exerciseId) as WorkoutLog[];
  
  // Group by day/week/month
  const byDay = groupBy(logs, log => 
    log.date.toISOString().split('T')[0]
  );
  
  // Insert or update aggregates
  for (const [dateStr, dayLogs] of Object.entries(byDay)) {
    const maxWeight = Math.max(...dayLogs.map(l => l.weight));
    const avgWeight = dayLogs.reduce((s, l) => s + l.weight, 0) / dayLogs.length;
    const totalVolume = dayLogs.reduce((s, l) => s + (l.weight * l.reps * l.sets), 0);
    
    db.prepare(`
      INSERT INTO analytics_aggregates (
        id, user_id, exercise_id, period_date, max_weight, avg_weight, 
        total_volume, total_reps, workout_count, personal_record, personal_record_date
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ON CONFLICT (user_id, exercise_id, period_date) 
      DO UPDATE SET 
        max_weight = excluded.max_weight,
        avg_weight = excluded.avg_weight,
        total_volume = excluded.total_volume
    `).run(
      crypto.randomUUID(),
      userId,
      exerciseId,
      dateStr,
      maxWeight,
      avgWeight,
      totalVolume,
      dayLogs.reduce((s, l) => s + l.reps, 0),
      dayLogs.length,
      maxWeight,
      dayLogs[0].date
    );
  }
}
```

### 4.4 Docker Compose

```yaml
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - DATABASE_URL=./data/fitness.db
      - JWT_SECRET=${JWT_SECRET}
      - NEXT_PUBLIC_API_URL=http://localhost:3000
    volumes:
      - ./:/app
      - /app/node_modules
      - fitness_data:/app/data
    depends_on:
      - db
    command: npm run dev

  db:
    image: sqlite3:latest
    volumes:
      - fitness_data:/app/data
    # SQLite runs in-process, so we don't expose it

volumes:
  fitness_data:
```

#### Dockerfile
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

### 4.5 API Specification (OpenAPI Overview)

```yaml
openapi: 3.0.0
info:
  title: Fitness Tracker API
  version: 1.0.0

paths:
  /api/workouts:
    get:
      summary: Get user's workout logs
      parameters:
        - name: exerciseId
          in: query
          schema:
            type: string
        - name: from
          in: query
          schema:
            type: string
            format: date-time
        - name: to
          in: query
          schema:
            type: string
            format: date-time
        - name: limit
          in: query
          schema:
            type: integer
            default: 100
      responses:
        200:
          description: Success
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/WorkoutLog'
    post:
      summary: Create workout log
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/WorkoutInput'
      responses:
        201:
          description: Created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/WorkoutLog'

  /api/analytics/progress:
    get:
      summary: Get progress analytics
      parameters:
        - name: exerciseId
          in: query
          required: true
          schema:
            type: string
        - name: from
          in: query
          schema:
            type: string
            format: date-time
        - name: to
          in: query
          schema:
            type: string
            format: date-time
      responses:
        200:
          description: Success
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                  stats:
                    $ref: '#/components/schemas/ProgressStats'

  /api/exercises:
    get:
      summary: Search exercises
      parameters:
        - name: search
          in: query
          schema:
            type: string
      responses:
        200:
          description: Success
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Exercise'

components:
  schemas:
    WorkoutLog:
      type: object
      properties:
        id:
          type: string
        exerciseId:
          type: string
        weight:
          type: number
        reps:
          type: integer
        sets:
          type: integer
        date:
          type: string
          format: date-time
        rpe:
          type: number
          nullable: true
      required:
        - id
        - exerciseId
        - weight
        - reps
        - date

    WorkoutInput:
      type: object
      properties:
        exerciseId:
          type: string
        weight:
          type: number
        reps:
          type: integer
        sets:
          type: integer
        rpe:
          type: number
          nullable: true
      required:
        - exerciseId
        - weight
        - reps

    Exercise:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        muscleGroup:
          type: string
        category:
          type: string

    ProgressStats:
      type: object
      properties:
        maxWeight:
          type: number
        avgWeight:
          type: number
        personalRecord:
          type: number
        workoutCount:
          type: integer
```

---

## ФАЗА 5: СТРАТЕГИЯ ТЕСТИРОВАНИЯ

### 🔴 КРИТИЧЕСКОЕ ТРЕБОВАНИЕ
**Тесты проектируются и описываются ПОСЛЕ архитектуры и UX, но ДО начала разработки кода. Разработчики начинают с RED → GREEN → REFACTOR, с опорой на уже определённые тест-кейсы.**

---

### 5.1 Backend Testing Strategy

#### 5.1.1 Unit Tests (Сервисный уровень)

**Область 1: Валидация входных данных**

```gherkin
Feature: Workout Log Validation
  Scenario: Reject negative weight
    Given a workout log with weight = -10
    When attempting to create the log
    Then return error "Weight must be positive"
    
  Scenario: Reject invalid reps (0 or > 100)
    Given a workout log with reps = 0
    When attempting to create the log
    Then return error "Reps must be between 1 and 100"
    
  Scenario: Accept valid weight and reps
    Given a workout log with weight = 100 and reps = 5
    When attempting to create the log
    Then the log is created successfully
```

**Test Code:**
```typescript
// server/services/__tests__/workout.service.test.ts
import { WorkoutService } from '../workout.service';

describe('WorkoutService', () => {
  let service: WorkoutService;
  
  beforeEach(() => {
    service = new WorkoutService();
  });
  
  describe('createWorkout', () => {
    it('should reject negative weight', async () => {
      const log = {
        userId: 'user1',
        exerciseId: 'ex1',
        weight: -10,
        reps: 5
      };
      
      await expect(service.createWorkout('user1', log))
        .rejects.toThrow('Weight must be positive');
    });
    
    it('should reject reps = 0', async () => {
      const log = {
        exerciseId: 'ex1',
        weight: 100,
        reps: 0
      };
      
      await expect(service.createWorkout('user1', log))
        .rejects.toThrow('Reps must be between 1 and 100');
    });
    
    it('should accept valid weight and reps', async () => {
      const log = {
        exerciseId: 'ex1',
        weight: 100,
        reps: 5
      };
      
      const result = await service.createWorkout('user1', log);
      expect(result).toHaveProperty('id');
      expect(result.weight).toBe(100);
    });
  });
});
```

**Область 2: Расчёт прогресса**

```gherkin
Feature: Progress Calculation
  Scenario: Calculate max weight for exercise
    Given workout logs: 100kg, 95kg, 110kg, 100kg
    When fetching max weight for the period
    Then return 110kg
    
  Scenario: Calculate average weight
    Given workout logs: 100kg, 100kg, 100kg, 100kg (4 logs)
    When fetching average weight
    Then return 100kg
    
  Scenario: Identify personal record with date
    Given workout logs: 100kg (2024-12-01), 110kg (2024-12-05), 105kg (2024-12-10)
    When fetching PR
    Then return { weight: 110kg, date: 2024-12-05 }
```

**Test Code:**
```typescript
describe('ProgressCalculation', () => {
  let service: AnalyticsService;
  
  beforeEach(() => {
    service = new AnalyticsService();
  });
  
  it('should calculate max weight correctly', () => {
    const logs = [
      { weight: 100, reps: 5 },
      { weight: 95, reps: 5 },
      { weight: 110, reps: 3 },
      { weight: 100, reps: 5 }
    ];
    
    const max = service.calculateMaxWeight(logs);
    expect(max).toBe(110);
  });
  
  it('should calculate average weight correctly', () => {
    const logs = [
      { weight: 100 },
      { weight: 100 },
      { weight: 100 },
      { weight: 100 }
    ];
    
    const avg = service.calculateAverageWeight(logs);
    expect(avg).toBe(100);
  });
  
  it('should identify personal record with date', () => {
    const logs = [
      { weight: 100, date: new Date('2024-12-01') },
      { weight: 110, date: new Date('2024-12-05') },
      { weight: 105, date: new Date('2024-12-10') }
    ];
    
    const pr = service.getPersonalRecord(logs);
    expect(pr.weight).toBe(110);
    expect(pr.date).toEqual(new Date('2024-12-05'));
  });
});
```

**Область 3: Агрегация и фильтрация**

```gherkin
Feature: Workout Log Filtering & Aggregation
  Scenario: Filter by exercise ID
    Given logs with exercise IDs: ex1, ex1, ex2, ex1
    When filtering by exercise_id = ex1
    Then return 3 logs
    
  Scenario: Filter by date range
    Given logs with dates: 2024-12-01, 2024-12-05, 2024-12-10
    When filtering from 2024-12-05 to 2024-12-10
    Then return 2 logs (2024-12-05 and 2024-12-10)
    
  Scenario: Aggregate by day
    Given 5 logs on 2024-12-01 (different weights)
    When aggregating by day
    Then return 1 record with stats: max, avg, total_volume
```

**Test Code:**
```typescript
describe('FilterAndAggregate', () => {
  it('should filter by exercise ID', () => {
    const logs = [
      { exerciseId: 'ex1' },
      { exerciseId: 'ex1' },
      { exerciseId: 'ex2' },
      { exerciseId: 'ex1' }
    ];
    
    const filtered = logs.filter(l => l.exerciseId === 'ex1');
    expect(filtered).toHaveLength(3);
  });
  
  it('should filter by date range', () => {
    const logs = [
      { date: new Date('2024-12-01') },
      { date: new Date('2024-12-05') },
      { date: new Date('2024-12-10') }
    ];
    
    const from = new Date('2024-12-05');
    const to = new Date('2024-12-10');
    const filtered = logs.filter(l => l.date >= from && l.date <= to);
    
    expect(filtered).toHaveLength(2);
  });
});
```

#### 5.1.2 Integration Tests

**Область 1: POST /api/workouts (успешный сценарий и ошибки)**

```gherkin
Feature: Create Workout Endpoint
  Scenario: Successfully create workout with valid data
    Given user is authenticated
    And request body: { exerciseId: ex1, weight: 100, reps: 5 }
    When POSTing to /api/workouts
    Then response status = 201
    And response includes id, exerciseId, weight, reps, date
    
  Scenario: Reject workout with missing required field
    Given user is authenticated
    And request body: { exerciseId: ex1, weight: 100 } (missing reps)
    When POSTing to /api/workouts
    Then response status = 400
    And response.error contains "reps is required"
    
  Scenario: Reject unauthenticated request
    Given user is NOT authenticated
    When POSTing to /api/workouts
    Then response status = 401
    And response.error = "Unauthorized"
```

**Test Code:**
```typescript
// server/__tests__/api/workouts.test.ts
import { createMocks } from 'node-mocks-http';
import handler from '@/pages/api/workouts/route';

describe('POST /api/workouts', () => {
  it('should create workout with valid data', async () => {
    const { req, res } = createMocks({
      method: 'POST',
      body: {
        exerciseId: 'ex1',
        weight: 100,
        reps: 5
      },
      headers: {
        authorization: 'Bearer valid-token'
      }
    });
    
    await handler(req, res);
    
    expect(res._getStatusCode()).toBe(201);
    const data = JSON.parse(res._getData());
    expect(data).toHaveProperty('id');
    expect(data.weight).toBe(100);
  });
  
  it('should reject missing reps field', async () => {
    const { req, res } = createMocks({
      method: 'POST',
      body: {
        exerciseId: 'ex1',
        weight: 100
        // missing reps
      },
      headers: {
        authorization: 'Bearer valid-token'
      }
    });
    
    await handler(req, res);
    
    expect(res._getStatusCode()).toBe(400);
    const data = JSON.parse(res._getData());
    expect(data.error).toContain('reps');
  });
  
  it('should reject unauthenticated request', async () => {
    const { req, res } = createMocks({
      method: 'POST',
      body: {
        exerciseId: 'ex1',
        weight: 100,
        reps: 5
      }
      // no auth header
    });
    
    await handler(req, res);
    
    expect(res._getStatusCode()).toBe(401);
    const data = JSON.parse(res._getData());
    expect(data.error).toBe('Unauthorized');
  });
});
```

**Область 2: GET /api/workouts (фильтрация, пагинация)**

```gherkin
Feature: Get Workouts Endpoint
  Scenario: Get all workouts for user
    Given user is authenticated
    When GETing /api/workouts
    Then response status = 200
    And response is array of WorkoutLog objects
    
  Scenario: Filter workouts by exercise ID
    Given user is authenticated
    And database has logs: ex1 (3x), ex2 (2x)
    When GETing /api/workouts?exerciseId=ex1
    Then response includes only 3 logs with exerciseId=ex1
    
  Scenario: Filter by date range
    Given user is authenticated
    And logs: 2024-12-01, 2024-12-05, 2024-12-10
    When GETing /api/workouts?from=2024-12-05&to=2024-12-10
    Then response includes logs from 2024-12-05 to 2024-12-10
    
  Scenario: Pagination with limit and offset
    Given user has 150 workout logs
    When GETing /api/workouts?limit=50&offset=0
    Then response includes first 50 logs
    When GETing /api/workouts?limit=50&offset=50
    Then response includes next 50 logs
```

**Test Code:**
```typescript
describe('GET /api/workouts', () => {
  beforeEach(() => {
    // Seed database with test data
    seedDatabase([
      { exerciseId: 'ex1', date: '2024-12-01' },
      { exerciseId: 'ex1', date: '2024-12-05' },
      { exerciseId: 'ex1', date: '2024-12-10' },
      { exerciseId: 'ex2', date: '2024-12-03' },
      { exerciseId: 'ex2', date: '2024-12-08' }
    ]);
  });
  
  it('should filter by exerciseId', async () => {
    const { req, res } = createMocks({
      method: 'GET',
      query: { exerciseId: 'ex1' }
    });
    
    await handler(req, res);
    
    expect(res._getStatusCode()).toBe(200);
    const data = JSON.parse(res._getData());
    expect(data).toHaveLength(3);
    expect(data.every(log => log.exerciseId === 'ex1')).toBe(true);
  });
  
  it('should filter by date range', async () => {
    const { req, res } = createMocks({
      method: 'GET',
      query: {
        from: '2024-12-05',
        to: '2024-12-10'
      }
    });
    
    await handler(req, res);
    
    const data = JSON.parse(res._getData());
    expect(data).toHaveLength(3);
    expect(data.every(log => 
      new Date(log.date) >= new Date('2024-12-05') &&
      new Date(log.date) <= new Date('2024-12-10')
    )).toBe(true);
  });
});
```

**Область 3: GET /api/analytics/progress (разные упражнения и периоды)**

```gherkin
Feature: Progress Analytics Endpoint
  Scenario: Get progress for exercise over month
    Given user is authenticated
    And exerciseId = ex1, logs over December 2024
    When GETing /api/analytics/progress?exerciseId=ex1&from=2024-12-01&to=2024-12-31
    Then response includes:
      - Array of daily aggregates (max, avg, volume)
      - Stats object (personalRecord, maxWeight, avgWeight)
    
  Scenario: Handle exercise with no logs
    Given user is authenticated
    And exerciseId = ex999 has NO logs
    When GETing /api/analytics/progress?exerciseId=ex999
    Then response status = 200
    And response.data is empty array
    And response.stats all values are null/0
```

**Test Code:**
```typescript
describe('GET /api/analytics/progress', () => {
  it('should return progress data with stats', async () => {
    const { req, res } = createMocks({
      method: 'GET',
      query: {
        exerciseId: 'ex1',
        from: '2024-12-01',
        to: '2024-12-31'
      }
    });
    
    await handler(req, res);
    
    expect(res._getStatusCode()).toBe(200);
    const data = JSON.parse(res._getData());
    expect(data).toHaveProperty('data');
    expect(data).toHaveProperty('stats');
    expect(data.stats).toHaveProperty('personalRecord');
    expect(data.stats).toHaveProperty('maxWeight');
  });
  
  it('should return empty data for exercise with no logs', async () => {
    const { req, res } = createMocks({
      method: 'GET',
      query: { exerciseId: 'ex999' }
    });
    
    await handler(req, res);
    
    const data = JSON.parse(res._getData());
    expect(data.data).toHaveLength(0);
    expect(data.stats.personalRecord).toBeNull();
  });
});
```

#### 5.1.3 Database Tests

```gherkin
Feature: Database Integrity
  Scenario: Foreign key constraint on user deletion
    Given user has 10 workout logs
    When deleting the user
    Then all workout logs are cascade-deleted
    
  Scenario: Index performance on large dataset
    Given 100,000 workout logs
    When querying by user_id and date
    Then query completes in < 100ms
```

**Test Code:**
```typescript
describe('Database Integrity', () => {
  it('should cascade delete logs when user deleted', () => {
    const db = Database.getInstance();
    
    // Create user and logs
    const userId = 'test-user-123';
    db.prepare('INSERT INTO users (id, email) VALUES (?, ?)').run(
      userId,
      'test@example.com'
    );
    
    db.prepare(`
      INSERT INTO workout_logs (user_id, exercise_id, weight, reps, date)
      VALUES (?, ?, ?, ?, ?)
    `).run(userId, 'ex1', 100, 5, new Date().toISOString());
    
    // Delete user
    db.prepare('DELETE FROM users WHERE id = ?').run(userId);
    
    // Verify logs are deleted
    const remaining = db.prepare(
      'SELECT COUNT(*) as count FROM workout_logs WHERE user_id = ?'
    ).get(userId);
    
    expect(remaining.count).toBe(0);
  });
});
```

---

### 5.2 Frontend Testing Strategy

#### 5.2.1 Unit Tests (Components & Utilities)

**Область 1: Form Validation**

```gherkin
Feature: Workout Form Validation
  Scenario: Reject form with empty weight
    Given form fields: exercise=ex1, weight="", reps=5
    When attempting submit
    Then validation error "Weight is required"
    
  Scenario: Reject form with non-numeric weight
    Given weight input = "abc"
    When validating
    Then error "Weight must be a number"
    
  Scenario: Accept valid form
    Given all fields valid
    When validating
    Then no errors, form is submittable
```

**Test Code:**
```typescript
// components/__tests__/WorkoutForm.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { WorkoutForm } from '@/components/forms/WorkoutForm';

describe('WorkoutForm Validation', () => {
  it('should reject empty weight', async () => {
    render(<WorkoutForm />);
    
    fireEvent.change(screen.getByLabelText(/exercise/i), {
      target: { value: 'ex1' }
    });
    fireEvent.change(screen.getByLabelText(/weight/i), {
      target: { value: '' }
    });
    fireEvent.click(screen.getByText(/submit/i));
    
    expect(screen.getByText(/weight is required/i)).toBeInTheDocument();
  });
  
  it('should reject non-numeric weight', () => {
    render(<WorkoutForm />);
    
    fireEvent.change(screen.getByLabelText(/weight/i), {
      target: { value: 'abc' }
    });
    fireEvent.click(screen.getByText(/submit/i));
    
    expect(screen.getByText(/must be a number/i)).toBeInTheDocument();
  });
  
  it('should accept valid form', async () => {
    const onSubmit = jest.fn();
    render(<WorkoutForm onSubmit={onSubmit} />);
    
    fireEvent.change(screen.getByLabelText(/exercise/i), {
      target: { value: 'ex1' }
    });
    fireEvent.change(screen.getByLabelText(/weight/i), {
      target: { value: '100' }
    });
    fireEvent.change(screen.getByLabelText(/reps/i), {
      target: { value: '5' }
    });
    fireEvent.click(screen.getByText(/submit/i));
    
    expect(onSubmit).toHaveBeenCalledWith({
      exerciseId: 'ex1',
      weight: 100,
      reps: 5
    });
  });
});
```

**Область 2: Data Formatting Utilities**

```gherkin
Feature: Data Formatting
  Scenario: Format date to DD.MM.YYYY
    Given date = 2024-12-25
    When formatting with locale ru-RU
    Then return "25.12.2024"
    
  Scenario: Format weight with unit
    Given weight = 100.5, unit = "kg"
    When formatting
    Then return "100.5 kg"
```

**Test Code:**
```typescript
import { formatDate, formatWeight } from '@/lib/utils/format';

describe('Data Formatting', () => {
  it('should format date to DD.MM.YYYY', () => {
    const date = new Date('2024-12-25');
    expect(formatDate(date, 'ru-RU')).toBe('25.12.2024');
  });
  
  it('should format weight with unit', () => {
    expect(formatWeight(100.5, 'kg')).toBe('100.5 kg');
  });
});
```

#### 5.2.2 Integration Tests

**Область 1: Добавление тренировки (Form + API + State Update)**

```gherkin
Feature: Add Workout (Full Flow)
  Scenario: Successfully log workout
    Given form is open
    When user fills form with valid data
    And clicks "Add Workout"
    Then API call is made with correct payload
    And optimistic update shows new log
    And sync status shows "Syncing"
    When server responds success
    Then log is marked as synced
    And user sees success notification
    
  Scenario: Handle offline (no internet)
    Given network is offline
    When user adds workout
    Then optimistic update works
    And log is queued locally
    And sync icon shows "Pending"
    When network comes back
    Then queued log is synced to server
```

**Test Code:**
```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { WorkoutForm } from '@/components/forms/WorkoutForm';
import { useAddWorkout } from '@/lib/api/workouts';

describe('Add Workout Integration', () => {
  let queryClient: QueryClient;
  
  beforeEach(() => {
    queryClient = new QueryClient();
    // Mock API
    jest.mock('fetch', () => jest.fn());
  });
  
  it('should successfully add workout', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        json: () => Promise.resolve({ id: 'log-1', weight: 100 })
      })
    );
    
    render(
      <QueryClientProvider client={queryClient}>
        <WorkoutForm />
      </QueryClientProvider>
    );
    
    fireEvent.change(screen.getByLabelText(/weight/i), {
      target: { value: '100' }
    });
    fireEvent.change(screen.getByLabelText(/reps/i), {
      target: { value: '5' }
    });
    fireEvent.click(screen.getByText(/submit/i));
    
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/workouts',
        expect.objectContaining({
          method: 'POST'
        })
      );
    });
    
    expect(screen.getByText(/success/i)).toBeInTheDocument();
  });
});
```

**Область 2: Просмотр графика прогресса**

```gherkin
Feature: Display Progress Chart
  Scenario: Load and render chart
    Given user navigates to Progress page
    When component mounts
    Then API is called to fetch analytics data
    And chart renders with data
    
  Scenario: Filter chart by period
    Given chart is displayed
    When user selects "Last Month"
    Then chart updates with new data
    And X-axis shows dates for last 30 days
```

**Test Code:**
```typescript
describe('ProgressChart Integration', () => {
  it('should load and render chart', async () => {
    jest.mock('@/lib/api/analytics', () => ({
      useAnalytics: () => ({
        data: [
          { date: '2024-12-01', weight: 100 },
          { date: '2024-12-05', weight: 105 },
          { date: '2024-12-10', weight: 110 }
        ],
        isLoading: false
      })
    }));
    
    render(<ProgressChart exerciseId="ex1" />);
    
    await waitFor(() => {
      expect(screen.getByRole('img', { hidden: true })).toBeInTheDocument();
    });
  });
});
```

#### 5.2.3 E2E Tests (Cypress)

```gherkin
Feature: End-to-End Workout Tracking
  Scenario: Complete workout logging flow
    Given user is logged in
    When user opens app
    Then dashboard is visible
    
    When user clicks "New Workout"
    And selects "Squat" exercise
    And enters weight "150 kg"
    And enters "5" reps
    And clicks "Add Set"
    Then new set is added to the list
    
    When user completes workout
    And views progress page
    Then chart shows updated data with 150 kg
```

**Test Code:**
```typescript
// cypress/e2e/workout-logging.cy.ts
describe('Workout Logging E2E', () => {
  beforeEach(() => {
    cy.login('test@example.com', 'password123');
    cy.visit('/dashboard');
  });
  
  it('should complete full workout flow', () => {
    // Open new workout form
    cy.get('[data-testid="new-workout-btn"]').click();
    
    // Select exercise
    cy.get('[data-testid="exercise-select"]').type('Squat');
    cy.get('[data-testid="exercise-option-squat"]').click();
    
    // Enter weight and reps
    cy.get('[data-testid="weight-input"]').type('150');
    cy.get('[data-testid="reps-input"]').type('5');
    
    // Add set
    cy.get('[data-testid="add-set-btn"]').click();
    cy.get('[data-testid="set-list"]').should('contain', '150 kg x 5');
    
    // Complete workout
    cy.get('[data-testid="complete-workout-btn"]').click();
    cy.get('[data-testid="success-toast"]').should('be.visible');
    
    // Verify in progress
    cy.visit('/progress');
    cy.get('[data-testid="exercise-select"]').select('Squat');
    cy.get('[data-testid="chart"]').should('contain', '150');
  });
});
```

---

### 5.3 Test Coverage Matrix

| Component | Unit | Integration | E2E | Coverage Target |
|-----------|------|-------------|-----|-----------------|
| WorkoutService | ✅ | ✅ | - | 90% |
| WorkoutRepository | ✅ | ✅ | - | 85% |
| AnalyticsService | ✅ | ✅ | - | 90% |
| WorkoutForm | ✅ | ✅ | ✅ | 85% |
| ProgressChart | ✅ | ✅ | ✅ | 80% |
| API Endpoints | - | ✅ | ✅ | 95% |
| Database Migrations | ✅ | ✅ | - | 100% |

### 5.4 Test Data & Fixtures

```typescript
// __tests__/fixtures.ts
export const mockExercises = [
  { id: 'ex1', name: 'Squat', muscleGroup: 'legs' },
  { id: 'ex2', name: 'Bench Press', muscleGroup: 'chest' },
  { id: 'ex3', name: 'Deadlift', muscleGroup: 'back' }
];

export const mockWorkoutLogs = [
  { id: 'log1', exerciseId: 'ex1', weight: 150, reps: 5, date: '2024-12-01' },
  { id: 'log2', exerciseId: 'ex1', weight: 155, reps: 3, date: '2024-12-05' },
  { id: 'log3', exerciseId: 'ex2', weight: 100, reps: 8, date: '2024-12-03' }
];

export const seedDatabase = (data: any[]) => {
  // Insert fixtures into test database
};
```

---

## ФАЗА 6: ТЗ ПО РОЛЯМ

### PRODUCT MANAGER

#### 6.1 Product Requirements Document (PRD)

**Название продукта:** Fitness Tracker — Силовые тренировки с аналитикой

**Видение:** Предоставить легкий и быстрый способ логирования силовых тренировок прямо в спортзале, с последующей аналитикой прогресса и интеграцией через API для мобильных приложений.

**Целевая аудитория:**
- Возраст: 18-50 лет
- Опыт: От новичков до опытных спортсменов
- Поведение: Активно занимаются в спортзале (2-5 раз в неделю)
- Tech-savvy: Готовы использовать веб-приложение + мобильные интеграции

**Метрики успеха (OKR):**
1. **Активные пользователи (DAU):** 1,000+ в первый месяц, 5,000+ в третий
2. **Удержание (Retention):** 7-day retention ≥ 40%, 30-day ≥ 20%
3. **Время логирования:** Средний подход логируется за < 30 сек
4. **API usage:** ≥ 500 API calls/день от mobile apps
5. **Satisfaction:** NPS ≥ 50, App Store rating ≥ 4.5

#### User Stories

**Story 1: Логирование тренировки**
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

**Story 2: Просмотр прогресса**
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

**Story 3: Повтор тренировок**
```
As a structured trainer,
I want to save workout templates and repeat them,
So that I follow my program consistently.

Acceptance Criteria:
- [ ] Can create custom template (name, exercises list)
- [ ] Templates show recent exercises first
- [ ] One-click "repeat last workout"
```

**Story 4: API для мобильных приложений**
```
As a mobile app developer,
I want REST API to create/read workout logs,
So that I can build native iOS/Android apps on top of it.

Acceptance Criteria:
- [ ] OAuth2 authentication
- [ ] POST /api/workouts (create)
- [ ] GET /api/workouts (list with filters)
- [ ] GET /api/analytics/progress
- [ ] Rate limit: 1000 req/hour per user
```

**Story 5: Экспорт данных**
```
As a data-conscious user,
I want to export my workout history as CSV/JSON,
So that I can backup or analyze data elsewhere.

Acceptance Criteria:
- [ ] Can export full history or by date range
- [ ] Format: CSV or JSON
- [ ] File downloads in < 5 sec
```

#### MVP vs. Roadmap

**MVP (Phase 1 - Week 1-3):**
- Логирование тренировок (форма)
- График прогресса (последний месяц)
- Просмотр истории
- Базовый REST API
- Docker Compose setup

**Phase 2 (Week 4-6):**
- Шаблоны тренировок
- Более гибкая аналитика (сравнение периодов)
- Экспорт данных (CSV)
- Email отчёты

**Phase 3 (Week 7-10):**
- Push-уведомления и напоминания
- Социум (шеринг прогресса, друзья)
- Body composition tracking
- ML-рекомендации упражнений

**Phase 4 (Future):**
- Мобильное приложение (iOS/Android)
- Wearable integration (Apple Watch, Fitbit)
- Video form analysis (computer vision)
- Marketplace интеграций

---

### ANALYST / DATA SPECIALIST

#### 6.2 Analytics & Reporting Requirements

**Ключевые метрики:**

1. **User Engagement**
   - DAU/MAU (Daily/Monthly Active Users)
   - Session length (средняя длительность)
   - Frequency: workouts per week per user

2. **Workout Metrics**
   - Total workouts logged
   - Distribution by exercise type
   - Average volume per workout (sum of weight * reps * sets)
   - Session duration

3. **Progress Tracking**
   - PR (Personal Record) hits per user
   - Weight progression (avg improvement per 30 days)
   - Exercise popularity (top 10 exercises logged)

4. **API Usage**
   - API calls per endpoint
   - Error rate by endpoint
   - Response time (latency)
   - Mobile app retention vs web

**Events to log:**

```typescript
interface AnalyticsEvent {
  userId: string;
  eventName: string;
  timestamp: Date;
  properties: Record<string, any>;
}

// Example events:
{
  eventName: 'workout_logged',
  properties: {
    exerciseId: 'ex1',
    weight: 100,
    reps: 5,
    setCount: 3,
    totalVolume: 1500
  }
}

{
  eventName: 'progress_viewed',
  properties: {
    exerciseId: 'ex1',
    period: 'month'
  }
}

{
  eventName: 'api_call',
  properties: {
    endpoint: 'POST /api/workouts',
    statusCode: 201,
    responseTime: 150, // ms
    appVersion: '1.0.0'
  }
}

{
  eventName: 'personal_record',
  properties: {
    exerciseId: 'ex1',
    weight: 180,
    previousPR: 175
  }
}
```

**Отчёты:**

1. **Daily Dashboard** (каждое утро):
   - DAU, workouts logged, API calls
   - Error rate

2. **Weekly Report** (пятница):
   - User cohort analysis (by signup date)
   - Retention: 7-day, 14-day, 30-day
   - Top exercises, most active users

3. **Monthly Report** (конец месяца):
   - Revenue (if applicable)
   - Churn rate
   - Feature adoption
   - API growth

---

### UX/UI DESIGNER

#### 6.3 UI Design Specification

**Design System:**
- Color palette (defined earlier)
- Typography scale
- Spacing scale
- Component library

**Key Screens to Design:**

1. **Authentication**
   - Login screen
   - Registration screen
   - Password reset

2. **Main App**
   - Dashboard (tab: Логирование)
   - Workout form (modal)
   - Workout history list
   - Progress page (tab: Прогресс)
   - Progress chart detail
   - Profile page (settings, export, logout)

3. **Responsive Breakpoints**
   - Mobile (< 640px)
   - Tablet (640px - 1024px)
   - Desktop (> 1024px)

**Deliverables:**

- [ ] Wireframes (low-fidelity) — все экраны
- [ ] High-fidelity mockups (Figma) — все экраны с реальными данными
- [ ] Interactions & animations (transitions, form validation feedback)
- [ ] Design tokens (colors, spacing, typography in JSON format)
- [ ] Responsive design specifications
- [ ] Accessibility checklist (contrast, keyboard nav, ARIA labels)
- [ ] Component inventory & usage guide
- [ ] Animation & microinteractions specs

**Figma Components to Create:**
- Button (primary, secondary, outline, disabled, loading)
- Input / Textarea
- Select / Dropdown
- Card
- Modal
- Badge
- Chart (line, bar)
- BottomNav
- Header
- Toast / Notification

---

### SYSTEM ARCHITECT

#### 6.4 Architecture Design Document

**High-Level Architecture Diagram:**

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Pages: Dashboard, Progress, History, Profile         │  │
│  │ Components: WorkoutForm, Chart, Card, etc.           │  │
│  │ State: Zustand (workouts, ui, auth)                  │  │
│  │ Data: React Query (caching, refetch)                 │  │
│  │ Offline: Service Worker + IndexedDB                  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↕ HTTP(S)
┌─────────────────────────────────────────────────────────────┐
│                    Backend (Next.js API)                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ API Routes:                                           │  │
│  │ - /api/auth/* (login, register, refresh)             │  │
│  │ - /api/workouts/* (CRUD)                             │  │
│  │ - /api/exercises/* (search)                          │  │
│  │ - /api/analytics/* (progress, export)                │  │
│  │ - /api/templates/* (CRUD)                            │  │
│  │                                                       │  │
│  │ Layers:                                              │  │
│  │ - Controllers (input validation, auth)               │  │
│  │ - Services (business logic)                          │  │
│  │ - Repositories (data access)                         │  │
│  │ - Middleware (error handling)                        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↕ Prepared Statements
┌─────────────────────────────────────────────────────────────┐
│                    Database (SQLite)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Tables:                                               │  │
│  │ - users                                               │  │
│  │ - exercises                                           │  │
│  │ - workout_logs (main data)                            │  │
│  │ - analytics_aggregates (pre-calculated)               │  │
│  │ - workout_templates                                   │  │
│  │ - user_preferences                                    │  │
│  │                                                       │  │
│  │ Indexes: user_date, user_exercise, exercise_name    │  │
│  │ Constraints: FK, CHECK, UNIQUE                        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

Infrastructure:
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose                           │
│  - Service: web (Next.js, port 3000)                       │
│  - Volume: fitness_data (/app/data/fitness.db)             │
│  - ENV: JWT_SECRET, NODE_ENV, DATABASE_URL                 │
└─────────────────────────────────────────────────────────────┘
```

**Component Interaction Diagram:**

```
┌──────────────┐
│  User/Login  │
└──────┬───────┘
       │ (1) POST /api/auth/login
       ↓
┌──────────────────────┐
│  Auth Controller     │ (2) Validate email/password
└──────┬───────────────┘
       │
       ↓ (3) AuthService
┌──────────────────────┐
│  Auth Service        │ (4) Generate JWT
└──────┬───────────────┘
       │
       ↓ Return JWT
┌──────────────────────┐
│  Client Store (JWT)  │ (5) Save token in localStorage
└──────────────────────┘

┌──────────────┐
│ Workout Form │
└──────┬───────┘
       │ (1) User fills: exercise, weight, reps
       ↓
┌──────────────────────┐
│  Validation (Client) │ (2) Check weight > 0, reps >= 1
└──────┬───────────────┘
       │
       ├─ (3a) Valid: Optimistic update in Zustand
       │
       ↓ (3b) POST /api/workouts (with JWT)
┌──────────────────────┐
│  Workout Controller  │ (4) Verify auth, validate input
└──────┬───────────────┘
       │
       ↓ (5) WorkoutService
┌──────────────────────┐
│  Workout Service     │ (6) Check business rules
└──────┬───────────────┘
       │
       ↓ (7) WorkoutRepository
┌──────────────────────┐
│  Database (SQLite)   │ (8) INSERT INTO workout_logs
└──────┬───────────────┘
       │
       ├─ (9) Trigger: Update analytics_aggregates
       │
       ↓ Return workout_id + data
┌──────────────────────┐
│  Response to Client  │ (10) Update React Query cache
└──────┬───────────────┘
       │
       ↓ (11) Update UI
┌──────────────────────┐
│  Success Toast       │
└──────────────────────┘
```

**Non-Functional Requirements:**

| Requirement | Target | Implementation |
|-------------|--------|-----------------|
| API Response Time | < 200ms (p95) | Indexes, connection pooling, caching |
| Concurrent Users | 10,000+ | Horizontal scaling with load balancer (future) |
| Data Durability | 99.9% | WAL mode, backups |
| Availability | 99.5% | Health checks, graceful shutdown |
| Security | OAuth2, HTTPS, rate limit | JWT, Content Security Policy |
| Scalability | 100k+ users, 10M+ logs | Pagination, aggregates, archival strategy |

**Deployment Architecture (Future):**

```
┌─────────────────────────────────────────────────┐
│          Load Balancer (nginx)                  │
└─────────┬───────────────────────────┬───────────┘
          ↓                           ↓
    ┌─────────────┐          ┌─────────────┐
    │  Web Pod 1  │          │  Web Pod 2  │
    │ (Next.js)   │          │ (Next.js)   │
    └──────┬──────┘          └──────┬──────┘
           │                        │
           └────────────┬───────────┘
                        ↓
                 ┌──────────────┐
                 │ PostgreSQL   │ (Future: migrate from SQLite)
                 │ (Persistent) │
                 └──────────────┘
```

---

### QA / TEST ENGINEER

#### 6.5 Test Strategy Document

**Objective:** Обеспечить качество приложения через систематическое тестирование на всех уровнях (unit, integration, e2e) с фокусом на критичные функции.

**Test Levels & Scope:**

| Level | Scope | Tools | Coverage % | Timeline |
|-------|-------|-------|-----------|----------|
| **Unit** | Services, utilities, components logic | Jest, React Testing Library | 90%+ | First (parallel with dev) |
| **Integration** | API + DB, form + API | Jest (mocks), node-mocks-http | 95%+ | After unit |
| **E2E** | Full user workflows | Cypress | 80%+ | After integration |
| **Performance** | Load time, query time | Lighthouse, k6 | N/A | Pre-launch |
| **Security** | Auth, XSS, SQL injection | Manual + OWASP | Critical | Ongoing |

**Key Test Scenarios:**

**1. Authentication & Authorization**
```
✓ User can register with valid email
✓ User cannot register with duplicate email
✓ User can login with correct credentials
✓ User cannot login with wrong password
✓ JWT token expires after 1 hour
✓ Refresh token extends session
✓ Unauthenticated request to protected endpoint → 401
✓ User cannot access other user's data
```

**2. Workout Logging**
```
✓ User can add workout (all fields required)
✓ Invalid weight → validation error
✓ Invalid reps → validation error
✓ Workout is saved with current timestamp
✓ Offline mode queues workout locally
✓ When online, queued workout syncs automatically
✓ Duplicate detection (same exercise, weight, reps, date)
```

**3. Progress Analytics**
```
✓ Chart loads with data for selected exercise
✓ Max weight calculation is correct
✓ Average weight calculation is correct
✓ PR is correctly identified with date
✓ Period filter (day/week/month) updates chart
✓ Chart is responsive on mobile
✓ No data → empty state message
```

**4. API Contract**
```
✓ POST /api/workouts returns 201 with workout data
✓ GET /api/workouts returns 200 with array
✓ GET /api/workouts?exerciseId=X filters correctly
✓ GET /api/workouts?from=X&to=Y respects date range
✓ Invalid query params → 400
✓ Missing auth header → 401
✓ Rate limit exceeded → 429
```

**5. Database Integrity**
```
✓ Foreign keys enforce referential integrity
✓ Indexes are used in WHERE clauses
✓ Aggregates are updated after new log
✓ Cascade delete works (user → logs)
✓ Concurrent writes don't corrupt data
```

**Test Case Template:**

```
Test Case: TC-001 - Add Workout with Valid Data
Module: Workout Logging
Priority: CRITICAL
Preconditions:
  - User is logged in
  - Browser cache is cleared
  - Network connection is stable

Steps:
  1. Navigate to Dashboard
  2. Click "New Workout"
  3. Select exercise: "Squat"
  4. Enter weight: "150"
  5. Enter reps: "5"
  6. Click "Add Set"
  7. Repeat steps 3-6 for total 3 sets
  8. Click "Complete Workout"

Expected Result:
  - Workout is saved in database
  - UI shows success notification
  - Workout appears in history
  - Progress chart is updated

Actual Result:
  [Test execution result]

Status:
  ☐ PASS ☐ FAIL ☐ BLOCKED

Notes:
  [Any deviations]
```

**Test Execution Plan:**

```
Phase 1: Unit Tests (Week 1-2, ongoing)
  - Run on: Every commit (pre-commit hook)
  - Target: 90% coverage
  - Tools: Jest
  - Time: 5-10 min per commit

Phase 2: Integration Tests (Week 2-3, after unit)
  - Run on: Daily (after main push)
  - Target: 95% coverage
  - Tools: Jest + mocks
  - Time: 30 min

Phase 3: E2E Tests (Week 3-4, before release)
  - Run on: Pre-release, manually
  - Target: 80% critical paths
  - Tools: Cypress
  - Time: 60 min per run

Phase 4: Regression Testing (Ongoing)
  - Run on: Each release
  - Tools: Test suite automation
```

**Defect Severity:**

| Severity | Definition | Example | Fix Timeline |
|----------|-----------|---------|--------------|
| **Critical** | App crashes, data loss, security breach | Login fails, workouts deleted | 4 hours |
| **High** | Core feature broken, wrong calculation | Chart shows wrong max weight | 1 day |
| **Medium** | Feature partially broken, workaround exists | Filter doesn't work but manual refresh does | 3 days |
| **Low** | UI issue, cosmetic problem | Button color slightly off | 1 week |

---

### BACKEND DEVELOPER

#### 6.6 Backend Development Specification

**Your Mission:** Implement backend API with strict adherence to TDD (RED → GREEN → REFACTOR), using pre-designed test cases as your north star.

**Key Endpoints & Implementation Order:**

**Priority 1 (Week 1):**

1. **POST /api/auth/login** — Authenticate user, return JWT
   - Input: { email, password }
   - Output: { token, user: { id, email } }
   - Error handling: 400 (invalid), 401 (wrong password), 500 (server)
   - Test: Already written, make it PASS

2. **POST /api/auth/register** — Create new user
   - Input: { email, password, passwordConfirm }
   - Validation: email format, password strength (min 8 chars)
   - Output: { token, user: { id, email } }
   - Test: Already written

3. **GET /api/exercises** — List exercises (search, filter)
   - Query: ?search=присед&muscleGroup=legs
   - Output: Array of { id, name, muscleGroup, category }
   - Cache: Redis or HTTP cache header
   - Test: Already written

**Priority 2 (Week 2):**

4. **POST /api/workouts** — Create workout log
   - Input: { exerciseId, weight, reps, sets, rpe?, notes? }
   - Validation: weight > 0, reps 1-100, sets 1-10
   - Process: Save to DB, update aggregates
   - Output: { id, exerciseId, weight, reps, date, createdAt }
   - Test: Already written (with offline queue scenario)

5. **GET /api/workouts** — Fetch workout logs
   - Query: ?exerciseId=X&from=2024-12-01&to=2024-12-31&limit=100&offset=0
   - Filtering: by exercise, date range, user
   - Pagination: limit (max 1000), offset
   - Output: { data: [...], total, hasMore }
   - Test: Already written

6. **PATCH /api/workouts/:id** — Update workout log
   - Input: Partial updates (weight, reps, notes)
   - Output: Updated workout object
   - Test: Already written

7. **DELETE /api/workouts/:id** — Delete workout log
   - Process: Delete, update aggregates
   - Output: { success: true }
   - Test: Already written

**Priority 3 (Week 3):**

8. **GET /api/analytics/progress** — Fetch progress data
   - Query: ?exerciseId=X&from=2024-12-01&to=2024-12-31&granularity=day
   - Process: Aggregate from analytics_aggregates table or calculate on-the-fly
   - Output: { data: [...], stats: { maxWeight, avgWeight, pr, workoutCount } }
   - Test: Already written

9. **GET /api/analytics/export** — Export data as CSV/JSON
   - Query: ?format=csv&from=2024-12-01&to=2024-12-31
   - Process: Stream response for large datasets
   - Output: CSV file or JSON array
   - Test: Already written

10. **POST /api/templates** — Create workout template
    - Input: { name, exercises: [...] }
    - Output: { id, name, exercises }
    - Test: Already written

**Development Workflow (TDD):**

```
1. Read Test Case (Already written)
   ├─ Understand inputs, outputs, edge cases
   └─ Run test → RED (fails, as expected)

2. Implement MINIMUM code to make test PASS
   ├─ Don't over-engineer
   ├─ Focus on test requirements only
   └─ Run test → GREEN (passes)

3. REFACTOR code
   ├─ Extract functions, improve clarity
   ├─ Add error handling
   ├─ Make it production-ready
   └─ Ensure test still PASSES

4. Move to next test
   └─ Repeat
```

**Example Implementation:**

```typescript
// Step 1: RED (Test is failing)
// Test expects: weight validation
test('should reject negative weight', async () => {
  await expect(service.createWorkout('user1', { weight: -10, reps: 5 }))
    .rejects.toThrow('Weight must be positive');
});

// Step 2: GREEN (Minimum implementation)
async createWorkout(userId: string, data: WorkoutInput) {
  if (data.weight <= 0) throw new Error('Weight must be positive');
  // ... rest of logic
}

// Step 3: REFACTOR (Production-ready)
async createWorkout(userId: string, data: WorkoutInput) {
  // Validate using Zod schema
  const validated = workoutSchema.parse(data);
  
  // Throw meaningful error
  if (validated.weight <= 0) {
    throw new ValidationError('Weight must be positive', {
      field: 'weight',
      value: validated.weight
    });
  }
  
  // ... rest of logic with error handling
}

// Step 4: All tests PASS ✅
```

**Code Quality Checklist:**

- [ ] All test cases pass
- [ ] Proper error handling (try-catch, custom errors)
- [ ] Input validation (Zod schemas)
- [ ] Database transactions (if multiple tables affected)
- [ ] Logging (for debugging and monitoring)
- [ ] Performance: Database query time < 100ms
- [ ] Security: No SQL injection, input sanitized
- [ ] Comments: Complex logic documented

**Common Pitfalls to Avoid:**

❌ "I'll write tests after implementation" → NO, use tests as guide BEFORE
❌ "This function is too simple to test" → Test it anyway
❌ "Just make it work, refactor later" → Refactor immediately while fresh
❌ "I'll handle this edge case later" → Handle it now, test it

---

### FRONTEND DEVELOPER

#### 6.7 Frontend Development Specification

**Your Mission:** Build responsive, accessible UI components using Next.js + React with TDD. Tests are pre-written, make them PASS.

**Component Development Order:**

**Priority 1 (Week 1):**

1. **WorkoutForm Component** — The core logging form
   - Fields: exercise (autosuggest), weight, reps, sets, rpe (optional), notes
   - Validation: Client-side, instant feedback
   - Behavior: 
     - Prefill weight from last log
     - "Add Set" button appends to list
     - "Complete" submits all sets at once
   - State: Zustand + React Hook Form
   - Tests: Already written (validation, submission, offline)

2. **ExerciseSelect Component** — Exercise dropdown with autosuggest
   - Behavior:
     - Show recent exercises first
     - Autosuggest as user types
     - Group by muscle group
   - API call: GET /api/exercises?search=...
   - Tests: Already written

3. **ProgressChart Component** — Recharts wrapper for progress visualization
   - Data: Array of { date, weight, reps }
   - Features:
     - Line chart with multiple series (max, avg)
     - Tooltip showing values
     - Responsive (mobile to desktop)
   - Tests: Already written

**Priority 2 (Week 2):**

4. **WorkoutCard Component** — Display individual workout in history
   - Props: workoutLog (with exercises array)
   - Display: Date, exercises, duration, PR indicator
   - Actions: Edit, delete (if recent)

5. **HistoryPage** — Workout history list view
   - Filtering: by date range, exercise
   - Pagination: load more or infinite scroll
   - Sorting: date descending
   - Tests: Already written (filter, pagination)

6. **ProgressPage** — Analytics dashboard
   - Components: ExerciseSelect, DateRangeFilter, ProgressChart, StatsDisplay
   - Behavior:
     - Select exercise → chart updates
     - Select period → chart updates
     - Show stats (max, avg, PR)
   - Tests: Already written

7. **ProfilePage** — User settings and logout
   - Settings: Units (kg/lbs), theme, notifications
   - Actions: Export data, logout

**Priority 3 (Week 3):**

8. **Offline Indicator** — Show sync status
   - States: synced ✓, syncing ⟳, error ✗, offline
   - Logic: Based on IndexedDB offline queue

9. **Authentication Pages** — Login and Register
   - Forms with validation
   - Error messages
   - Success redirect

**Development Workflow (TDD):**

```
1. Read Test File
   ├─ Understand expected behavior
   ├─ Note props, state, interactions
   └─ Run test → RED

2. Create Component Skeleton
   ├─ Props interface
   ├─ Initial JSX structure
   └─ Run test → RED (missing functionality)

3. Implement Functionality
   ├─ Add state (useState, Zustand)
   ├─ Add event handlers
   ├─ Add effects (useEffect)
   ├─ Connect to API (useQuery, useMutation)
   └─ Run test → GREEN

4. Style Component
   ├─ Apply design system variables
   ├─ Responsive breakpoints
   ├─ Focus states (accessibility)
   └─ Run test → Still GREEN ✅

5. Refactor
   ├─ Extract sub-components if too large
   ├─ Remove duplication
   ├─ Add comments
   └─ All tests PASS
```

**Example Component Implementation:**

```typescript
// Step 1: Read test to understand requirements
// Test expects: form validation, API call, success notification

// Step 2: Skeleton
interface WorkoutFormProps {
  onSuccess?: () => void;
}

export const WorkoutForm: React.FC<WorkoutFormProps> = ({ onSuccess }) => {
  const [weight, setWeight] = useState('');
  const [reps, setReps] = useState('');
  
  return (
    <form>
      <input value={weight} onChange={e => setWeight(e.target.value)} />
      <input value={reps} onChange={e => setReps(e.target.value)} />
      <button type="submit">Submit</button>
    </form>
  );
};

// Step 3: Implement
export const WorkoutForm: React.FC<WorkoutFormProps> = ({ onSuccess }) => {
  const [weight, setWeight] = useState('');
  const [reps, setReps] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  
  const { mutate, isPending } = useAddWorkout();
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate
    const newErrors: Record<string, string> = {};
    if (!weight) newErrors.weight = 'Required';
    if (isNaN(Number(weight))) newErrors.weight = 'Must be a number';
    if (!reps) newErrors.reps = 'Required';
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    
    setErrors({});
    
    // Submit
    mutate({
      weight: parseFloat(weight),
      reps: parseInt(reps)
    }, {
      onSuccess: () => {
        onSuccess?.();
      }
    });
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input value={weight} onChange={e => setWeight(e.target.value)} />
      {errors.weight && <span className="error">{errors.weight}</span>}
      
      <input value={reps} onChange={e => setReps(e.target.value)} />
      {errors.reps && <span className="error">{errors.reps}</span>}
      
      <button type="submit" disabled={isPending}>
        {isPending ? 'Submitting...' : 'Submit'}
      </button>
    </form>
  );
};

// Step 4: Style
export const WorkoutForm: React.FC<WorkoutFormProps> = ({ onSuccess }) => {
  // ... (same logic)
  
  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <input 
          value={weight}
          onChange={e => setWeight(e.target.value)}
          className="form-input"
          placeholder="Weight (kg)"
          aria-label="Weight"
        />
        {errors.weight && <span className="text-error">{errors.weight}</span>}
      </div>
      
      <div>
        <input 
          value={reps}
          onChange={e => setReps(e.target.value)}
          className="form-input"
          placeholder="Reps"
          aria-label="Reps"
        />
        {errors.reps && <span className="text-error">{errors.reps}</span>}
      </div>
      
      <button 
        type="submit"
        disabled={isPending}
        className="btn btn--primary w-full"
      >
        {isPending ? 'Submitting...' : 'Submit'}
      </button>
    </form>
  );
};

// Step 5: All tests PASS ✅
```

**Code Quality Checklist:**

- [ ] Component is tested (all test cases pass)
- [ ] Props are typed with TypeScript
- [ ] Accessibility: aria-labels, semantic HTML, keyboard nav
- [ ] Responsive: mobile, tablet, desktop
- [ ] Design system: colors, spacing, typography from variables
- [ ] Error states: form errors, API errors, empty states
- [ ] Loading states: spinners, disabled buttons
- [ ] Comments: Complex logic documented

**Common Pitfalls:**

❌ "I'll make it responsive after MVP" → Make it responsive from start (mobile-first)
❌ "This doesn't need a test" → If tests are written, implement against them
❌ "Inline styles" → Use CSS variables and Tailwind classes
❌ "No error handling" → Always show errors to user

---

## ФАЗА 7: RISK ASSESSMENT & MITIGATION

### 7.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| **SQLite concurrency limit** | HIGH | HIGH | Use WAL mode, connection pooling, queue system for writes |
| **Chart rendering slow** | MEDIUM | MEDIUM | Virtual scroll, reduce data points, client-side aggregation |
| **Offline sync conflicts** | MEDIUM | MEDIUM | Last-write-wins, timestamp-based reconciliation, test scenarios |
| **Database size grows rapidly** | MEDIUM | MEDIUM | Implement archival (move old logs), partition strategy |
| **API rate limiting issues** | MEDIUM | LOW | Implement backoff, client-side queue, rate limit headers |
| **Mobile browser compatibility** | LOW | MEDIUM | Test on iOS Safari, Android Chrome, PWA caching |
| **Data export latency** | MEDIUM | LOW | Stream response, background job, cron export |
| **JWT token expiration UX** | MEDIUM | MEDIUM | Auto-refresh with refresh token, transparent to user |

### 7.2 Testing Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| **Tests not matching reality** | HIGH | HIGH | **Write tests AFTER architecture, before code** — this is mandatory |
| **Tests become outdated** | MEDIUM | MEDIUM | Maintain tests as living document, update with code changes |
| **Offline test coverage gaps** | MEDIUM | HIGH | Dedicated offline test suite, use Cypress offline mode |
| **API contract test neglect** | MEDIUM | MEDIUM | OpenAPI spec first, generate client from spec |
| **Database state pollution** | MEDIUM | MEDIUM | Use test fixtures, reset DB between tests, use transactions |

### 7.3 Performance Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| **N+1 queries** | MEDIUM | HIGH | JOIN queries, eager loading, test with many records |
| **Memory leak in React** | LOW | HIGH | Use React DevTools, test for memory leaks during development |
| **Large file export timeout** | MEDIUM | MEDIUM | Stream CSV, pagination, async export + email delivery |
| **Bundle size bloat** | MEDIUM | MEDIUM | Tree-shaking, code splitting, lazy load charts |
| **Unoptimized charts for large data** | MEDIUM | MEDIUM | Limit chart to 6 months, aggregate data points, use canvas-based charts |

### 7.4 Business Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| **Low user adoption** | MEDIUM | HIGH | Focus on UX, fast onboarding, viral features (sharing) |
| **Competitor (Strong, JEFIT) advantage** | HIGH | HIGH | Differentiate: API-first, open source, privacy-focused |
| **Data privacy concerns** | MEDIUM | HIGH | Clear privacy policy, option for self-hosted, SOC2 roadmap |
| **API abuse** | MEDIUM | MEDIUM | Rate limiting, API keys, monitoring, abuse detection |
| **Monetization conflicts** | MEDIUM | MEDIUM | Freemium model clear, no dark patterns, transparent pricing |

---

## ФАЗА 8: IMPLEMENTATION TIMELINE

### Week 1-2: Foundation & Backend Core
- [ ] Setup: Docker, DB schema, migrations
- [ ] Auth API: login, register, refresh token
- [ ] Workout API: POST/GET/DELETE (basic)
- [ ] Unit & integration tests for core endpoints
- [ ] Backend: 100% test coverage for services

### Week 2-3: Frontend Core
- [ ] Next.js setup, routing, layouts
- [ ] Components: WorkoutForm, ExerciseSelect
- [ ] Pages: Dashboard (logging), History
- [ ] State: Zustand setup, queries
- [ ] Tests: Form validation, API integration

### Week 3-4: Analytics & Advanced Features
- [ ] Backend: GET /api/analytics/progress, export
- [ ] Frontend: ProgressPage, charts (Recharts)
- [ ] Offline: Service Worker, IndexedDB queue
- [ ] Tests: E2E scenarios (logging → chart)

### Week 4-5: Polish & Testing
- [ ] Responsive design, accessibility audit
- [ ] Comprehensive E2E tests (Cypress)
- [ ] Performance testing (Lighthouse, k6)
- [ ] Security review (OWASP)
- [ ] Documentation (API, deployment)

### Week 5-6: Launch Preparation & Production
- [ ] Docker Compose for prod, CI/CD
- [ ] Monitoring setup (error tracking, analytics)
- [ ] Launch checklist, go/no-go decision
- [ ] Post-launch: monitoring, bug fixes

---

## ВЫВОДЫ И КЛЮЧЕВЫЕ ТРЕБОВАНИЯ

### ✅ ЧТО ОБЯЗАТЕЛЬНО ВЫПОЛНИТЬ

1. **Architecture First**
   - ✓ Спроектирована полная архитектура (frontend, backend, DB, API)
   - ✓ Определены все endpoint'ы и их поведение
   - ✓ Спроектирована БД схема с индексами

2. **Tests Second (Уже сделано в этом документе)**
   - ✓ Unit test cases для services и utilities
   - ✓ Integration test cases для API endpoints
   - ✓ E2E test scenarios (полные workflows)
   - ✓ Все тест-кейсы написаны ДО разработки кода

3. **Development Third (RED → GREEN → REFACTOR)**
   - ✓ Backend dev: выполняет тест-кейсы один за другим
   - ✓ Frontend dev: выполняет тест-кейсы один за другим
   - ✓ Каждая фичка: сначала RED (тест падает), потом GREEN (проходит), потом REFACTOR

### 🎯 МЕТРИКИ УСПЕХА

- **Покрытие тестами:** Backend 90%+, Frontend 85%+
- **Качество кода:** ESLint без errors, TypeScript strict mode
- **Performance:** API < 200ms (p95), FCP < 2s
- **Accessibility:** WCAG 2.1 AA, 100% keyboard accessible
- **User satisfaction:** First user session < 5 min to first log

### 📋 РАЗДАЧА ПО РОЛЯМ

Каждый developer получает:
1. **Архитектурный дизайн** — что и как строить
2. **Тест-кейсы** — что именно проверяют тесты
3. **Спецификация** — требования, примеры, edge cases
4. **Код-примеры** — как правильно реализовать

**Никаких неясностей. Разработчики знают ТОЧНО, что нужно делать.**

---

**Документ подготовлен как полная спецификация для разработки.**  
**Следующий шаг: Раздача ролям и начало Phase 1 (Week 1).**

