# QA ENGINEER SPECIFICATION

## Mission

Обеспечить качество приложения через систематическое тестирование на всех уровнях с фокусом на критичные функции.

---

## Test Strategy Overview

| Level | Scope | Tools | Coverage | Timeline |
|-------|-------|-------|----------|----------|
| **Unit** | Services, utils, components | Vitest | 90%+ | Parallel with dev |
| **Integration** | API + DB, Form + API | Vitest, Supertest | 95%+ | After unit |
| **E2E** | Full user workflows | Cypress | 80%+ | After integration |
| **Performance** | Load time, queries | Lighthouse, k6 | N/A | Pre-launch |
| **Security** | Auth, XSS, SQL injection | Manual, OWASP | Critical | Ongoing |

---

## Key Test Scenarios

### 1. Authentication & Authorization

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

### 2. Workout Logging

```
✓ User can add workout (all fields required)
✓ Invalid weight (negative, zero) → validation error
✓ Invalid reps (0, > 100) → validation error
✓ Workout is saved with current timestamp
✓ Offline mode queues workout locally
✓ When online, queued workout syncs automatically
```

### 3. Progress Analytics

```
✓ Chart loads with data for selected exercise
✓ Max weight calculation is correct
✓ Average weight calculation is correct
✓ PR is correctly identified with date
✓ Period filter (week/month/year) updates chart
✓ Chart is responsive on mobile
✓ No data → empty state message
```

### 4. API Contract

```
✓ POST /api/workouts returns 201 with workout data
✓ GET /api/workouts returns 200 with array
✓ GET /api/workouts?exerciseId=X filters correctly
✓ GET /api/workouts?from=X&to=Y respects date range
✓ Invalid query params → 400
✓ Missing auth header → 401
✓ Rate limit exceeded → 429
```

### 5. Database Integrity

```
✓ Foreign keys enforce referential integrity
✓ Indexes are used in WHERE clauses
✓ Aggregates are updated after new log
✓ Cascade delete works (user → logs)
✓ Concurrent writes don't corrupt data
```

---

## Test Case Template

```markdown
## Test Case: TC-001

**Module:** Workout Logging  
**Priority:** CRITICAL  
**Type:** E2E

### Preconditions
- User is logged in
- Browser cache is cleared

### Steps
1. Navigate to Dashboard
2. Click "New Workout"
3. Select exercise: "Squat"
4. Enter weight: "150"
5. Enter reps: "5"
6. Click "Add Set"

### Expected Result
- Workout is saved
- Success notification appears
- Workout appears in history

### Actual Result
_[Fill during execution]_

### Status
☐ PASS  ☐ FAIL  ☐ BLOCKED

### Notes
_[Any deviations]_
```

---

## Test Execution Plan

### Phase 1: Unit Tests (Week 1-2)

**Run on:** Every commit (pre-commit hook)  
**Target:** 90% coverage  
**Duration:** 5-10 min

**Focus:**
- Service layer validation
- Utility functions
- Component rendering
- State management

### Phase 2: Integration Tests (Week 2-3)

**Run on:** Daily push (CI)  
**Target:** 95% coverage  
**Duration:** 30 min

**Focus:**
- API endpoint responses
- Database operations
- Form → API flow
- Error handling

### Phase 3: E2E Tests (Week 3-4)

**Run on:** Pre-release  
**Target:** 80% critical paths  
**Duration:** 60 min

**Focus:**
- Complete user journeys
- Cross-browser (Chrome, Firefox, Safari)
- Mobile browsers
- Offline scenarios

### Phase 4: Regression (Each Release)

**Run on:** Before deployment  
**Duration:** 2 hours

**Focus:**
- All previous test cases
- Performance benchmarks
- Security checks

---

## Defect Management

### Severity Levels

| Severity | Definition | Example | Fix Time |
|----------|-----------|---------|----------|
| **Critical** | App crash, data loss, security | Login fails, data deleted | 4 hours |
| **High** | Core feature broken | Wrong chart calculation | 1 day |
| **Medium** | Feature partial, workaround exists | Filter doesn't work | 3 days |
| **Low** | Cosmetic, minor UX | Button color off | 1 week |

### Bug Report Template

