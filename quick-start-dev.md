# QUICK START GUIDES FOR DEVELOPERS
## Fitness Tracker Implementation

---

## BACKEND DEVELOPER QUICK START

### Getting Started

```bash
# Clone and setup
git clone <repo>
cd fitness-tracker
npm install

# Setup environment
cp .env.example .env
# Edit .env:
# JWT_SECRET=your-secret-key
# NODE_ENV=development
# DATABASE_URL=./data/fitness.db

# Run migrations
npm run db:migrate

# Start dev server
npm run dev

# Run tests
npm test
npm run test:watch
npm run test:coverage
```

### Your First Task: POST /api/workouts (Endpoint)

**TDD Workflow:**

```bash
# 1. Read the test (it already exists)
cat server/__tests__/api/workouts.test.ts

# 2. Run test (RED - should fail)
npm test -- workouts.test.ts

# 3. Implement handler (pages/api/workouts/route.ts)
# 4. Run test again (GREEN - should pass)
npm test -- workouts.test.ts

# 5. Refactor code, ensure test still passes
npm test -- workouts.test.ts --watch
```

### File Structure (What You'll Touch)

```
app/api/workouts/route.ts          ← Handler layer (you implement here)
  ↓ imports
server/services/workout.service.ts  ← Business logic
  ↓ imports
server/repositories/workout.repository.ts ← DB access
  ↓ imports
server/db/database.ts               ← SQLite connection (don't modify)

server/__tests__/
├── api/workouts.test.ts            ← Read these tests first
├── services/workout.service.test.ts
└── ...
```

### Implementation Template

```typescript
// app/api/workouts/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { authMiddleware } from '@/lib/middleware';
import { WorkoutService } from '@/server/services/workout.service';
import { workoutSchema } from '@/server/db/schema';

export async function POST(req: NextRequest) {
  try {
    // 1. Authenticate
    const user = await authMiddleware(req);
    
    // 2. Parse request body
    const body = await req.json();
    
    // 3. Validate input
    const validated = workoutSchema.parse(body);
    
    // 4. Call service
    const service = new WorkoutService();
    const result = await service.createWorkout(user.userId, validated);
    
    // 5. Return response
    return NextResponse.json(result, { status: 201 });
  } catch (error) {
    // Error handling
    if (error instanceof SyntaxError) {
      return NextResponse.json(
        { error: 'Invalid JSON' },
        { status: 400 }
      );
    }
    
    return NextResponse.json(
      { error: error.message },
      { status: error.status || 500 }
    );
  }
}
```

### Common Commands

```bash
# Run specific test file
npm test -- workouts.test.ts

# Run in watch mode (reruns on file change)
npm test -- --watch

# Run with coverage
npm test -- --coverage

# Run only unit tests (skip integration)
npm test -- --testPathPattern="services|utils"

# Debug a test
node --inspect-brk ./node_modules/.bin/jest --runInBand
```

### Debugging Tips

```typescript
// Add console.log to see what's happening
console.log('Received body:', body);

// Use debugger
debugger; // Then run: npm test -- --inspect-brk

// Check database state
const logs = db.prepare('SELECT * FROM workout_logs').all();
console.log('DB logs:', logs);
```

---

## FRONTEND DEVELOPER QUICK START

### Getting Started

```bash
# Setup (same as backend)
git clone <repo>
cd fitness-tracker
npm install
cp .env.example .env

# Start dev server (includes Next.js frontend dev server)
npm run dev

# Run component tests
npm test

# Run E2E tests
npm run e2e

# Run with coverage
npm test -- --coverage
```

### Your First Task: WorkoutForm Component

**TDD Workflow:**

```bash
# 1. Read the test
cat components/__tests__/WorkoutForm.test.tsx

# 2. Run test (RED)
npm test -- WorkoutForm.test.tsx

# 3. Create component (components/forms/WorkoutForm.tsx)
# 4. Implement step by step
# 5. Run test (GREEN)
npm test -- WorkoutForm.test.tsx

# 6. Refactor and style
```

### File Structure (What You'll Touch)

