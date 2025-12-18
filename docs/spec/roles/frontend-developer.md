# FRONTEND DEVELOPER SPECIFICATION

## Mission

Build responsive, accessible UI components using **Next.js + FSD** with TDD approach. Tests are pre-written — make them PASS.

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
'use client';

import { useState } from 'react';
import { useAddWorkout } from '../model/useWorkoutForm';
import { ExerciseSelect } from './ExerciseSelect';
import { Button, Input } from '@/shared/ui';

interface WorkoutFormProps {
  onSuccess?: () => void;
}

export const WorkoutForm = ({ onSuccess }: WorkoutFormProps) => {
  const [exerciseId, setExerciseId] = useState('');
  const [weight, setWeight] = useState('');
  const [reps, setReps] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  
  const { mutate, isPending } = useAddWorkout();
  
  const validate = () => {
    const newErrors: Record<string, string> = {};
    
    if (!exerciseId) newErrors.exerciseId = 'Выберите упражнение';
    if (!weight) newErrors.weight = 'Введите вес';
    else if (isNaN(Number(weight))) newErrors.weight = 'Должно быть число';
    if (!reps) newErrors.reps = 'Введите повторения';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validate()) return;
    
    mutate({
      exerciseId,
      weight: parseFloat(weight),
      reps: parseInt(reps)
    }, {
      onSuccess: () => {
        setWeight('');
        setReps('');
        onSuccess?.();
      }
    });
  };
  
  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <ExerciseSelect
        value={exerciseId}
        onChange={setExerciseId}
        error={errors.exerciseId}
      />
      
      <Input
        label="Вес (кг)"
        type="number"
        value={weight}
        onChange={(e) => setWeight(e.target.value)}
        error={errors.weight}
        aria-label="Weight"
      />
      
      <Input
        label="Повторения"
        type="number"
        value={reps}
        onChange={(e) => setReps(e.target.value)}
        error={errors.reps}
        aria-label="Reps"
      />
      
      <Button
        type="submit"
        variant="primary"
        loading={isPending}
        className="w-full"
      >
        Добавить подход
      </Button>
    </form>
  );
};
```

### Model Hook

```typescript
// packages/frontend/src/features/workout-logging/model/useWorkoutForm.ts
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/shared/api';
import type { WorkoutInput } from '@fitness/shared/types';

export const useAddWorkout = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: WorkoutInput) => 
      apiClient.post('/api/workouts', data),
    
    onMutate: async (newWorkout) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['workouts'] });
      
      // Snapshot previous value
      const previous = queryClient.getQueryData(['workouts']);
      
      // Optimistically update
      queryClient.setQueryData(['workouts'], (old: any) => ({
        ...old,
        data: [{ ...newWorkout, id: 'temp-' + Date.now() }, ...old.data]
      }));
      
      return { previous };
    },
    
    onError: (err, newWorkout, context) => {
      // Rollback on error
      queryClient.setQueryData(['workouts'], context?.previous);
    },
    
    onSettled: () => {
      // Refetch after mutation
      queryClient.invalidateQueries({ queryKey: ['workouts'] });
    }
  });
};
```

### Shared UI Component

```typescript
// packages/frontend/src/shared/ui/Input/Input.tsx
import { forwardRef } from 'react';
import { cn } from '@/shared/lib/cn';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, hint, className, id, ...props }, ref) => {
    const inputId = id || `input-${label?.toLowerCase().replace(/\s/g, '-')}`;
    
    return (
      <div className="space-y-1">
        {label && (
          <label 
            htmlFor={inputId}
            className="block text-sm font-medium text-text"
          >
            {label}
          </label>
        )}
        
        <input
          ref={ref}
          id={inputId}
          className={cn(
            'w-full h-10 px-3 border rounded-md',
            'transition-colors duration-150',
            'focus:outline-none focus:ring-2 focus:ring-primary/20',
            error 
              ? 'border-error focus:border-error' 
              : 'border-border focus:border-primary',
            className
          )}
          aria-invalid={!!error}
          aria-describedby={error ? `${inputId}-error` : undefined}
          {...props}
        />
        
        {error && (
          <p 
            id={`${inputId}-error`}
            className="text-sm text-error"
            role="alert"
          >
            {error}
          </p>
        )}
        
        {hint && !error && (
          <p className="text-sm text-text-muted">{hint}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
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
  it('should show error for empty weight', async () => {
    render(<WorkoutForm />, { wrapper: createWrapper() });
    
    fireEvent.click(screen.getByText(/добавить/i));
    
    expect(await screen.findByText(/введите вес/i)).toBeInTheDocument();
  });
  
  it('should show error for non-numeric weight', async () => {
    render(<WorkoutForm />, { wrapper: createWrapper() });
    
    fireEvent.change(screen.getByLabelText(/вес/i), {
      target: { value: 'abc' }
    });
    fireEvent.click(screen.getByText(/добавить/i));
    
    expect(await screen.findByText(/должно быть число/i)).toBeInTheDocument();
  });
  
  it('should submit valid form', async () => {
    const onSuccess = vi.fn();
    
    render(<WorkoutForm onSuccess={onSuccess} />, { wrapper: createWrapper() });
    
    // Fill form
    fireEvent.change(screen.getByLabelText(/вес/i), {
      target: { value: '100' }
    });
    fireEvent.change(screen.getByLabelText(/повторения/i), {
      target: { value: '5' }
    });
    
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

### Responsive First

```css
/* Mobile first */
.card {
  padding: var(--space-sm);
}

/* Tablet */
@media (min-width: 640px) {
  .card {
    padding: var(--space-md);
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .card {
    padding: var(--space-lg);
  }
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