```markdown
## Bug Report: BUG-001

**Title:** [Short description]

**Environment:**
- Browser: Chrome 120
- OS: macOS 14.2
- Screen: 1920x1080

**Steps to Reproduce:**
1. ...
2. ...
3. ...

**Expected:** [What should happen]

**Actual:** [What actually happens]

**Screenshots/Video:** [Attach]

**Severity:** HIGH

**Assigned:** [Developer name]
```

---

## Test Data & Fixtures

### Users

```typescript
export const testUsers = {
  valid: {
    email: 'test@example.com',
    password: 'SecurePass123!'
  },
  invalid: {
    email: 'invalid-email',
    password: '123' // too short
  }
};
```

### Exercises

```typescript
export const mockExercises = [
  { id: 'ex1', name: 'Squat', muscleGroup: 'legs' },
  { id: 'ex2', name: 'Bench Press', muscleGroup: 'chest' },
  { id: 'ex3', name: 'Deadlift', muscleGroup: 'back' }
];
```

### Workout Logs

```typescript
export const mockWorkoutLogs = [
  { id: 'log1', exerciseId: 'ex1', weight: 100, reps: 5, date: '2024-12-01' },
  { id: 'log2', exerciseId: 'ex1', weight: 105, reps: 5, date: '2024-12-05' },
  { id: 'log3', exerciseId: 'ex1', weight: 110, reps: 3, date: '2024-12-10' }
];
```

### Database Reset

```typescript
// Reset before each test
beforeEach(async () => {
  await db.exec('DELETE FROM workout_logs');
  await db.exec('DELETE FROM users');
  await seedTestData();
});
```

---

## E2E Test Examples

### Cypress: Complete Workout Flow

```typescript
describe('Workout Logging E2E', () => {
  beforeEach(() => {
    cy.login('test@example.com', 'password123');
    cy.visit('/dashboard');
  });
  
  it('should complete full workout flow', () => {
    // Open form
    cy.get('[data-testid="new-workout-btn"]').click();
    
    // Select exercise
    cy.get('[data-testid="exercise-select"]').type('Squat');
    cy.get('[data-testid="exercise-option-squat"]').click();
    
    // Enter data
    cy.get('[data-testid="weight-input"]').type('150');
    cy.get('[data-testid="reps-input"]').type('5');
    
    // Add set
    cy.get('[data-testid="add-set-btn"]').click();
    cy.get('[data-testid="set-list"]').should('contain', '150 kg x 5');
    
    // Complete
    cy.get('[data-testid="complete-workout-btn"]').click();
    cy.get('[data-testid="success-toast"]').should('be.visible');
    
    // Verify in history
    cy.visit('/history');
    cy.get('[data-testid="workout-card"]').first().should('contain', 'Squat');
    cy.get('[data-testid="workout-card"]').first().should('contain', '150');
  });
});
```

### Cypress: Offline Flow

```typescript
describe('Offline Support', () => {
  it('should queue workout when offline', () => {
    cy.login('test@example.com', 'password123');
    
    // Go offline
    cy.window().then((win) => {
      cy.stub(win.navigator, 'onLine').value(false);
    });
    
    cy.visit('/dashboard');
    
    // Add workout
    cy.get('[data-testid="new-workout-btn"]').click();
    cy.get('[data-testid="exercise-select"]').select('Squat');
    cy.get('[data-testid="weight-input"]').type('150');
    cy.get('[data-testid="reps-input"]').type('5');
    cy.get('[data-testid="add-set-btn"]').click();
    
    // Verify queued
    cy.get('[data-testid="sync-status"]').should('contain', 'Pending');
    
    // Go online
    cy.window().then((win) => {
      cy.stub(win.navigator, 'onLine').value(true);
    });
    
    // Verify synced
    cy.get('[data-testid="sync-status"]').should('contain', 'Synced');
  });
});
```

---

## Performance Benchmarks

| Metric | Target | Tool |
|--------|--------|------|
| API Response (p95) | < 200ms | k6 |
| First Contentful Paint | < 1.5s | Lighthouse |
| Largest Contentful Paint | < 2.5s | Lighthouse |
| Time to Interactive | < 3s | Lighthouse |
| Lighthouse Performance | > 90 | Lighthouse |

---

## Security Checklist

- [ ] JWT token validation
- [ ] Password hashing (bcrypt)
- [ ] Input sanitization
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] CORS configuration
- [ ] Rate limiting
- [ ] HTTPS enforcement
- [ ] Sensitive data encryption

