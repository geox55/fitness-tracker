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
│   ├── frontend/                   # React + Vite (UI only)
│   │   ├── src/
│   │   │   ├── app/                # Application entry, routing, providers
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

## Frontend Architecture (React + Vite + FSD)

### FSD Structure

```
packages/frontend/src/
├── app/                            # Application entry, routing, providers
│   ├── app.tsx                     # Main app component with Outlet
│   ├── router.tsx                  # React Router v7 configuration
│   ├── providers.tsx               # QueryClientProvider, ThemeProvider
│   ├── main.tsx                     # Entry point with MSW setup
│   ├── protected-toute.tsx         # Protected route wrapper
│   └── root-error-boundary.tsx     # Error boundary
│
├── features/                       # Business features (FSD)
│   ├── auth/
│   │   ├── login.page.tsx
│   │   ├── register.page.tsx
│   │   ├── model/
│   │   │   ├── use-login.ts
│   │   │   └── use-register.ts
│   │   └── ui/
│   │       ├── auth-layout.tsx
│   │       ├── login-form.tsx
│   │       └── register-form.tsx
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
    ├── api/
    │   ├── instance.ts              # openapi-fetch client
    │   ├── query-client.ts          # TanStack Query client
    │   ├── schema/                  # OpenAPI schema files
    │   │   ├── main.yaml
    │   │   ├── endpoints/
    │   │   │   ├── auth.yaml
    │   │   │   └── workouts.yaml
    │   │   └── generated.ts         # Generated types (run `pnpm api`)
    │   └── mocks/                   # MSW handlers
    │       ├── browser.ts
    │       └── handlers/
    ├── ui/kit/                      # shadcn/ui components
    │   ├── button.tsx
    │   ├── input.tsx
    │   ├── form.tsx
    │   └── ...
    ├── model/                       # Global state (create-gstore)
    │   ├── session.ts               # Auth session management
    │   ├── routes.ts                # Route constants
    │   └── config.ts                # App config
    └── lib/                         # Utils
        └── css.ts                   # Tailwind utilities
```

### Routing: React Router v7

Роутинг настроен через React Router v7 с поддержкой lazy loading и protected routes.

```typescript
// app/router.tsx
import { createBrowserRouter, redirect } from 'react-router';
import { ROUTES } from '@/shared/model/routes';

export const router = createBrowserRouter([
  {
    element: (
      <Providers>
        <App />
      </Providers>
    ),
    ErrorBoundary: RootErrorBoundary,
    children: [
      {
        element: <ProtectedRoute />,
        children: [
          {
            path: ROUTES.WORKOUTS,
            lazy: () => import('@/features/workouts/workouts.page'),
          },
        ],
      },
      {
        path: ROUTES.LOGIN,
        lazy: () => import('@/features/auth/login.page'),
      },
    ],
  },
]);
```

**Protected Routes:**
```typescript
// app/protected-toute.tsx
import { Navigate, Outlet } from 'react-router';
import { useSession } from '@/shared/model/session';

export function ProtectedRoute() {
  const { session } = useSession();
  
  if (!session) {
    return <Navigate to={ROUTES.LOGIN} replace />;
  }
  
  return <Outlet />;
}
```

### State Management: create-gstore + TanStack Query

**Глобальное состояние (create-gstore):**
Используется для сессии пользователя и конфигурации приложения.

```typescript
// shared/model/session.ts
import { createGStore } from 'create-gstore';
import { jwtDecode } from 'jwt-decode';

export const useSession = createGStore(() => {
  const [token, setToken] = useState(() => localStorage.getItem('token'));

  const login = (token: string) => {
    localStorage.setItem('token', token);
    setToken(token);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
  };

  const session = token ? jwtDecode<Session>(token) : null;

  return { login, logout, session };
});
```

**Серверное состояние (TanStack Query):**
Для данных с сервера используется TanStack Query v5.

### Data Fetching: OpenAPI + TanStack Query