```
components/
├── forms/
│   ├── WorkoutForm.tsx              ← You implement here
│   ├── __tests__/
│   │   └── WorkoutForm.test.tsx     ← Read this first
│   └── ...
├── charts/
│   ├── ProgressChart.tsx
│   └── ...
└── ui/
    ├── Button.tsx                    ← Use these primitives
    ├── Input.tsx
    └── ...

app/(protected)/
├── dashboard/page.tsx               ← Page that uses components
├── progress/page.tsx
└── ...

lib/
├── api/
│   ├── workouts.ts                  ← API calls (use in component)
│   └── ...
├── hooks/
│   ├── useWorkouts.ts               ← Custom hooks
│   └── ...
└── utils/
    ├── format.ts                     ← Helper functions
    └── ...
```

### Implementation Template

```typescript
// components/forms/WorkoutForm.tsx
'use client';

import React, { useState } from 'react';
import { useAddWorkout } from '@/lib/api/workouts';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { ExerciseSelect } from './ExerciseSelect';

interface WorkoutFormProps {
  onSuccess?: () => void;
}

export const WorkoutForm: React.FC<WorkoutFormProps> = ({ onSuccess }) => {
  const [weight, setWeight] = useState('');
  const [reps, setReps] = useState('');
  const [exerciseId, setExerciseId] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  
  const { mutate, isPending } = useAddWorkout();
  
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    if (!exerciseId) newErrors.exercise = 'Select an exercise';
    if (!weight) newErrors.weight = 'Weight is required';
    if (isNaN(Number(weight))) newErrors.weight = 'Must be a number';
    if (Number(weight) <= 0) newErrors.weight = 'Must be positive';
    if (!reps) newErrors.reps = 'Reps is required';
    if (isNaN(Number(reps))) newErrors.reps = 'Must be a number';
    if (Number(reps) < 1 || Number(reps) > 100) 
      newErrors.reps = 'Must be between 1 and 100';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
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
      <div>
        <label htmlFor="exercise" className="form-label">Exercise</label>
        <ExerciseSelect 
          value={exerciseId}
          onChange={setExerciseId}
        />
        {errors.exercise && <span className="text-error">{errors.exercise}</span>}
      </div>
      
      <div>
        <label htmlFor="weight" className="form-label">Weight (kg)</label>
        <Input
          id="weight"
          type="number"
          value={weight}
          onChange={e => setWeight(e.target.value)}
          placeholder="100"
          disabled={isPending}
        />
        {errors.weight && <span className="text-error">{errors.weight}</span>}
      </div>
      
      <div>
        <label htmlFor="reps" className="form-label">Reps</label>
        <Input
          id="reps"
          type="number"
          value={reps}
          onChange={e => setReps(e.target.value)}
          placeholder="5"
          disabled={isPending}
        />
        {errors.reps && <span className="text-error">{errors.reps}</span>}
      </div>
      
      <Button
        type="submit"
        disabled={isPending}
        className="w-full"
      >
        {isPending ? 'Adding...' : 'Add Workout'}
      </Button>
    </form>
  );
};
```

### Common Commands

```bash
# Run specific component test
npm test -- WorkoutForm.test.tsx

# Run in watch mode
npm test -- --watch

# Debug component in browser
npm run dev
# Open http://localhost:3000
# Right-click → Inspect

# Run E2E test
npm run e2e

# Run E2E with GUI
npm run e2e -- --headed

# Update snapshots (after intentional UI changes)
npm test -- --updateSnapshot
```

### Testing Tips

```typescript
// Test file structure
describe('WorkoutForm', () => {
  it('should validate weight is required', () => {
    render(<WorkoutForm />);
    fireEvent.click(screen.getByText(/submit/i));
    expect(screen.getByText(/weight is required/i)).toBeInTheDocument();
  });
});

// Use data-testid for reliable selectors
// In component:
<input data-testid="weight-input" />

// In test:
fireEvent.change(screen.getByTestId('weight-input'), { target: { value: '100' } });
```

---

## QA ENGINEER QUICK START

### Getting Started

```bash
# Setup Cypress for E2E tests
npm run e2e:open

# Run all E2E tests
npm run e2e

# Run specific test
npm run e2e -- --spec "cypress/e2e/workout.cy.ts"

# Run with specific browser
npm run e2e -- --browser chrome
npm run e2e -- --browser firefox
```

### Your First Test: Add Workout E2E

