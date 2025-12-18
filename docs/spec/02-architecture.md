# ARCHITECTURE SPECIFICATION

## Монорепозиторий (Monorepo Structure)

Проект организован как монорепозиторий с использованием **pnpm workspaces**.

```
fitness-tracker/
├── packages/
│   ├── backend/                    # Fastify REST API
│   │   ├── src/
│   │   │   ├── api/                # Routes/Controllers
│   │   │   │   ├── auth/
│   │   │   │   ├── workouts/
│   │   │   │   ├── exercises/
│   │   │   │   ├── analytics/
│   │   │   │   └── templates/
│   │   │   ├── services/           # Business logic
│   │   │   ├── repositories/       # Data access
│   │   │   ├── db/                 # SQLite, migrations
│   │   │   ├── middleware/         # Auth, validation, errors
│   │   │   └── index.ts            # Entry point
│   │   ├── tests/
│   │   └── package.json
│   │
│   ├── frontend/                   # Next.js (UI only)
│   │   ├── src/
│   │   │   ├── app/                # Next.js App Router
│   │   │   ├── features/           # FSD features
│   │   │   ├── shared/             # FSD shared
│   │   │   └── styles/
│   │   ├── tests/
│   │   └── package.json
│   │
│   └── shared/                     # Shared types, schemas
│       ├── src/
│       │   ├── types/
│       │   ├── constants/
│       │   ├── utils/
│       │   └── schemas/            # Zod schemas
│       └── package.json
│
├── infra/                          # Docker, nginx
│   ├── docker/
│   └── docker-compose.yml
│
├── e2e/                            # Cypress/Playwright
├── pnpm-workspace.yaml
└── package.json
```

---

## Backend Architecture (Fastify)

### API Layer Structure

```
packages/backend/src/api/
├── auth/
│   ├── routes.ts       # POST /api/auth/login, register, refresh
│   └── controller.ts
├── workouts/
│   ├── routes.ts       # CRUD /api/workouts
│   └── controller.ts
├── exercises/
│   ├── routes.ts       # GET /api/exercises
│   └── controller.ts
├── analytics/
│   ├── routes.ts       # GET /api/analytics/*
│   └── controller.ts
└── health.ts           # GET /api/health
```

### Layered Architecture Pattern

```
Controller → Service → Repository → Database
     ↓           ↓           ↓
  Validation  Business    SQL Queries
              Logic
```

### Fastify App Setup

```typescript
// packages/backend/src/index.ts
import Fastify from 'fastify';
import cors from '@fastify/cors';

const app = Fastify({ logger: true });

// CORS
await app.register(cors, {
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true
});

// Routes
await app.register(authRoutes, { prefix: '/api/auth' });
await app.register(workoutRoutes, { prefix: '/api/workouts' });
await app.register(exerciseRoutes, { prefix: '/api/exercises' });
await app.register(analyticsRoutes, { prefix: '/api/analytics' });

app.get('/api/health', async (request, reply) => {
  return { status: 'ok' };
});

// Error handling
app.setErrorHandler(errorHandler);

const PORT = process.env.PORT || 4000;
await app.listen({ port: Number(PORT), host: '0.0.0.0' });
```

---

## Frontend Architecture (Next.js + FSD)

### FSD Structure

```
packages/frontend/src/
├── app/                            # Next.js App Router
│   ├── layout.tsx
│   ├── page.tsx
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   └── (protected)/
│       ├── dashboard/page.tsx
│       ├── progress/page.tsx
│       ├── history/page.tsx
│       └── layout.tsx
│
├── features/                       # Business features
│   ├── workout-logging/
│   │   ├── ui/
│   │   │   ├── WorkoutForm.tsx
│   │   │   └── SetList.tsx
│   │   ├── model/
│   │   │   └── useWorkoutForm.ts
│   │   └── index.ts
│   ├── progress-analytics/
│   └── workout-history/
│
└── shared/                         # Reusable
    ├── api/                        # API client
    ├── ui/                         # UI components (shadcn/ui based)
    ├── lib/                        # Utils
    └── model/                      # Zustand stores
```

### State Management: Zustand

```typescript
// shared/model/workouts.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface WorkoutStore {
  logs: WorkoutLog[];
  pendingLogs: WorkoutLog[]; // Offline queue
  addLog: (log: WorkoutLog) => void;
  syncPending: () => Promise<void>;
}

export const useWorkoutStore = create<WorkoutStore>()(
  persist(
    (set) => ({
      logs: [],
      pendingLogs: [],
      addLog: (log) => set((state) => ({
        logs: [log, ...state.logs],
        pendingLogs: [log, ...state.pendingLogs]
      })),
      syncPending: async () => { /* sync logic */ }
    }),
    { name: 'workout-store' }
  )
);
```

### Data Fetching: TanStack Query

