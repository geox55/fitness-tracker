# BEST PRACTICES

## Best Practice #1: One-Tap Logging

**Goal:** Пользователь логирует подход за < 30 секунд

### UX/UI
- Предзаполненные поля (вес из прошлого раза)
- Крупные кнопки (для тренировочных перчаток)
- Быстрое переключение между подходами

### Technical
```typescript
// Оптимистичное обновление
const { mutate } = useAddWorkout({
  onMutate: async (newLog) => {
    // Отмена текущих запросов
    await queryClient.cancelQueries({ queryKey: ['workouts'] });
    
    // Сохранение предыдущего состояния
    const previous = queryClient.getQueryData(['workouts']);
    
    // Оптимистичное обновление
    queryClient.setQueryData(['workouts'], (old) => [newLog, ...old]);
    
    return { previous };
  },
  onError: (err, newLog, context) => {
    // Откат при ошибке
    queryClient.setQueryData(['workouts'], context.previous);
  }
});
```

---

## Best Practice #2: Contextual Progress Visualization

**Goal:** Пользователь видит тренд прогресса (макс, среднее, PR)

### UX/UI
- График линии (вес по времени)
- Маркер PR на графике
- Переключатель периода (неделя/месяц/год)

### Technical
```typescript
// Server-side агрегация
// GET /api/analytics/progress?exerciseId=X&from=Y&to=Z

// Client-side кэширование
const { data } = useQuery({
  queryKey: ['progress', exerciseId, period],
  queryFn: () => fetchProgress(exerciseId, period),
  staleTime: 1000 * 60 * 5, // 5 минут
  gcTime: 1000 * 60 * 30,   // 30 минут
});
```

---

## Best Practice #3: Pre-populated Templates

**Goal:** Повтор тренировки одним кликом

### Implementation
```typescript
// Таблица workout_templates
interface WorkoutTemplate {
  id: string;
  userId: string;
  name: string;
  exercises: {
    exerciseId: string;
    defaultWeight?: number;
    defaultReps?: number;
    defaultSets?: number;
  }[];
}

// Быстрый старт с шаблона
const startFromTemplate = (template: WorkoutTemplate) => {
  const workouts = template.exercises.map(ex => ({
    exerciseId: ex.exerciseId,
    weight: ex.defaultWeight || getLastWeight(ex.exerciseId),
    reps: ex.defaultReps || 5,
    sets: ex.defaultSets || 3
  }));
  
  setCurrentWorkout(workouts);
};
```

---

## Best Practice #4: Offline Capability

**Goal:** Приложение работает без интернета

### Architecture
```
┌──────────────────────────────────┐
│           UI Layer               │
├──────────────────────────────────┤
│         Zustand Store            │
│   (logs, pendingLogs, synced)    │
├──────────────────────────────────┤
│         IndexedDB Queue          │
│   (offline writes queue)         │
├──────────────────────────────────┤
│      Background Sync API         │
│   (auto-sync when online)        │
└──────────────────────────────────┘
```

### Implementation
```typescript
// Добавление в offline queue
export const addToOfflineQueue = async (log: WorkoutLog) => {
  const db = await openDB('fitness-tracker', 1);
  await db.add('offline-queue', {
    ...log,
    syncStatus: 'pending',
    createdAt: new Date().toISOString()
  });
};

// Синхронизация при восстановлении сети
export const syncQueue = async () => {
  const db = await openDB('fitness-tracker', 1);
  const logs = await db.getAll('offline-queue');
  
  for (const log of logs) {
    try {
      await apiClient.post('/api/workouts', log);
      await db.delete('offline-queue', log.id);
    } catch (err) {
      console.error('Sync failed for log:', log.id);
    }
  }
};

// Service Worker регистрация
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');
}
```

---

## Best Practice #5: Structured Exercise Data

**Goal:** Быстрый поиск упражнений

### UX/UI
- Autosuggest при вводе
- Группировка по мышечным группам
- "Недавние" упражнения первыми

