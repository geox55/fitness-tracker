# UI/UX GUIDELINES

## Design System

### Color Palette

```css
:root {
  /* Primary */
  --color-primary: #218081;          /* Teal — Active buttons, links */
  --color-primary-hover: #1a6768;
  --color-primary-light: #e6f3f3;
  
  /* Secondary */
  --color-secondary: #5E5240;        /* Brown — Secondary actions */
  
  /* Background */
  --color-bg: #FCFCF9;               /* Cream light — Main background */
  --color-surface: #FFFFFD;          /* Cream — Card background */
  --color-surface-hover: #F8F8F5;
  
  /* Text */
  --color-text: #134252;             /* Dark slate — Primary text */
  --color-text-secondary: #626C71;   /* Slate — Helper text */
  --color-text-muted: #9CA3AF;
  
  /* Semantic */
  --color-success: #218081;          /* Teal — PR, achievements */
  --color-warning: #A84B2F;          /* Orange — Warnings */
  --color-error: #C0152F;            /* Red — Errors */
  
  /* Border */
  --color-border: #E5E7EB;
  --color-border-focus: #218081;
}
```

### Typography

```css
:root {
  --font-family: 'Inter', -apple-system, sans-serif;
  
  /* Sizes */
  --text-h1: 30px;
  --text-h2: 24px;
  --text-h3: 18px;
  --text-body: 14px;
  --text-small: 12px;
  --text-label: 12px;
  
  /* Weights */
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 550;
  --font-weight-bold: 600;
  
  /* Line heights */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;
}

/* Headings */
h1 { font-size: var(--text-h1); font-weight: var(--font-weight-bold); letter-spacing: -0.01em; }
h2 { font-size: var(--text-h2); font-weight: var(--font-weight-bold); }
h3 { font-size: var(--text-h3); font-weight: var(--font-weight-semibold); }
```

### Spacing

```css
:root {
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  --space-2xl: 48px;
}
```

### Border Radius

```css
:root {
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 9999px;
}
```

---

## Component Library

### Button

```tsx
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'outline' | 'ghost';
  size: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
}

// Usage
<Button variant="primary" size="md">Add Set</Button>
<Button variant="outline" size="sm" loading>Saving...</Button>
```

**Styles:**
```css
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  font-weight: var(--font-weight-medium);
  transition: all 0.15s ease;
}

.btn--primary {
  background: var(--color-primary);
  color: white;
}
.btn--primary:hover { background: var(--color-primary-hover); }

.btn--outline {
  border: 1px solid var(--color-border);
  background: transparent;
}
.btn--outline:hover { background: var(--color-surface-hover); }

/* Sizes */
.btn--sm { height: 32px; padding: 0 12px; font-size: 13px; }
.btn--md { height: 40px; padding: 0 16px; font-size: 14px; }
.btn--lg { height: 48px; padding: 0 24px; font-size: 16px; }
```

### Input

```tsx
interface InputProps {
  label: string;
  error?: string;
  hint?: string;
  type?: 'text' | 'number' | 'email' | 'password';
}

// Usage
<Input label="Weight (kg)" type="number" error="Required" />
```

**Styles:**
```css
.input {
  width: 100%;
  height: 40px;
  padding: 0 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--text-body);
  transition: border-color 0.15s ease;
}

.input:focus {
  outline: none;
  border-color: var(--color-border-focus);
  box-shadow: 0 0 0 3px var(--color-primary-light);
}

.input--error {
  border-color: var(--color-error);
}

.input-error-text {
  color: var(--color-error);
  font-size: var(--text-small);
  margin-top: var(--space-xs);
}
```

### Card

```tsx
interface CardProps {
  padding?: 'sm' | 'md' | 'lg';
  hover?: boolean;
}

// Usage
<Card padding="md" hover>
  <WorkoutDetails />
</Card>
```

**Styles:**
```css
.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
}

.card--hover:hover {
  border-color: var(--color-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.card--sm { padding: var(--space-sm); }
.card--md { padding: var(--space-md); }
.card--lg { padding: var(--space-lg); }
```

### Select / Dropdown

```tsx
interface SelectProps {
  label: string;
  options: { value: string; label: string }[];
  searchable?: boolean;
}
```

### Badge

```tsx
interface BadgeProps {
  variant: 'default' | 'success' | 'warning' | 'error';
}

// Usage
<Badge variant="success">PR!</Badge>
<Badge variant="default">5 sets</Badge>
```

---

## Screen Layouts

### Логирование тренировки