```typescript
// shared/api/workouts.ts
import { useQuery, useMutation } from '@tanstack/react-query';

export const useWorkouts = (filters?: WorkoutFilters) => {
  return useQuery({
    queryKey: ['workouts', filters],
    queryFn: () => apiClient.get('/api/workouts', filters),
    staleTime: 1000 * 60 * 5, // 5 min
  });
};

export const useAddWorkout = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (log: WorkoutInput) => apiClient.post('/api/workouts', log),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['workouts'] })
  });
};
```

### UI Components: shadcn/ui

UI компоненты в `shared/ui` построены на основе **shadcn/ui** — коллекции переиспользуемых компонентов, скопированных в проект.

```typescript
// shared/ui/Button/Button.tsx
import { Button as ShadcnButton } from '@/components/ui/button';
import { cn } from '@/shared/lib/utils';

export const Button = ({ className, variant, ...props }) => {
  return (
    <ShadcnButton
      className={cn('custom-styles', className)}
      variant={variant}
      {...props}
    />
  );
};
```

**Установка shadcn/ui:**
```bash
# В packages/frontend
npx shadcn-ui@latest init
npx shadcn-ui@latest add button input card
```

**Структура компонентов:**
- Базовые компоненты (Button, Input, Card) — из shadcn/ui
- Кастомные компоненты (WorkoutForm, ProgressChart) — обёртки над shadcn
- Все компоненты доступны через `@/shared/ui`

---

## Database Architecture (SQLite)

### Schema

```sql
-- Users
CREATE TABLE users (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Exercises master data
CREATE TABLE exercises (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  muscle_group TEXT NOT NULL,
  category TEXT
);
CREATE INDEX idx_exercises_name ON exercises(name);

-- Workout logs (main data)
CREATE TABLE workout_logs (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  exercise_id TEXT NOT NULL,
  weight DECIMAL(10, 2) NOT NULL,
  reps INTEGER NOT NULL CHECK (reps > 0),
  sets INTEGER DEFAULT 1,
  rpe DECIMAL(3, 1),
  notes TEXT,
  date DATETIME NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (exercise_id) REFERENCES exercises(id)
);
CREATE INDEX idx_workout_logs_user_date ON workout_logs(user_id, date DESC);
CREATE INDEX idx_workout_logs_user_exercise ON workout_logs(user_id, exercise_id);

-- Pre-calculated analytics
CREATE TABLE analytics_aggregates (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  exercise_id TEXT NOT NULL,
  period_date DATE NOT NULL,
  max_weight DECIMAL(10, 2),
  avg_weight DECIMAL(10, 2),
  total_volume DECIMAL(15, 2),
  personal_record DECIMAL(10, 2),
  UNIQUE (user_id, exercise_id, period_date)
);

-- Workout templates
CREATE TABLE workout_templates (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  name TEXT NOT NULL,
  exercises_json TEXT NOT NULL
);
```

### Database Connection

```typescript
// packages/backend/src/db/database.ts
import Database from 'better-sqlite3';

export class DatabaseManager {
  private static instance: Database.Database;
  
  static getInstance(): Database.Database {
    if (!DatabaseManager.instance) {
      DatabaseManager.instance = new Database(process.env.DATABASE_PATH);
      DatabaseManager.instance.pragma('journal_mode = WAL');
      DatabaseManager.instance.pragma('foreign_keys = ON');
    }
    return DatabaseManager.instance;
  }
}
```

---

## Shared Package

### Types

```typescript
// packages/shared/src/types/workout.ts
export interface WorkoutLog {
  id: string;
  userId: string;
  exerciseId: string;
  weight: number;
  reps: number;
  sets: number;
  rpe?: number;
  date: string;
}

export interface WorkoutInput {
  exerciseId: string;
  weight: number;
  reps: number;
  sets?: number;
  rpe?: number;
  notes?: string;
}

export interface WorkoutFilters {
  exerciseId?: string;
  from?: string;
  to?: string;
  limit?: number;
  offset?: number;
}
```

### Zod Schemas

```typescript
// packages/shared/src/schemas/workout.schema.ts
import { z } from 'zod';

export const workoutSchema = z.object({
  exerciseId: z.string().uuid(),
  weight: z.number().positive(),
  reps: z.number().int().min(1).max(100),
  sets: z.number().int().min(1).max(10).optional().default(1),
  rpe: z.number().min(1).max(10).optional(),
  notes: z.string().optional(),
});
```

---

## Infrastructure (Docker)

### docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: infra/docker/backend.Dockerfile
    ports:
      - "4000:4000"
    environment:
      - DATABASE_PATH=/data/fitness.db
      - JWT_SECRET=${JWT_SECRET}
    volumes:
      - fitness_data:/data

  frontend:
    build:
      context: .
      dockerfile: infra/docker/frontend.Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:4000
    depends_on:
      - backend

volumes:
  fitness_data:
```

---

## Non-Functional Requirements

| Requirement | Target | Implementation |
|-------------|--------|----------------|
| API Response Time | < 200ms (p95) | Indexes, caching |
| Concurrent Users | 10,000+ | Horizontal scaling |
| Data Durability | 99.9% | WAL mode, backups |
| Security | OAuth2, HTTPS | JWT, CSP |