```typescript
// cypress/e2e/workout-add.cy.ts
describe('Add Workout', () => {
  beforeEach(() => {
    cy.login('test@example.com', 'password123');
    cy.visit('/dashboard');
  });
  
  it('should add a workout successfully', () => {
    // Click "New Workout" button
    cy.get('[data-testid="new-workout-btn"]').click();
    
    // Modal should open
    cy.get('[data-testid="workout-form"]').should('be.visible');
    
    // Fill exercise
    cy.get('[data-testid="exercise-input"]').type('Squat');
    cy.get('[data-testid="exercise-option"]').first().click();
    
    // Fill weight
    cy.get('[data-testid="weight-input"]').type('150');
    
    // Fill reps
    cy.get('[data-testid="reps-input"]').type('5');
    
    // Submit
    cy.get('[data-testid="submit-btn"]').click();
    
    // Success notification
    cy.get('[data-testid="success-toast"]').should('be.visible');
    
    // Form should close
    cy.get('[data-testid="workout-form"]').should('not.exist');
    
    // New workout should appear in list
    cy.get('[data-testid="workout-list"]')
      .should('contain', 'Squat')
      .should('contain', '150 kg');
  });
  
  it('should show validation errors', () => {
    cy.get('[data-testid="new-workout-btn"]').click();
    cy.get('[data-testid="submit-btn"]').click();
    
    cy.get('[data-testid="error-message"]')
      .should('contain', 'Weight is required');
  });
});
```

### Test Case Template

```
Test Case: TC-001
Title: Log Workout with Valid Data

Preconditions:
  1. User is logged in
  2. Navigate to Dashboard

Steps:
  1. Click "New Workout" button
  2. Select exercise: "Squat"
  3. Enter weight: "150 kg"
  4. Enter reps: "5"
  5. Click "Submit"

Expected Results:
  1. Form closes
  2. Success notification appears
  3. New workout appears in list
  4. Workout is persisted (visible after refresh)

Status:
  ☐ PASS ☐ FAIL ☐ BLOCKED ☐ IN PROGRESS

Notes:
  [Any observations]
```

### Common Commands

```bash
# Run tests in headless mode (CI)
npm run e2e

# Run with GUI (development)
npm run e2e:open

# Run specific file
npm run e2e -- --spec "cypress/e2e/progress.cy.ts"

# Debug specific test
npm run e2e -- --spec "cypress/e2e/progress.cy.ts" --headed

# Record video of test run
npm run e2e -- --record

# Update screenshots/baselines
npm run e2e -- --updateSnapshots
```

---

## COMMON ISSUES & SOLUTIONS

### Backend Issues

**Q: "Module not found: WorkoutRepository"**
```typescript
// Make sure file exists and path is correct:
// ✓ server/repositories/workout.repository.ts
// In import:
import { WorkoutRepository } from '@/server/repositories/workout.repository';
// NOT:
import { WorkoutRepository } from '../../server/repositories/workout'; // Missing extension
```

**Q: "Test fails: Unauthorized"**
```typescript
// Add auth header in mock request:
const { req, res } = createMocks({
  method: 'POST',
  headers: {
    authorization: 'Bearer valid-token' // Don't forget this!
  }
});
```

**Q: "Database locked error"**
```typescript
// Ensure WAL mode is enabled:
// In Database.getInstance():
db.pragma('journal_mode = WAL');
db.pragma('busy_timeout = 5000');
```

### Frontend Issues

**Q: "Component won't re-render"**
```typescript
// Use React.FC properly:
export const MyComponent: React.FC = () => {
  const [state, setState] = useState(0);
  return <div>{state}</div>;
};

// NOT:
export const MyComponent = () => {
  // Missing type annotation
};
```

**Q: "useQuery hook error: no QueryClientProvider"**
```typescript
// Wrap your component in provider:
<QueryClientProvider client={queryClient}>
  <MyComponent />
</QueryClientProvider>
```

**Q: "Test fails: element not found"**
```typescript
// Use data-testid for reliable selection:
// In component:
<button data-testid="submit-btn">Submit</button>

// In test:
screen.getByTestId('submit-btn');

// NOT:
screen.getByRole('button', { name: /submit/i }); // Fragile if text changes
```

### E2E Testing Issues

**Q: "Test times out waiting for element"**
```typescript
// Increase timeout:
cy.get('[data-testid="workout-form"]', { timeout: 10000 }).should('be.visible');

// Or use cy.intercept to wait for API:
cy.intercept('GET', '/api/workouts').as('getWorkouts');
cy.visit('/dashboard');
cy.wait('@getWorkouts');
```

