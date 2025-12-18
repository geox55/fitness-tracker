# TESTING STRATEGY

## 🔴 КРИТИЧЕСКОЕ ТРЕБОВАНИЕ

**Тесты проектируются ПОСЛЕ архитектуры, но ДО начала разработки кода.**  
**Разработчики начинают с RED → GREEN → REFACTOR.**

---

## Test Pyramid

```
        /\
       /  \      E2E Tests (Cypress)
      /----\     - 10% — Critical user flows
     /      \
    /--------\   Integration Tests
   /          \  - 30% — API + DB, Form + API
  /------------\
 /              \ Unit Tests
/________________\ - 60% — Services, Utils, Components
```

---

## Coverage Targets

| Component | Unit | Integration | E2E | Target |
|-----------|------|-------------|-----|--------|
| WorkoutService | ✅ | ✅ | - | 90% |
| WorkoutRepository | ✅ | ✅ | - | 85% |
| AnalyticsService | ✅ | ✅ | - | 90% |
| WorkoutForm | ✅ | ✅ | ✅ | 85% |
| ProgressChart | ✅ | ✅ | ✅ | 80% |
| API Endpoints | - | ✅ | ✅ | 95% |

---

## Backend Unit Tests

### Workout Service Validation

```gherkin
Feature: Workout Log Validation

  Scenario: Reject negative weight
    Given a workout log with weight = -10
    When attempting to create the log
    Then return error "Weight must be positive"
    
  Scenario: Reject invalid reps
    Given a workout log with reps = 0
    When attempting to create the log
    Then return error "Reps must be between 1 and 100"
    
  Scenario: Accept valid data
    Given a workout log with weight = 100 and reps = 5
    When attempting to create the log
    Then the log is created successfully
```

```typescript
// packages/backend/tests/unit/workout.service.test.ts
describe('WorkoutService', () => {
  let service: WorkoutService;
  
  beforeEach(() => {
    service = new WorkoutService();
  });
  
  describe('createWorkout', () => {
    it('should reject negative weight', async () => {
      const log = { exerciseId: 'ex1', weight: -10, reps: 5 };
      
      await expect(service.createWorkout('user1', log))
        .rejects.toThrow('Weight must be positive');
    });
    
    it('should reject reps = 0', async () => {
      const log = { exerciseId: 'ex1', weight: 100, reps: 0 };
      
      await expect(service.createWorkout('user1', log))
        .rejects.toThrow('Reps must be between 1 and 100');
    });
    
    it('should accept valid data', async () => {
      const log = { exerciseId: 'ex1', weight: 100, reps: 5 };
      
      const result = await service.createWorkout('user1', log);
      expect(result).toHaveProperty('id');
      expect(result.weight).toBe(100);
    });
  });
});
```

### Analytics Calculation

```gherkin
Feature: Progress Calculation

  Scenario: Calculate max weight
    Given workout logs: 100kg, 95kg, 110kg, 100kg
    When fetching max weight
    Then return 110kg
    
  Scenario: Calculate average weight
    Given workout logs: 100kg x 4
    When fetching average weight
    Then return 100kg
    
  Scenario: Identify personal record
    Given logs: 100kg (12-01), 110kg (12-05), 105kg (12-10)
    When fetching PR
    Then return { weight: 110kg, date: 2024-12-05 }
```

```typescript
describe('AnalyticsService', () => {
  it('should calculate max weight correctly', () => {
    const logs = [
      { weight: 100 }, { weight: 95 },
      { weight: 110 }, { weight: 100 }
    ];
    
    const max = service.calculateMaxWeight(logs);
    expect(max).toBe(110);
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

---

## Backend Integration Tests

### POST /api/workouts

```gherkin
Feature: Create Workout Endpoint

  Scenario: Successfully create workout
    Given user is authenticated
    And request body: { exerciseId, weight: 100, reps: 5 }
    When POSTing to /api/workouts
    Then response status = 201
    And response includes id, weight, date
    
  Scenario: Reject missing required field
    Given request body missing reps
    When POSTing to /api/workouts
    Then response status = 400
    
  Scenario: Reject unauthenticated request
    Given no auth header
    When POSTing to /api/workouts
    Then response status = 401
