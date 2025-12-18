# BACKEND DEVELOPER SPECIFICATION

## Mission

Implement backend API with strict adherence to **TDD (RED → GREEN → REFACTOR)**, using pre-designed test cases as your north star.

---

## Development Workflow

```
1. Read Test Case (Already written in spec)
   ├─ Understand inputs, outputs, edge cases
   └─ Run test → RED (fails)

2. Implement MINIMUM code to make test PASS
   ├─ Don't over-engineer
   └─ Run test → GREEN (passes)

3. REFACTOR code
   ├─ Extract functions, improve clarity
   ├─ Add error handling
   └─ Ensure test still PASSES

4. Move to next test
```

---

## Endpoints Priority

### Priority 1 (Week 1)

#### POST /api/auth/login
```typescript
// Input
{ email: string, password: string }

// Output (200)
{ token: string, user: { id, email } }

// Errors
400 — Invalid format
401 — Wrong password
```

#### POST /api/auth/register
```typescript
// Input
{ email: string, password: string, passwordConfirm: string }

// Validation
- Email format
- Password min 8 chars
- Passwords match

// Output (201)
{ token: string, user: { id, email } }
```

#### GET /api/exercises
```typescript
// Query
?search=присед&muscleGroup=legs

// Output (200)
[{ id, name, muscleGroup, category }]
```

### Priority 2 (Week 2)

#### POST /api/workouts
```typescript
// Input
{ 
  exerciseId: string,
  weight: number,     // > 0
  reps: number,       // 1-100
  sets?: number,      // 1-10
  rpe?: number,       // 1-10
  notes?: string
}

// Process
1. Validate with Zod schema
2. Save to DB
3. Update analytics aggregates

// Output (201)
{ id, exerciseId, weight, reps, date, createdAt }
```

#### GET /api/workouts
```typescript
// Query
?exerciseId=X&from=2024-12-01&to=2024-12-31&limit=100&offset=0

// Output (200)
{ 
  data: WorkoutLog[],
  total: number,
  hasMore: boolean
}
```

#### PATCH /api/workouts/:id
```typescript
// Input (partial)
{ weight?, reps?, notes? }

// Output (200)
{ ...updatedWorkout }
```

#### DELETE /api/workouts/:id
```typescript
// Process
1. Delete record
2. Update analytics aggregates

// Output (200)
{ success: true }
```

### Priority 3 (Week 3)

#### GET /api/analytics/progress
```typescript
// Query
?exerciseId=X&from=Y&to=Z&granularity=day

// Output (200)
{
  data: [{ date, maxWeight, avgWeight, totalVolume }],
  stats: { personalRecord, maxWeight, avgWeight, totalWorkouts }
}
```

#### GET /api/analytics/export
```typescript
// Query
?format=csv|json&from=X&to=Y

// Output
- CSV: File download
- JSON: Array of logs
```

---

## Code Patterns

### Controller

```typescript
// packages/backend/src/api/workouts/controller.ts
import { FastifyRequest, FastifyReply } from 'fastify';
import { WorkoutService } from '../../services/workout.service';
import { workoutSchema } from '@fitness/shared/schemas';

interface AuthRequest extends FastifyRequest {
  user?: { userId: string; email: string };
}

export class WorkoutController {
  private service = new WorkoutService();
  
  async create(req: AuthRequest, reply: FastifyReply) {
    try {
      const validated = workoutSchema.parse(req.body);
      const result = await this.service.createWorkout(
        req.user!.userId,
        validated
      );
      return reply.status(201).send(result);
    } catch (err: any) {
      if (err.name === 'ZodError') {
        return reply.status(400).send({ 
          error: 'Validation failed',
          details: err.errors 
        });
      }
      return reply.status(500).send({ error: err.message });
    }
  }
}
```

### Service

```typescript
// packages/backend/src/services/workout.service.ts
export class WorkoutService {
  private repo = new WorkoutRepository();
  private analytics = new AnalyticsService();
  
  async createWorkout(userId: string, data: WorkoutInput) {
    // Business validation
    if (data.weight <= 0) {
      throw new ValidationError('Weight must be positive');
    }
    
    // Create record
    const workout = await this.repo.create(userId, data);
    
    // Update aggregates
    await this.analytics.updateAggregates(userId, data.exerciseId);
    
    return workout;
  }
}
```

### Repository

```typescript
// packages/backend/src/repositories/workout.repository.ts
export class WorkoutRepository {
  private db = DatabaseManager.getInstance();
  
  async create(userId: string, data: WorkoutInput) {
    const id = crypto.randomUUID();
    
    this.db.prepare(`
      INSERT INTO workout_logs (id, user_id, exercise_id, weight, reps, sets, date)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `).run(id, userId, data.exerciseId, data.weight, data.reps, data.sets || 1, new Date().toISOString());
    
    return { id, ...data };
  }
  
  async find(userId: string, filters: WorkoutFilters) {
    let query = 'SELECT * FROM workout_logs WHERE user_id = ?';
    const params: any[] = [userId];
    
    if (filters.exerciseId) {
      query += ' AND exercise_id = ?';
      params.push(filters.exerciseId);
    }
    
    if (filters.from) {
      query += ' AND date >= ?';
      params.push(filters.from);
    }
    
    query += ' ORDER BY date DESC LIMIT ? OFFSET ?';
    params.push(filters.limit || 100, filters.offset || 0);
    
    return this.db.prepare(query).all(...params);
  }
}
```

---

## Testing Requirements

### Unit Tests

```typescript
describe('WorkoutService', () => {
  it('should reject negative weight', async () => {
    await expect(service.createWorkout('user1', { weight: -10, reps: 5 }))
      .rejects.toThrow('Weight must be positive');
  });
  
  it('should reject reps = 0', async () => {
    await expect(service.createWorkout('user1', { weight: 100, reps: 0 }))
      .rejects.toThrow('Reps must be between 1 and 100');
  });
  
  it('should accept valid data', async () => {
    const result = await service.createWorkout('user1', { weight: 100, reps: 5 });
    expect(result).toHaveProperty('id');
  });
});
```

### Integration Tests

```typescript
describe('POST /api/workouts', () => {
  it('should create with valid data', async () => {
    const res = await request(app)
      .post('/api/workouts')
      .set('Authorization', `Bearer ${token}`)
      .send({ exerciseId: 'ex1', weight: 100, reps: 5 });
    
    expect(res.status).toBe(201);
    expect(res.body).toHaveProperty('id');
  });
  
  it('should reject unauthenticated', async () => {
    const res = await request(app)
      .post('/api/workouts')
      .send({ exerciseId: 'ex1', weight: 100, reps: 5 });
    
    expect(res.status).toBe(401);
  });
});
```

---

## Code Quality Checklist

- [ ] All test cases pass
- [ ] Proper error handling (try-catch)
- [ ] Input validation (Zod schemas)
- [ ] Database transactions where needed
- [ ] Logging for debugging
- [ ] Query time < 100ms
- [ ] No SQL injection
- [ ] Comments for complex logic

---

## Common Pitfalls

❌ "I'll write tests after implementation"  
✅ Use tests as guide BEFORE

❌ "This function is too simple to test"  
✅ Test it anyway

❌ "Just make it work, refactor later"  
✅ Refactor immediately while fresh

❌ "I'll handle this edge case later"  
✅ Handle it now, test it

