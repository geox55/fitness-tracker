# FRONTEND DEVELOPER SPECIFICATION

## Mission

Build responsive, accessible UI components using **React + Vite + FSD** with TDD approach. Tests are pre-written — make them PASS.

---

## Development Workflow

```
1. Read Test File
   ├─ Understand expected behavior
   ├─ Note props, state, interactions
   └─ Run test → RED

2. Create Component Skeleton
   ├─ Props interface
   └─ Initial JSX structure

3. Implement Functionality
   ├─ Add state (useState, Zustand)
   ├─ Add event handlers
   ├─ Connect to API (useQuery, useMutation)
   └─ Run test → GREEN

4. Style Component
   ├─ Apply design system variables
   ├─ Responsive breakpoints
   └─ Focus states (accessibility)

5. Refactor
   ├─ Extract sub-components if large
   └─ All tests PASS ✅
```

---

## Component Priority

### Priority 1 (Week 1)

#### WorkoutForm

Core logging form component.

```typescript
interface WorkoutFormProps {
  onSuccess?: () => void;
  defaultExerciseId?: string;
}

// Features:
// - Exercise autosuggest
// - Prefill weight from last log
// - Client-side validation
// - "Add Set" appends to list
// - Offline support (queue)
```

**Test Cases:**
- Empty weight → error
- Non-numeric weight → error
- Valid data → API call
- API error → show error
- Offline → queue locally

#### ExerciseSelect

```typescript
interface ExerciseSelectProps {
  value?: string;
  onChange: (exerciseId: string) => void;
  error?: string;
}

// Features:
// - Autosuggest as user types
// - Recent exercises first
// - Group by muscle group
```

#### ProgressChart

```typescript
interface ProgressChartProps {
  exerciseId: string;
  period: 'week' | 'month' | '3months' | 'year';
}

// Features:
// - Line chart (Recharts)
// - Tooltip with values
// - Responsive width
// - Loading state
```

### Priority 2 (Week 2)

#### WorkoutCard

```typescript
interface WorkoutCardProps {
  workout: WorkoutLog;
  onEdit?: () => void;
  onDelete?: () => void;
}

// Display:
// - Date
// - Exercises list
// - Duration
// - PR indicator
```

#### HistoryPage

```typescript
// Features:
// - Filter by date range
// - Filter by exercise
// - Infinite scroll or pagination
// - Empty state
```

#### ProgressPage

```typescript
// Components used:
// - ExerciseSelect
// - DateRangeFilter
// - ProgressChart
// - StatsDisplay (max, avg, PR)
```

### Priority 3 (Week 3)

#### OfflineIndicator

```typescript
// States:
// - synced ✓
// - syncing ⟳
// - error ✗
// - offline

// Based on IndexedDB queue status
```

#### Auth Pages

```typescript
// LoginPage
// - Email/password form
// - Validation
// - Error messages
// - Success redirect

// RegisterPage
// - Email/password/confirm form
// - Password strength indicator
```

---

## Code Patterns

### Feature Component

```typescript
// packages/frontend/src/features/workout-logging/ui/WorkoutForm.tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import z from 'zod';

import { Button } from '@/shared/ui/kit/button';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/shared/ui/kit/form';
import { Input } from '@/shared/ui/kit/input';
import { Spinner } from '@/shared/ui/kit/spinner';

import { useAddWorkout } from '../model/useWorkoutForm';
import { ExerciseSelect } from './ExerciseSelect';

const workoutSchema = z.object({
  exerciseId: z.string().min(1, 'Выберите упражнение'),
  weight: z.number().positive('Вес должен быть положительным'),
  reps: z.number().int().min(1).max(100, 'Повторения должны быть от 1 до 100'),
});

interface WorkoutFormProps {
  onSuccess?: () => void;
}

export function WorkoutForm({ onSuccess }: WorkoutFormProps) {
  const form = useForm({
    resolver: zodResolver(workoutSchema),
    defaultValues: {
      exerciseId: '',
      weight: 0,
      reps: 0,
    },
  });

  const { mutate, isPending, errorMessage } = useAddWorkout();

  const onSubmit = form.handleSubmit((data) => {
    mutate(data, {
      onSuccess: () => {
        form.reset();
        onSuccess?.();
      },
    });
  });

  return (
    <Form {...form}>
      <form onSubmit={onSubmit} className="space-y-4">
        <FormField
          control={form.control}
          name="exerciseId"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Упражнение</FormLabel>
              <FormControl>
                <ExerciseSelect
                  value={field.value}
                  onChange={field.onChange}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="weight"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Вес (кг)</FormLabel>
              <FormControl>
                <Input
                  {...field}
                  type="number"
                  placeholder="100"
                  disabled={isPending}
                  onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="reps"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Повторения</FormLabel>
              <FormControl>
                <Input
                  {...field}
                  type="number"
                  placeholder="5"
                  disabled={isPending}
                  onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {errorMessage && (
          <p className="text-destructive text-sm">{errorMessage}</p>
        )}

        <Button type="submit" disabled={isPending} className="w-full">
          {isPending && <Spinner />}
          Добавить подход
        </Button>
      </form>
    </Form>
  );
}
```

