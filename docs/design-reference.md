# Design Reference Documentation

Единый источник правды для frontend-разработки Fitness Tracker.

**Приоритет:** Информация из [`docs/spec/`](../spec/) имеет приоритет над визуальными референсами из HTML файлов.

---

## 1. Design System

### 1.1 Colors

Цветовая схема из спецификации (Фаза 3.3):

```
Primary:        #21808D (Teal)         — Active buttons, links
Secondary:      #5E5240 (Brown)        — Secondary actions
Background:     #FCFCF9 (Cream light)  — Main background
Surface:        #FFFFFD (Cream)        — Card background
Text:           #134252 (Dark slate)   — Primary text
Text-secondary: #626C71 (Slate)        — Helper text
Success:        #218081 (Teal)         — PR, achievements
Warning:        #A84B2F (Orange)        — Warnings, validations
Error:          #C0152F (Red)           — Errors
```

### 1.2 Typography

```
Heading 1:  30px, weight 600, letter-spacing -0.01em
Heading 2:  24px, weight 600
Heading 3:  18px, weight 550
Body:       14px, weight 400, line-height 1.5
Small:      12px, weight 400
Label:      12px, weight 500
```

### 1.3 Spacing

```
xs:  4px
sm:  8px
md:  16px
lg:  24px
xl:  32px
```

### 1.4 Border Radius

```
sm:   6px
md:   8px
lg:   12px
full: 9999px
```

### 1.5 Shadows

Использовать стандартные тени для карточек и elevation:
- Card shadow: `0 4px 20px -2px rgba(0, 0, 0, 0.05)`
- Focus ring: `0 0 0 2px rgba(33, 128, 141, 0.2)`

---

## 2. Component Inventory

Компоненты из спецификации (Фаза 3.3):

| Component | Purpose | Screen | Implementation Notes |
|-----------|---------|--------|---------------------|
| **WorkoutForm** | Форма логирования (упражнение, подходы, вес, повторения) | Workout | Pre-filled fields from history, large touch-friendly buttons |
| **WorkoutCard** | Карточка истории тренировки | History | Date, exercises list, duration, total volume |
| **ProgressChart** | График прогресса (Recharts) | Progress | Line chart with PR markers, period filters |
| **ExerciseSelect** | Dropdown/autosuggest выбора упражнения | Workout | Autosuggest, recent exercises first, categories |
| **FilterBar** | Фильтр по дате, упражнению | History, Progress | Chips/pills UI, date range picker |
| **StatsBadge** | Знак статистики (макс, средний, PR) | Progress | Display max weight, average, PR with dates |
| **Header** | Заголовок с навигацией | All | Sticky header, back button, title, actions |
| **BottomNav** | Нижняя навигация (4 tabs) | Mobile | Логирование, История, Прогресс, Профиль |

### 2.1 Bottom Navigation Tabs

Навигация для mobile (< 640px):
1. **Логирование** (Log) — иконка: edit_square
2. **История** (History) — иконка: history
3. **Прогресс** (Progress/Charts) — иконка: show_chart
4. **Профиль** (Profile/Templates) — иконка: folder_copy или person

---

## 3. Screen References

HTML файлы в [`docs/design/`](design/) служат **визуальными референсами** для понимания layout и UX patterns. **НЕ использовать цвета из HTML** — они отличаются от спецификации.

| Screen | File | Use for | Notes |
|--------|------|---------|-------|
| **Login** | [`login-screen.html`](design/login-screen.html) | Form layout, input styling, social auth buttons | Layout structure, input field design |
| **Signup** | [`logup-screen.html`](design/logup-screen.html) | Registration flow, password toggle | Multi-step form patterns |
| **Workout Logging** | [`workout-screen.html`](design/workout-screen.html) | Sets table, timer UI, exercise card, active set indicator | Sets logging flow, exercise swap button |
| **Progress Charts** | [`progress-chart-screen.html`](design/progress-chart-screen.html) | Chart layout, period toggles (1W/1M/3M/1Y/All), stats cards, recent history | Chart visualization patterns, period selector UI |
| **History** | [`history-screen.html`](design/history-screen.html) | Card list, search bar, filter chips, month grouping, FAB | List layout, search/filter patterns, pagination |

### 3.1 Key UX Patterns from HTML References

**Workout Screen:**
- Timer pill in header
- Active set indicator (left border highlight)
- Completed sets (grayed out with checkmark)
- Upcoming sets (preview with dashed border)
- Exercise swap button
- Next exercise preview card
- Add Exercise button

**Progress Screen:**
- Exercise selector chips (horizontal scroll)
- Large headline stat (max weight with trend indicator)
- Period toggle buttons (radio-style in pill container)
- Chart with PR marker (pulsing animation)
- Stats summary cards (3-column grid)
- Recent history list below chart

**History Screen:**
- Sticky header with search bar
- Filter chips (All Time, This Month, By Exercise, PRs Only)
- Month grouping with sticky labels
- Workout cards with date column, exercise list, duration, total volume
- PR badge on cards
- Floating Action Button (FAB) for quick add
- Load more button at bottom