### Implementation
```typescript
// API с поиском
// GET /api/exercises?search=присед&limit=10

// Frontend с debounce
const useExerciseSearch = (query: string) => {
  const [debouncedQuery] = useDebouncedValue(query, 300);
  
  return useQuery({
    queryKey: ['exercises', debouncedQuery],
    queryFn: () => searchExercises(debouncedQuery),
    enabled: debouncedQuery.length >= 2
  });
};

// Сортировка: недавние первыми
const sortExercises = (exercises: Exercise[], recentIds: string[]) => {
  return [...exercises].sort((a, b) => {
    const aRecent = recentIds.indexOf(a.id);
    const bRecent = recentIds.indexOf(b.id);
    
    if (aRecent >= 0 && bRecent < 0) return -1;
    if (bRecent >= 0 && aRecent < 0) return 1;
    return a.name.localeCompare(b.name);
  });
};
```

---

## Best Practice #6: Data Export

**Goal:** Пользователь может экспортировать свои данные

### Implementation
```typescript
// Backend: Stream CSV для больших данных
app.get('/api/analytics/export', async (req, res) => {
  const { format, from, to } = req.query;
  
  if (format === 'csv') {
    res.setHeader('Content-Type', 'text/csv');
    res.setHeader('Content-Disposition', 'attachment; filename=workouts.csv');
    
    const stream = db.prepare(`
      SELECT * FROM workout_logs 
      WHERE user_id = ? AND date BETWEEN ? AND ?
    `).iterate(req.user.id, from, to);
    
    res.write('date,exercise,weight,reps,sets\n');
    
    for (const row of stream) {
      res.write(`${row.date},${row.exercise_name},${row.weight},${row.reps},${row.sets}\n`);
    }
    
    res.end();
  }
});
```

---

## Anti-Patterns to Avoid

### ❌ Business Logic in UI

```typescript
// WRONG: API call in component
const WorkoutForm = () => {
  const handleSubmit = async (data) => {
    setLoading(true);
    await fetch('/api/workouts', { 
      method: 'POST', 
      body: JSON.stringify(data) 
    });
    setLoading(false);
  };
};

// CORRECT: Logic in model layer
const WorkoutForm = () => {
  const { mutate, isPending } = useAddWorkout();
  
  const handleSubmit = (data) => {
    mutate(data);
  };
};
```

### ❌ N+1 Queries

```typescript
// WRONG: Multiple queries
const workouts = await db.all('SELECT * FROM workout_logs WHERE user_id = ?', userId);
for (const workout of workouts) {
  workout.exercise = await db.get('SELECT * FROM exercises WHERE id = ?', workout.exercise_id);
}

// CORRECT: JOIN query
const workouts = await db.all(`
  SELECT w.*, e.name as exercise_name, e.muscle_group
  FROM workout_logs w
  JOIN exercises e ON w.exercise_id = e.id
  WHERE w.user_id = ?
`, userId);
```

### ❌ Missing Error Boundaries

```typescript
// CORRECT: Wrap features with error boundaries
<ErrorBoundary fallback={<ErrorMessage />}>
  <ProgressChart />
</ErrorBoundary>
```

### ❌ Uncontrolled Re-renders

```typescript
// WRONG: New object on every render
<Chart data={workouts.map(w => ({ x: w.date, y: w.weight }))} />

// CORRECT: Memoize
const chartData = useMemo(
  () => workouts.map(w => ({ x: w.date, y: w.weight })),
  [workouts]
);
<Chart data={chartData} />
```

---

## Performance Checklist

- [ ] Database indexes on frequently queried columns
- [ ] API pagination (limit/offset or cursor)
- [ ] Client-side caching (TanStack Query)
- [ ] Code splitting (dynamic imports)
- [ ] Image lazy loading
- [ ] Memoization (useMemo, useCallback)
- [ ] Debounce search inputs
- [ ] Virtual scrolling for long lists

---

## Security Checklist

- [ ] JWT token expiration (1 hour)
- [ ] Refresh token rotation
- [ ] Input validation (Zod schemas)
- [ ] SQL injection prevention (prepared statements)
- [ ] XSS prevention (sanitize output)
- [ ] CORS configuration
- [ ] Rate limiting
- [ ] HTTPS only in production