```

```typescript
describe('POST /api/workouts', () => {
  it('should create workout with valid data', async () => {
    const res = await request(app)
      .post('/api/workouts')
      .set('Authorization', `Bearer ${token}`)
      .send({ exerciseId: 'ex1', weight: 100, reps: 5 });
    
    expect(res.status).toBe(201);
    expect(res.body).toHaveProperty('id');
    expect(res.body.weight).toBe(100);
  });
  
  it('should reject missing reps field', async () => {
    const res = await request(app)
      .post('/api/workouts')
      .set('Authorization', `Bearer ${token}`)
      .send({ exerciseId: 'ex1', weight: 100 });
    
    expect(res.status).toBe(400);
    expect(res.body.error).toContain('reps');
  });
  
  it('should reject unauthenticated request', async () => {
    const res = await request(app)
      .post('/api/workouts')
      .send({ exerciseId: 'ex1', weight: 100, reps: 5 });
    
    expect(res.status).toBe(401);
  });
});
```

### GET /api/workouts (Filtering)

```typescript
describe('GET /api/workouts', () => {
  beforeEach(() => {
    // Seed test data
  });
  
  it('should filter by exerciseId', async () => {
    const res = await request(app)
      .get('/api/workouts?exerciseId=ex1')
      .set('Authorization', `Bearer ${token}`);
    
    expect(res.status).toBe(200);
    expect(res.body.data).toHaveLength(3);
    expect(res.body.data.every(l => l.exerciseId === 'ex1')).toBe(true);
  });
  
  it('should filter by date range', async () => {
    const res = await request(app)
      .get('/api/workouts?from=2024-12-05&to=2024-12-10')
      .set('Authorization', `Bearer ${token}`);
    
    expect(res.body.data).toHaveLength(2);
  });
});
```

---

## Frontend Unit Tests

### Form Validation

```gherkin
Feature: Workout Form Validation

  Scenario: Reject empty weight
    Given weight input is empty
    When submitting form
    Then show error "Weight is required"
    
  Scenario: Reject non-numeric weight
    Given weight input = "abc"
    When validating
    Then show error "Weight must be a number"
```

```typescript
// packages/frontend/tests/components/WorkoutForm.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { WorkoutForm } from '@/features/workout-logging';

describe('WorkoutForm Validation', () => {
  it('should reject empty weight', async () => {
    render(<WorkoutForm />);
    
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
    const onSubmit = vi.fn();
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

---

## E2E Tests (Cypress)

### Full Workout Flow

```gherkin
Feature: End-to-End Workout Tracking

  Scenario: Complete workout logging flow
    Given user is logged in
    When user clicks "New Workout"
    And selects "Squat" exercise
    And enters weight "150 kg"
    And enters "5" reps
    And clicks "Add Set"
    Then new set appears in list
    
    When user completes workout
    And views progress page
    Then chart shows 150 kg data point
```

```typescript
// e2e/cypress/e2e/workout-logging.cy.ts
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

## Test Fixtures

```typescript
// tests/fixtures.ts
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

export const mockUser = {
  id: 'user1',
  email: 'test@example.com',
  token: 'valid-jwt-token'
};
```

---

## Test Execution Schedule

| Phase | Trigger | Target | Duration |
|-------|---------|--------|----------|
| Unit Tests | Every commit | 90% pass | 5-10 min |
| Integration | Daily push | 95% pass | 30 min |
| E2E | Pre-release | 80% critical | 60 min |
| Regression | Each release | All pass | 2 hours |

---

## Defect Severity

| Severity | Definition | Example | Fix Time |
|----------|-----------|---------|----------|
| **Critical** | App crash, data loss | Login fails | 4 hours |
| **High** | Core feature broken | Wrong chart data | 1 day |
| **Medium** | Partial break, workaround exists | Filter bug | 3 days |
| **Low** | Cosmetic issue | Wrong color | 1 week |