---

## 4. Responsive Design

Breakpoints из спецификации (Фаза 3.5):

### Mobile (< 640px)
- Bottom navigation (4 tabs)
- Full-width forms
- Vertical charts
- Single column layout

### Tablet (640px - 1024px)
- Side navigation
- Grid layout (2-column)
- Horizontal charts (if space allows)

### Desktop (> 1024px)
- Side navigation
- Full analytics dashboard (3-column)
- Expanded chart views
- Multi-column layouts

---

## 5. Accessibility Requirements

Требования из спецификации (Фаза 3.6):

### 5.1 Keyboard Navigation
- **Tab** между полями
- **Enter** для submit форм
- **Arrow keys** для навигации в списках (опционально)

### 5.2 ARIA Labels
- Все кнопки и инпуты должны иметь `aria-label` или `aria-labelledby`
- Интерактивные элементы с иконками должны иметь текстовые labels

### 5.3 Color Contrast
- **Текст:** 4.5:1 (WCAG AA)
- **Крупные элементы:** 3:1 (WCAG AA)

### 5.4 Focus Indicators
- Видимый outline при навигации с клавиатуры
- Focus ring: `0 0 0 2px rgba(33, 128, 141, 0.2)`

---

## 6. Performance Considerations

Требования из спецификации (Фаза 3.7):

### 6.1 Chart Rendering
- Recharts на клиенте
- Виртуализация для больших датасетов
- **Максимум 6 месяцев** данных на экран одновременно
- Client-side aggregation для быстрой отрисовки

### 6.2 Form Validation
- Client-side validation (instant feedback)
- Zod schemas для валидации

### 6.3 Image Optimization
- Lazy loading для карточек истории
- Оптимизация изображений упражнений

### 6.4 Caching
- React Query с `stale-while-revalidate` стратегией
- Кэширование последних логов в IndexedDB (offline-first)

---

## 7. Important Notes

### 7.1 Color Discrepancies

⚠️ **Внимание:** HTML референсы используют другую цветовую схему:
- HTML использует: `primary: #f9f506` (Yellow)
- Спецификация требует: `primary: #21808D` (Teal)

**При реализации:**
- ✅ Использовать цвета из спецификации (Teal-based)
- ✅ HTML файлы использовать **только** для понимания layout и UX patterns
- ❌ НЕ копировать цвета из HTML напрямую

### 7.2 Font Discrepancies

HTML референсы используют **Spline Sans**, но спецификация не указывает конкретный шрифт. Использовать системный шрифт или шрифт, указанный в проекте.

### 7.3 Component Implementation Priority

При разработке компонентов:
1. Следовать структуре из спецификации (Фаза 3.4 — детальные экраны)
2. Использовать HTML референсы для визуального понимания layout
3. Применять цвета и типографику из спецификации
4. Соблюдать responsive breakpoints
5. Обеспечить accessibility требования

---

## 8. User Journeys Reference

Детальные сценарии из спецификации (Фаза 3.1):

### 8.1 Логирование тренировки (на тренировке)
**Time:** 30-60 секунд на упражнение

1. Открыть приложение (быстрый доступ, offline mode)
2. Выбрать упражнение из истории или шаблона
3. Ввести: подходы, вес, повторения, RPE (опционально)
4. Нажать "Добавить подход" (повторить x3-5)
5. Нажать "Завершить упражнение"
6. Перейти к следующему упражнению
7. Нажать "Завершить тренировку"
8. Синхронизация с сервером

### 8.2 Просмотр прогресса (дома, анализ)

1. Открыть приложение
2. Перейти на вкладку "Прогресс"
3. Выбрать упражнение (присед, жим и т.д.)
4. Выбрать период (неделя/месяц/год)
5. Увидеть график (вес по времени)
6. Увидеть статистику (макс, средний, PR)
7. Опционально: экспортировать или поделиться

### 8.3 Планирование тренировки (вечер перед тренировкой)

1. Открыть приложение
2. Перейти на вкладку "Планы"
3. Выбрать или создать шаблон (PPL, Upper/Lower)
4. Добавить упражнения
5. Сохранить шаблон
6. На тренировке: использовать шаблон + логировать данные

---

## 9. Quick Reference

### Colors (CSS Variables)
```css
--color-primary: #21808D;
--color-secondary: #5E5240;
--color-background: #FCFCF9;
--color-surface: #FFFFFD;
--color-text: #134252;
--color-text-secondary: #626C71;
--color-success: #218081;
--color-warning: #A84B2F;
--color-error: #C0152F;
```

### Spacing (Tailwind-like)
```css
--spacing-xs: 4px;
--spacing-sm: 8px;
--spacing-md: 16px;
--spacing-lg: 24px;
--spacing-xl: 32px;
```

### Border Radius
```css
--radius-sm: 6px;
--radius-md: 8px;
--radius-lg: 12px;
--radius-full: 9999px;
```

---

**Last Updated:** December 2025  
**Version:** 1.0  
**Source:** [`docs/spec/05-ui-ux-guidelines.md`](../spec/05-ui-ux-guidelines.md)