### Model Hook

```typescript
// packages/frontend/src/features/workout-logging/model/useWorkoutForm.ts
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { rqClient } from '@/shared/api/instance';
import type { paths } from '@/shared/api/schema';

type CreateWorkoutRequest = paths['/api/workouts']['post']['requestBody']['content']['application/json'];
type WorkoutResponse = paths['/api/workouts']['post']['responses']['201']['content']['application/json'];

export function useAddWorkout() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: CreateWorkoutRequest) => {
      const { data: result, error } = await rqClient.POST('/api/workouts', {
        body: data,
      });

      if (error) {
        throw new Error(error.message || 'Failed to create workout');
      }

      return result as WorkoutResponse;
    },
    onSuccess: () => {
      // Invalidate and refetch workouts list
      queryClient.invalidateQueries({ queryKey: ['workouts'] });
    },
  });
}
```

**Использование OpenAPI типов:**
Типы автоматически генерируются из OpenAPI схемы. После изменения схемы запустите:
```bash
pnpm --filter front api
```

Это создаст типизированные интерфейсы в `shared/api/schema/generated.ts`, которые можно использовать для типизации запросов и ответов.

### Shared UI Component

Компоненты из shadcn/ui находятся в `shared/ui/kit/`. Они уже настроены и готовы к использованию.

```typescript
// packages/frontend/src/shared/ui/kit/input.tsx
// Это файл из shadcn/ui, уже настроен в проекте
import * as React from 'react';
import { cn } from '@/shared/lib/css';

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);
Input.displayName = 'Input';

export { Input };
```

**Использование в формах:**
Для форм используйте компоненты из `@/shared/ui/kit/form` вместе с React Hook Form:

```typescript
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/shared/ui/kit/form';
import { Input } from '@/shared/ui/kit/input';

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
```

---

## Working with OpenAPI Schema

### Generating Types

```bash
# Generate TypeScript types from OpenAPI schema
pnpm --filter front api

# This creates src/shared/api/schema/generated.ts
# Run this after updating OpenAPI schema files
```

### Using Generated Types

```typescript
import type { paths } from '@/shared/api/schema';

// Request type
type CreateWorkoutRequest = paths['/api/workouts']['post']['requestBody']['content']['application/json'];

// Response type
type WorkoutResponse = paths['/api/workouts']['post']['responses']['201']['content']['application/json'];

// Path parameters
type WorkoutParams = paths['/api/workouts/{id}']['get']['parameters']['path'];
// { id: string }
```

### Updating OpenAPI Schema

```yaml
# shared/api/schema/endpoints/workouts.yaml
paths:
  /api/workouts:
    post:
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required: [exerciseId, weight, reps]
              properties:
                exerciseId:
                  type: string
                  format: uuid
                weight:
                  type: number
                  minimum: 0
                reps:
                  type: integer
                  minimum: 1
                  maximum: 100
      responses:
        '201':
          content:
            application/json:
              schema:
                $ref: '../shared/responses.yaml#/Workout'
```

---

## Mock Service Worker (MSW)

MSW автоматически включается в development режиме для моков API.

### Creating Handlers

```typescript
// shared/api/mocks/handlers/workouts.ts
import { http, HttpResponse } from 'msw';

export const workoutHandlers = [
  http.post('/api/workouts', async ({ request }) => {
    const body = await request.json();
    
    return HttpResponse.json({
      id: 'workout-1',
      ...body,
      createdAt: new Date().toISOString(),
    }, { status: 201 });
  }),

  http.get('/api/workouts', () => {
    return HttpResponse.json({
      data: [
        { id: '1', exerciseId: 'ex1', weight: 100, reps: 5 },
      ],
    });
  }),
];
```

### Registering Handlers

```typescript
// shared/api/mocks/browser.ts
import { setupWorker } from 'msw/browser';
import { workoutHandlers } from './handlers/workouts';
import { authHandlers } from './handlers/auth';

export const worker = setupWorker(...workoutHandlers, ...authHandlers);
```

---

## React Router v7

### Creating Routes