```
┌─────────────────────────────────────┐
│ Новая тренировка            [×]    │  ← Header
├─────────────────────────────────────┤
│ 🏋️ Упражнение                       │
│ ┌─────────────────────────────────┐ │
│ │ Поиск или выбрать...            │ │ ← ExerciseSelect
│ └─────────────────────────────────┘ │
├─────────────────────────────────────┤
│ Текущий подход: 1 / 5               │
├─────────────────────────────────────┤
│ Вес (кг)                            │
│ ┌─────────────────────────────────┐ │
│ │ 100                             │ │ ← Prefilled
│ └─────────────────────────────────┘ │
│ Повторения                          │
│ ┌─────────────────────────────────┐ │
│ │ 5                               │ │
│ └─────────────────────────────────┘ │
│ RPE (опционально)                   │
│ ┌─────────────────────────────────┐ │
│ │ 7 / 10                          │ │
│ └─────────────────────────────────┘ │
├─────────────────────────────────────┤
│ [  Добавить подход  ]  [ − Удалить ]│
├─────────────────────────────────────┤
│ Сохранённые:                        │
│ 100×5 | 100×5 | 95×3                │
├─────────────────────────────────────┤
│ [ Завершить ]       [ Отмена ]      │
└─────────────────────────────────────┘
```

### Просмотр прогресса

```
┌─────────────────────────────────────┐
│ Прогресс                            │
├─────────────────────────────────────┤
│ [Упражнение ▼]    [Период ▼]        │
├─────────────────────────────────────┤
│ Присед • Последний месяц            │
├─────────────────────────────────────┤
│ Макс: 150 кг  Средний: 120 кг       │
│ 🏆 PR: 155 кг (01.12.2024)          │
├─────────────────────────────────────┤
│                                     │
│  150 ┼─────────●                    │
│      │        /                     │
│  125 ┼───────/──────●               │
│      │      /        \              │
│  100 ┼─────●          ●─────        │
│      └──────────────────────        │
│      01    05    10    15    20     │
│                                     │
├─────────────────────────────────────┤
│ История:                            │
│ 20.12 — 150 кг × 3                  │
│ 18.12 — 145 кг × 5                  │
│ 15.12 — 145 кг × 3                  │
├─────────────────────────────────────┤
│ [ Export ]            [ Share ]     │
└─────────────────────────────────────┘
```

### История тренировок

```
┌─────────────────────────────────────┐
│ История                             │
├─────────────────────────────────────┤
│ [Дата ▼]        [Упражнение ▼]      │
├─────────────────────────────────────┤
│ ┌─────────────────────────────────┐ │
│ │ 20 декабря 2024                 │ │
│ │ Верхняя часть тела              │ │
│ │ • Жим лежа: 100 кг × 5 × 3      │ │
│ │ • Тяга штанги: 120 кг × 5 × 4   │ │
│ │ ⏱ 45 мин                        │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ 18 декабря 2024                 │ │
│ │ Нижняя часть тела               │ │
│ │ • Присед: 150 кг × 3 × 5 🏆     │ │
│ │ • Становая: 180 кг × 1 × 3      │ │
│ │ ⏱ 50 мин                        │ │
│ └─────────────────────────────────┘ │
│                                     │
│ [ Load more ]                       │
└─────────────────────────────────────┘
```

---

## Responsive Breakpoints

```css
/* Mobile first */
.container { width: 100%; padding: 0 16px; }

/* Tablet: 640px+ */
@media (min-width: 640px) {
  .container { max-width: 640px; margin: 0 auto; }
  /* Side navigation appears */
  /* 2-column grid for cards */
}

/* Desktop: 1024px+ */
@media (min-width: 1024px) {
  .container { max-width: 1024px; }
  /* Full analytics dashboard */
  /* 3-column grid */
}
```

### Mobile (< 640px)
- Bottom navigation
- Full-width forms
- Vertical charts
- Single column layout

### Tablet (640px - 1024px)
- Side navigation
- 2-column grid
- Expanded cards

### Desktop (> 1024px)
- Side navigation
- 3-column dashboard
- Full chart controls

---

## Accessibility

### Requirements

- **Keyboard navigation:** Tab между полями, Enter для submit
- **ARIA labels:** Все интерактивные элементы
- **Color contrast:** 4.5:1 для текста, 3:1 для крупных элементов
- **Focus indicators:** Visible outline

### Implementation

```tsx
// Good
<button aria-label="Add new set">
  <PlusIcon aria-hidden="true" />
</button>

// Good
<input
  id="weight"
  aria-describedby="weight-error"
  aria-invalid={!!error}
/>
{error && <span id="weight-error" role="alert">{error}</span>}
```

---

## Animations

### Transitions

```css
/* Default transition */
.transition-default {
  transition: all 0.15s ease;
}

/* Button hover */
.btn {
  transition: background-color 0.15s ease, transform 0.1s ease;
}
.btn:active {
  transform: scale(0.98);
}

/* Card hover */
.card {
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
```

### Micro-interactions

```css
/* Success animation */
@keyframes success-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.success-badge {
  animation: success-pulse 0.3s ease;
}

/* Loading spinner */
@keyframes spin {
  to { transform: rotate(360deg); }
}

.spinner {
  animation: spin 1s linear infinite;
}
```

---

## Icons

Используем **Lucide React** для иконок.

```tsx
import { 
  Plus, 
  Trash2, 
  TrendingUp, 
  Calendar,
  Dumbbell,
  Trophy
} from 'lucide-react';

// Usage
<Button>
  <Plus size={16} />
  Add Set
</Button>
```

### Icon Sizes

| Context | Size |
|---------|------|
| Button inline | 16px |
| Button only | 20px |
| Navigation | 24px |
| Empty state | 48px |