API клиент построен на основе **openapi-fetch** и **openapi-react-query** для автоматической типизации запросов и ответов.

**OpenAPI Schema:**
```yaml
# shared/api/schema/main.yaml
openapi: 3.0.0
paths:
  /api/workouts:
    post:
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                exerciseId: { type: string }
                weight: { type: number }
                reps: { type: number }
```

**Генерация типов:**
```bash
# Генерация TypeScript типов из OpenAPI схемы
pnpm --filter front api
# Создает shared/api/schema/generated.ts
```

**API Client:**
```typescript
// shared/api/instance.ts
import createFetchClient from 'openapi-fetch';
import createClient from 'openapi-react-query';
import type { paths } from './schema';

export const fetchClient = createFetchClient<paths>({
  baseUrl: CONFIG.API_BASE_URL,
});

export const rqClient = createClient(fetchClient);

// Автоматическое добавление JWT токена
fetchClient.use({
  async onRequest({ request }) {
    const token = await useSession.getState().refreshToken();
    if (token) {
      request.headers.set('Authorization', `Bearer ${token}`);
    }
  },
});
```

**Использование в компонентах:**
```typescript
// features/workout-logging/model/useWorkoutForm.ts
import { useMutation } from '@tanstack/react-query';
import { rqClient } from '@/shared/api/instance';
import type { paths } from '@/shared/api/schema';

type CreateWorkoutRequest = paths['/api/workouts']['post']['requestBody']['content']['application/json'];

export function useAddWorkout() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: CreateWorkoutRequest) => {
      const { data: result, error } = await rqClient.POST('/api/workouts', {
        body: data,
      });
      
      if (error) throw new Error(error.message);
      return result;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workouts'] });
    },
  });
}
```

**Mock Service Worker (MSW):**
В development режиме используется MSW для моков API.

```typescript
// shared/api/mocks/browser.ts
import { setupWorker } from 'msw/browser';
import { authHandlers } from './handlers/auth';
import { workoutHandlers } from './handlers/workouts';

export const worker = setupWorker(...authHandlers, ...workoutHandlers);
```

```typescript
// app/main.tsx
async function enableMocking() {
  if (import.meta.env.MODE === 'production') {
    return;
  }
  
  const { worker } = await import('@/shared/api/mocks/browser');
  return worker.start();
}

enableMocking().then(() => {
  createRoot(root).render(/* ... */);
});
```

### UI Components: shadcn/ui + Tailwind CSS v4

UI компоненты в `shared/ui/kit` построены на основе **shadcn/ui** — коллекции переиспользуемых компонентов, скопированных в проект. Используется **Tailwind CSS v4** через `@tailwindcss/vite`.

```typescript
// shared/ui/kit/button.tsx
import { Button as ShadcnButton } from '@/components/ui/button';
import { cn } from '@/shared/lib/css';

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
# Выбрать: Vite, TypeScript, New York style
npx shadcn-ui@latest add button input card form label
```

**Конфигурация (components.json):**
```json
{
  "aliases": {
    "components": "@/shared/ui",
    "utils": "@/shared/lib/css",
    "ui": "@/shared/ui/kit"
  },
  "tailwind": {
    "css": "src/app/main.css"
  }
}
```

**Структура компонентов:**
- Базовые компоненты (Button, Input, Form) — из shadcn/ui в `shared/ui/kit/`
- Кастомные компоненты (WorkoutForm, ProgressChart) — в `features/*/ui/`
- Все компоненты используют Tailwind CSS v4
- Доступны через `@/shared/ui/kit/*`

**Формы: React Hook Form + Zod:**
```typescript
// features/auth/ui/login-form.tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import z from 'zod';

const loginSchema = z.object({
  email: z.string().email('Неверный email'),
  password: z.string().min(6, 'Пароль должен быть не менее 6 символов'),
});

export function LoginForm() {
  const form = useForm({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', password: '' },
  });

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)}>
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input {...field} type="email" />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </form>
    </Form>
  );
}
```

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
      - VITE_API_URL=http://backend:4000
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