**Q: "Login fails in E2E test"**
```typescript
// Create login helper:
// cypress/support/commands.ts
Cypress.Commands.add('login', (email, password) => {
  cy.visit('/login');
  cy.get('[data-testid="email"]').type(email);
  cy.get('[data-testid="password"]').type(password);
  cy.get('[data-testid="submit"]').click();
  cy.url().should('include', '/dashboard');
});

// Use in test:
cy.login('test@example.com', 'password123');
```

---

## DEBUGGING WORKFLOW

### 1. Backend Debugging

```bash
# Option A: Console logs
console.log('Received:', body);

# Option B: Debugger
# Add to code:
debugger;

# Then run:
node --inspect-brk ./node_modules/.bin/jest --runInBand

# Then open: chrome://inspect

# Option C: Database inspection
import { Database } from '@/server/db/database';
const db = Database.getInstance();
const logs = db.prepare('SELECT * FROM workout_logs LIMIT 5').all();
console.log(logs);
```

### 2. Frontend Debugging

```bash
# Option A: React DevTools
npm run dev
# Open in browser, install React DevTools extension

# Option B: Browser console
console.log('Component props:', props);

# Option C: Jest debug
npm test -- --inspect-brk --runInBand

# Option D: VS Code debugger
# .vscode/launch.json:
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "node",
      "request": "launch",
      "name": "Jest Debug",
      "program": "${workspaceFolder}/node_modules/.bin/jest",
      "args": ["--runInBand"],
      "console": "integratedTerminal"
    }
  ]
}
```

### 3. API Debugging

```bash
# Option A: VS Code REST Client
# Create: test-api.http
POST http://localhost:3000/api/workouts
Authorization: Bearer <your-token>
Content-Type: application/json

{
  "exerciseId": "ex1",
  "weight": 100,
  "reps": 5
}

# Option B: curl
curl -X POST http://localhost:3000/api/workouts \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"exerciseId":"ex1","weight":100,"reps":5}'

# Option C: Postman
# Import: postman-collection.json (from repo root)
```

---

## USEFUL COMMANDS

```bash
# Development
npm run dev              # Start dev server
npm test               # Run all tests
npm test:watch        # Watch mode
npm test:coverage     # Generate coverage report
npm run e2e           # Run E2E tests
npm run e2e:open      # Open E2E GUI
npm run lint          # Lint code
npm run type-check    # TypeScript check
npm run format        # Format code with Prettier

# Database
npm run db:migrate    # Run migrations
npm run db:reset      # Reset to initial state
npm run db:seed       # Seed test data

# Build & Production
npm run build         # Build for production
npm start             # Start production server
npm run docker:build  # Build Docker image
npm run docker:run    # Run Docker container
```

---

## RESOURCES & DOCUMENTATION

- **Next.js Docs:** https://nextjs.org/docs
- **React Testing Library:** https://testing-library.com/
- **Jest Docs:** https://jestjs.io/
- **Cypress Docs:** https://docs.cypress.io/
- **SQLite Docs:** https://www.sqlite.org/docs.html
- **Better SQLite3:** https://github.com/WiseLibs/better-sqlite3/wiki
- **Zustand:** https://github.com/pmndrs/zustand
- **TanStack Query:** https://tanstack.com/query/latest
- **Recharts:** https://recharts.org/

---

## ASKING FOR HELP

When you get stuck, provide:

1. **Error message** (full stack trace)
2. **What you were trying to do**
3. **Code snippet** (relevant part)
4. **What you've already tried**

Example:

```
I'm getting error: "TypeError: Cannot read properties of undefined (reading 'id')"

What I was trying to do:
  - Add a workout via POST /api/workouts

Code snippet:
  const workout = await service.createWorkout(userId, { ... });
  console.log(workout.id); // Error here

Stack trace:
  at WorkoutService.createWorkout (server/services/workout.service.ts:25)

What I've tried:
  - Added console.log before the line (workout is undefined)
  - Checked if repository.create() is returning null
```

---

**Remember: Tests are your guide. If a test fails, read what it expects and make it pass.**

**You're not fighting the code. You're following the tests. The tests are the spec.**