```typescript
// app/router.tsx
import { createBrowserRouter } from 'react-router';
import { ROUTES } from '@/shared/model/routes';

export const router = createBrowserRouter([
  {
    element: (
      <Providers>
        <App />
      </Providers>
    ),
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

### Route Constants

```typescript
// shared/model/routes.ts
export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  WORKOUTS: '/workouts',
  WORKOUT: '/workouts/:workoutId',
} as const;
```

### Navigation

```typescript
import { useNavigate } from 'react-router';
import { ROUTES } from '@/shared/model/routes';

function MyComponent() {
  const navigate = useNavigate();
  
  const handleClick = () => {
    navigate(ROUTES.WORKOUTS);
  };
  
  return <button onClick={handleClick}>Go to Workouts</button>;
}
```

---

## Testing

### Component Test

```typescript
// packages/frontend/tests/features/workout-logging/WorkoutForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { WorkoutForm } from '@/features/workout-logging';

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } }
  });
  
  return ({ children }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('WorkoutForm', () => {
  it('should show error for empty exercise', async () => {
    render(<WorkoutForm />, { wrapper: createWrapper() });
    
    fireEvent.click(screen.getByText(/добавить/i));
    
    expect(await screen.findByText(/выберите упражнение/i)).toBeInTheDocument();
  });
  
  it('should show error for invalid weight', async () => {
    render(<WorkoutForm />, { wrapper: createWrapper() });
    
    // Fill exercise
    const exerciseSelect = screen.getByLabelText(/упражнение/i);
    fireEvent.change(exerciseSelect, { target: { value: 'ex1' } });
    
    // Fill invalid weight
    const weightInput = screen.getByLabelText(/вес/i);
    fireEvent.change(weightInput, { target: { value: '-10' } });
    
    fireEvent.click(screen.getByText(/добавить/i));
    
    expect(await screen.findByText(/вес должен быть положительным/i)).toBeInTheDocument();
  });
  
  it('should submit valid form', async () => {
    const onSuccess = vi.fn();
    
    render(<WorkoutForm onSuccess={onSuccess} />, { wrapper: createWrapper() });
    
    // Fill form using React Hook Form
    const exerciseSelect = screen.getByLabelText(/упражнение/i);
    fireEvent.change(exerciseSelect, { target: { value: 'ex1' } });
    
    const weightInput = screen.getByLabelText(/вес/i);
    fireEvent.change(weightInput, { target: { value: '100' } });
    
    const repsInput = screen.getByLabelText(/повторения/i);
    fireEvent.change(repsInput, { target: { value: '5' } });
    
    fireEvent.click(screen.getByText(/добавить/i));
    
    await waitFor(() => {
      expect(onSuccess).toHaveBeenCalled();
    });
  });
});
```

---

## Styling Guidelines

### Use Design System Variables

```css
/* ✅ Good */
.button {
  background: var(--color-primary);
  border-radius: var(--radius-md);
  padding: var(--space-sm) var(--space-md);
}

/* ❌ Bad */
.button {
  background: #218081;
  border-radius: 8px;
  padding: 8px 16px;
}
```

### Responsive First (Tailwind CSS)

```tsx
// ✅ Good - Mobile first with Tailwind
<div className="p-4 sm:p-6 lg:p-8">
  <h1 className="text-lg sm:text-xl lg:text-2xl">Title</h1>
</div>

// ❌ Bad - Fixed values
<div style={{ padding: '16px' }}>
  <h1 style={{ fontSize: '20px' }}>Title</h1>
</div>
```

### Using Tailwind CSS v4

```tsx
// Tailwind CSS v4 is configured via @tailwindcss/vite
// Use utility classes directly:
<Button className="bg-primary text-white hover:bg-primary/90">
  Click me
</Button>

// Custom styles in main.css:
@theme {
  --color-primary: #218081;
  --radius-md: 0.5rem;
}
```

---

## Code Quality Checklist

- [ ] Component is tested
- [ ] Props are typed with TypeScript
- [ ] Accessibility: aria-labels, semantic HTML
- [ ] Responsive: mobile, tablet, desktop
- [ ] Design system: colors, spacing from variables
- [ ] Error states: form errors, API errors
- [ ] Loading states: spinners, disabled buttons
- [ ] Comments for complex logic

---

## Common Pitfalls

❌ "I'll make it responsive after MVP"  
✅ Mobile-first from start

❌ "Inline styles are fine"  
✅ Use CSS variables and Tailwind

❌ "No error handling needed"  
✅ Always show errors to user

❌ "Testing is optional"  
✅ If tests are written, implement against them

