import { describe, it, expect, beforeAll, afterAll, beforeEach } from 'vitest';
import Fastify from 'fastify';
import workoutRoutes from '../../src/api/workouts/routes.js';
import authRoutes from '../../src/api/auth/routes.js';
import { DatabaseManager } from '../../src/db/database.js';
import { randomUUID } from 'crypto';

// Setup database before all tests
beforeAll(() => {
  const db = DatabaseManager.getInstance();
  const migrateSql = `
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS exercises (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      category TEXT NOT NULL,
      muscle_groups TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS workout_logs (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      exercise_id TEXT NOT NULL,
      weight REAL NOT NULL,
      reps INTEGER NOT NULL,
      sets INTEGER NOT NULL DEFAULT 1,
      notes TEXT,
      logged_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (user_id) REFERENCES users(id),
      FOREIGN KEY (exercise_id) REFERENCES exercises(id)
    );
  `;
  db.exec(migrateSql);
});

afterAll(() => {
  DatabaseManager.close();
});

async function getTestToken(app: ReturnType<typeof Fastify>): Promise<string> {
  const email = `test-${Date.now()}@example.com`;
  const password = 'password123';
  const registerResponse = await app.inject({
    method: 'POST',
    url: '/api/auth/register',
    payload: {
      email,
      password,
      passwordConfirm: password,
    },
  });
  const registerBody = JSON.parse(registerResponse.body);
  return registerBody.token;
}

async function getTestTokenAndUserId(
  app: ReturnType<typeof Fastify>
): Promise<{ token: string; userId: string }> {
  const email = `test-${Date.now()}@example.com`;
  const password = 'password123';
  const registerResponse = await app.inject({
    method: 'POST',
    url: '/api/auth/register',
    payload: {
      email,
      password,
      passwordConfirm: password,
    },
  });
  const registerBody = JSON.parse(registerResponse.body);
  return {
    token: registerBody.token,
    userId: registerBody.user.id,
  };
}

describe('POST /api/workouts', () => {
  let app: ReturnType<typeof Fastify>;
  let token: string;

  beforeAll(async () => {
    app = Fastify();
    await app.register(authRoutes, { prefix: '/api/auth' });
    await app.register(workoutRoutes, { prefix: '/api/workouts' });
    await app.ready();
    token = await getTestToken(app);
  });

  afterAll(async () => {
    await app.close();
  });

  beforeEach(() => {
    // Clean up test data before each test
    const db = DatabaseManager.getInstance();
    db.prepare('DELETE FROM workout_logs').run();
    db.prepare('DELETE FROM exercises').run();

    // Create a test exercise for foreign key constraint
    const exerciseId = randomUUID();
    db.prepare(`
      INSERT INTO exercises (id, name, category, muscle_groups)
      VALUES (?, ?, ?, ?)
    `).run(exerciseId, 'Test Exercise', 'Strength', JSON.stringify(['Legs']));
  });

  it('should create workout with valid data', async () => {
    // Get the exercise ID created in beforeEach
    const db = DatabaseManager.getInstance();
    const exercise = db.prepare('SELECT id FROM exercises LIMIT 1').get() as { id: string };
    const exerciseId = exercise.id;
    const response = await app.inject({
      method: 'POST',
      url: '/api/workouts',
      headers: {
        authorization: `Bearer ${token}`,
      },
      payload: {
        exerciseId,
        weight: 100,
        reps: 5,
      },
    });

    expect(response.statusCode).toBe(201);
    const body = JSON.parse(response.body);
    expect(body).toHaveProperty('id');
    expect(body.exerciseId).toBe(exerciseId);
    expect(body.weight).toBe(100);
    expect(body.reps).toBe(5);
    expect(body.sets).toBe(1); // Default value
  });

  it('should create workout with all optional fields', async () => {
    // Get the exercise ID created in beforeEach
    const db = DatabaseManager.getInstance();
    const exercise = db.prepare('SELECT id FROM exercises LIMIT 1').get() as { id: string };
    const exerciseId = exercise.id;
    const response = await app.inject({
      method: 'POST',
      url: '/api/workouts',
      headers: {
        authorization: `Bearer ${token}`,
      },
      payload: {
        exerciseId,
        weight: 150,
        reps: 8,
        sets: 3,
        notes: 'Felt strong today',
      },
    });

    expect(response.statusCode).toBe(201);
    const body = JSON.parse(response.body);
    expect(body.weight).toBe(150);
    expect(body.reps).toBe(8);
    expect(body.sets).toBe(3);
    expect(body.notes).toBe('Felt strong today');
  });

  it('should return 401 without auth header', async () => {
    const exerciseId = crypto.randomUUID();
    const response = await app.inject({
      method: 'POST',
      url: '/api/workouts',
      payload: {
        exerciseId,
        weight: 100,
        reps: 5,
      },
    });

    expect(response.statusCode).toBe(401);
    const body = JSON.parse(response.body);
    expect(body).toHaveProperty('error');
  });

  it('should return 400 for invalid exerciseId format', async () => {
    const response = await app.inject({
      method: 'POST',
      url: '/api/workouts',
      headers: {
        authorization: `Bearer ${token}`,
      },
      payload: {
        exerciseId: 'invalid-uuid',
        weight: 100,
        reps: 5,
      },
    });

    expect(response.statusCode).toBe(400);
    const body = JSON.parse(response.body);
    expect(body).toHaveProperty('error');
  });

  it('should return 400 for negative weight', async () => {
    const exerciseId = crypto.randomUUID();
    const response = await app.inject({
      method: 'POST',
      url: '/api/workouts',
      headers: {
        authorization: `Bearer ${token}`,
      },
      payload: {
        exerciseId,
        weight: -10,
        reps: 5,
      },
    });

    expect(response.statusCode).toBe(400);
    const body = JSON.parse(response.body);
    expect(body).toHaveProperty('error');
  });

  it('should return 400 for zero weight', async () => {
    const exerciseId = crypto.randomUUID();
    const response = await app.inject({
      method: 'POST',
      url: '/api/workouts',
      headers: {
        authorization: `Bearer ${token}`,
      },
      payload: {
        exerciseId,
        weight: 0,
        reps: 5,
      },
    });

    expect(response.statusCode).toBe(400);
    const body = JSON.parse(response.body);
    expect(body).toHaveProperty('error');
  });

  it('should return 400 for reps less than 1', async () => {
    const exerciseId = crypto.randomUUID();
    const response = await app.inject({
      method: 'POST',
      url: '/api/workouts',
      headers: {
        authorization: `Bearer ${token}`,
      },
      payload: {
        exerciseId,
        weight: 100,
        reps: 0,
      },
    });

    expect(response.statusCode).toBe(400);
    const body = JSON.parse(response.body);
    expect(body).toHaveProperty('error');
  });

  it('should return 400 for reps greater than 100', async () => {
    const exerciseId = crypto.randomUUID();
    const response = await app.inject({
      method: 'POST',
      url: '/api/workouts',
      headers: {
        authorization: `Bearer ${token}`,
      },
      payload: {
        exerciseId,
        weight: 100,
        reps: 101,
      },
    });

    expect(response.statusCode).toBe(400);
    const body = JSON.parse(response.body);
    expect(body).toHaveProperty('error');
  });

  it('should return 400 for missing exerciseId', async () => {
    const response = await app.inject({
      method: 'POST',
      url: '/api/workouts',
      headers: {
        authorization: `Bearer ${token}`,
      },
      payload: {
        weight: 100,
        reps: 5,
      },
    });

    expect(response.statusCode).toBe(400);
    const body = JSON.parse(response.body);
    expect(body).toHaveProperty('error');
  });

  it('should return 400 for missing weight', async () => {
    const exerciseId = crypto.randomUUID();
    const response = await app.inject({
      method: 'POST',
      url: '/api/workouts',
      headers: {
        authorization: `Bearer ${token}`,
      },
      payload: {
        exerciseId,
        reps: 5,
      },
    });

    expect(response.statusCode).toBe(400);
    const body = JSON.parse(response.body);
    expect(body).toHaveProperty('error');
  });

  it('should return 400 for missing reps', async () => {
    const exerciseId = crypto.randomUUID();
    const response = await app.inject({
      method: 'POST',
      url: '/api/workouts',
      headers: {
        authorization: `Bearer ${token}`,
      },
      payload: {
        exerciseId,
        weight: 100,
      },
    });

    expect(response.statusCode).toBe(400);
    const body = JSON.parse(response.body);
    expect(body).toHaveProperty('error');
  });
});

describe('GET /api/workouts', () => {
  let app: ReturnType<typeof Fastify>;
  let token: string;
  let userId: string;
  let exerciseId1: string;
  let exerciseId2: string;

  beforeAll(async () => {
    app = Fastify();
    await app.register(authRoutes, { prefix: '/api/auth' });
    await app.register(workoutRoutes, { prefix: '/api/workouts' });
    await app.ready();
    const authData = await getTestTokenAndUserId(app);
    token = authData.token;
    userId = authData.userId;
  });

  afterAll(async () => {
    await app.close();
  });

  beforeEach(() => {
    // Clean up test data
    const db = DatabaseManager.getInstance();
    db.prepare('DELETE FROM workout_logs').run();
    db.prepare('DELETE FROM exercises').run();

    // Create test exercises
    exerciseId1 = randomUUID();
    exerciseId2 = randomUUID();
    db.prepare(`
      INSERT INTO exercises (id, name, category, muscle_groups)
      VALUES (?, ?, ?, ?)
    `).run(exerciseId1, 'Squat', 'Strength', JSON.stringify(['Legs']));
    db.prepare(`
      INSERT INTO exercises (id, name, category, muscle_groups)
      VALUES (?, ?, ?, ?)
    `).run(exerciseId2, 'Bench Press', 'Strength', JSON.stringify(['Chest']));
  });

  it('should return empty list when user has no workouts', async () => {
    const response = await app.inject({
      method: 'GET',
      url: '/api/workouts',
      headers: {
        authorization: `Bearer ${token}`,
      },
    });

    expect(response.statusCode).toBe(200);
    const body = JSON.parse(response.body);
    expect(body.data).toEqual([]);
    expect(body.total).toBe(0);
    expect(body.hasMore).toBe(false);
  });

  it('should return list of user workouts', async () => {
    const db = DatabaseManager.getInstance();
    const now = new Date().toISOString();

    // Create test workouts
    const workout1Id = randomUUID();
    const workout2Id = randomUUID();
    db.prepare(`
      INSERT INTO workout_logs (id, user_id, exercise_id, weight, reps, sets, logged_at, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(workout1Id, userId, exerciseId1, 100, 5, 1, now, now, now);
    db.prepare(`
      INSERT INTO workout_logs (id, user_id, exercise_id, weight, reps, sets, logged_at, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(workout2Id, userId, exerciseId2, 80, 8, 3, now, now, now);

    const response = await app.inject({
      method: 'GET',
      url: '/api/workouts',
      headers: {
        authorization: `Bearer ${token}`,
      },
    });

    expect(response.statusCode).toBe(200);
    const body = JSON.parse(response.body);
    expect(body.data).toHaveLength(2);
    expect(body.total).toBe(2);
    expect(body.hasMore).toBe(false);
    expect(body.data[0]).toHaveProperty('id');
    expect(body.data[0]).toHaveProperty('exerciseId');
    expect(body.data[0]).toHaveProperty('weight');
    expect(body.data[0]).toHaveProperty('reps');
  });

  it('should filter by exerciseId', async () => {
    const db = DatabaseManager.getInstance();
    const now = new Date().toISOString();

    const workout1Id = randomUUID();
    const workout2Id = randomUUID();
    db.prepare(`
      INSERT INTO workout_logs (id, user_id, exercise_id, weight, reps, sets, logged_at, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(workout1Id, userId, exerciseId1, 100, 5, 1, now, now, now);
    db.prepare(`
      INSERT INTO workout_logs (id, user_id, exercise_id, weight, reps, sets, logged_at, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(workout2Id, userId, exerciseId2, 80, 8, 3, now, now, now);

    const response = await app.inject({
      method: 'GET',
      url: `/api/workouts?exerciseId=${exerciseId1}`,
      headers: {
        authorization: `Bearer ${token}`,
      },
    });

    expect(response.statusCode).toBe(200);
    const body = JSON.parse(response.body);
    expect(body.data).toHaveLength(1);
    expect(body.data[0].exerciseId).toBe(exerciseId1);
    expect(body.total).toBe(1);
  });

  it('should filter by date range (from)', async () => {
    const db = DatabaseManager.getInstance();
    const today = new Date().toISOString();
    const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();

    const workout1Id = randomUUID();
    const workout2Id = randomUUID();
    db.prepare(`
      INSERT INTO workout_logs (id, user_id, exercise_id, weight, reps, sets, logged_at, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(workout1Id, userId, exerciseId1, 100, 5, 1, today, today, today);
    db.prepare(`
      INSERT INTO workout_logs (id, user_id, exercise_id, weight, reps, sets, logged_at, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(workout2Id, userId, exerciseId2, 80, 8, 3, yesterday, yesterday, yesterday);

    const fromDate = new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString();
    const response = await app.inject({
      method: 'GET',
      url: `/api/workouts?from=${encodeURIComponent(fromDate)}`,
      headers: {
        authorization: `Bearer ${token}`,
      },
    });

    expect(response.statusCode).toBe(200);
    const body = JSON.parse(response.body);
    expect(body.data.length).toBeGreaterThanOrEqual(1);
    expect(body.data.every((w: any) => w.loggedAt >= fromDate)).toBe(true);
  });

  it('should filter by date range (to)', async () => {
    const db = DatabaseManager.getInstance();
    const today = new Date().toISOString();
    const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();

    const workout1Id = randomUUID();
    const workout2Id = randomUUID();
    db.prepare(`
      INSERT INTO workout_logs (id, user_id, exercise_id, weight, reps, sets, logged_at, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(workout1Id, userId, exerciseId1, 100, 5, 1, today, today, today);
    db.prepare(`
      INSERT INTO workout_logs (id, user_id, exercise_id, weight, reps, sets, logged_at, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(workout2Id, userId, exerciseId2, 80, 8, 3, yesterday, yesterday, yesterday);

    const toDate = new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString();
    const response = await app.inject({
      method: 'GET',
      url: `/api/workouts?to=${encodeURIComponent(toDate)}`,
      headers: {
        authorization: `Bearer ${token}`,
      },
    });

    expect(response.statusCode).toBe(200);
    const body = JSON.parse(response.body);
    expect(body.data.length).toBeGreaterThanOrEqual(1);
    expect(body.data.every((w: any) => w.loggedAt <= toDate)).toBe(true);
  });

  it('should support pagination with limit and offset', async () => {
    const db = DatabaseManager.getInstance();
    const now = new Date().toISOString();

    // Create 5 workouts
    for (let i = 0; i < 5; i++) {
      const workoutId = randomUUID();
      db.prepare(`
        INSERT INTO workout_logs (id, user_id, exercise_id, weight, reps, sets, logged_at, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
      `).run(workoutId, userId, exerciseId1, 100 + i, 5, 1, now, now, now);
    }

    const response = await app.inject({
      method: 'GET',
      url: '/api/workouts?limit=2&offset=0',
      headers: {
        authorization: `Bearer ${token}`,
      },
    });

    expect(response.statusCode).toBe(200);
    const body = JSON.parse(response.body);
    expect(body.data).toHaveLength(2);
    expect(body.total).toBe(5);
    expect(body.hasMore).toBe(true);
  });

  it('should return hasMore=false when no more results', async () => {
    const db = DatabaseManager.getInstance();
    const now = new Date().toISOString();

    // Create 3 workouts
    for (let i = 0; i < 3; i++) {
      const workoutId = randomUUID();
      db.prepare(`
        INSERT INTO workout_logs (id, user_id, exercise_id, weight, reps, sets, logged_at, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
      `).run(workoutId, userId, exerciseId1, 100 + i, 5, 1, now, now, now);
    }

    const response = await app.inject({
      method: 'GET',
      url: '/api/workouts?limit=10&offset=0',
      headers: {
        authorization: `Bearer ${token}`,
      },
    });

    expect(response.statusCode).toBe(200);
    const body = JSON.parse(response.body);
    expect(body.data).toHaveLength(3);
    expect(body.total).toBe(3);
    expect(body.hasMore).toBe(false);
  });

  it('should return 401 without auth header', async () => {
    const response = await app.inject({
      method: 'GET',
      url: '/api/workouts',
    });

    expect(response.statusCode).toBe(401);
    const body = JSON.parse(response.body);
    expect(body).toHaveProperty('error');
  });

  it('should not return workouts from other users', async () => {
    const db = DatabaseManager.getInstance();
    const now = new Date().toISOString();

    // Create another user
    const otherUserEmail = `other-${Date.now()}@example.com`;
    const registerResponse = await app.inject({
      method: 'POST',
      url: '/api/auth/register',
      payload: {
        email: otherUserEmail,
        password: 'password123',
        passwordConfirm: 'password123',
      },
    });
    const otherUserBody = JSON.parse(registerResponse.body);
    const otherUserId = otherUserBody.user.id;

    // Create workout for current user
    const workout1Id = randomUUID();
    db.prepare(`
      INSERT INTO workout_logs (id, user_id, exercise_id, weight, reps, sets, logged_at, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(workout1Id, userId, exerciseId1, 100, 5, 1, now, now, now);

    // Create workout for other user
    const workout2Id = randomUUID();
    db.prepare(`
      INSERT INTO workout_logs (id, user_id, exercise_id, weight, reps, sets, logged_at, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(workout2Id, otherUserId, exerciseId1, 200, 10, 1, now, now, now);

    const response = await app.inject({
      method: 'GET',
      url: '/api/workouts',
      headers: {
        authorization: `Bearer ${token}`,
      },
    });

    expect(response.statusCode).toBe(200);
    const body = JSON.parse(response.body);
    expect(body.data).toHaveLength(1);
    expect(body.data[0].userId).toBe(userId);
    expect(body.data[0].weight).toBe(100);
  });
});

describe('PATCH /api/workouts/:id', () => {
  let app: ReturnType<typeof Fastify>;
  let token: string;
  let userId: string;
  let exerciseId: string;
  let workoutId: string;

  beforeAll(async () => {
    app = Fastify();
    await app.register(authRoutes, { prefix: '/api/auth' });
    await app.register(workoutRoutes, { prefix: '/api/workouts' });
    await app.ready();
    const authData = await getTestTokenAndUserId(app);
    token = authData.token;
    userId = authData.userId;
  });

  afterAll(async () => {
    await app.close();
  });

  beforeEach(() => {
    const db = DatabaseManager.getInstance();
    db.prepare('DELETE FROM workout_logs').run();
    db.prepare('DELETE FROM exercises').run();

    exerciseId = randomUUID();
    db.prepare(`
      INSERT INTO exercises (id, name, category, muscle_groups)
      VALUES (?, ?, ?, ?)
    `).run(exerciseId, 'Squat', 'Strength', JSON.stringify(['Legs']));

    workoutId = randomUUID();
    const now = new Date().toISOString();
    db.prepare(`
      INSERT INTO workout_logs (id, user_id, exercise_id, weight, reps, sets, notes, logged_at, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(workoutId, userId, exerciseId, 100, 5, 1, 'Original notes', now, now, now);
  });

  it('should update workout with valid data', async () => {
    const response = await app.inject({
      method: 'PATCH',
      url: `/api/workouts/${workoutId}`,
      headers: {
        authorization: `Bearer ${token}`,
      },
      payload: {
        weight: 105,
        reps: 6,
      },
    });

    expect(response.statusCode).toBe(200);
    const body = JSON.parse(response.body);
    expect(body.weight).toBe(105);
    expect(body.reps).toBe(6);
    expect(body.sets).toBe(1); // Unchanged
    expect(body.notes).toBe('Original notes'); // Unchanged
  });

  it('should update only provided fields', async () => {
    const response = await app.inject({
      method: 'PATCH',
      url: `/api/workouts/${workoutId}`,
      headers: {
        authorization: `Bearer ${token}`,
      },
      payload: {
        notes: 'Updated notes',
      },
    });

    expect(response.statusCode).toBe(200);
    const body = JSON.parse(response.body);
    expect(body.weight).toBe(100); // Unchanged
    expect(body.reps).toBe(5); // Unchanged
    expect(body.notes).toBe('Updated notes');
  });

  it('should return 404 for non-existent workout', async () => {
    const nonExistentId = randomUUID();
    const response = await app.inject({
      method: 'PATCH',
      url: `/api/workouts/${nonExistentId}`,
      headers: {
        authorization: `Bearer ${token}`,
      },
      payload: {
        weight: 105,
      },
    });

    expect(response.statusCode).toBe(404);
    const body = JSON.parse(response.body);
    expect(body).toHaveProperty('error');
  });

  it('should return 403 for workout owned by another user', async () => {
    // Create another user
    const otherUserEmail = `other-${Date.now()}@example.com`;
    const registerResponse = await app.inject({
      method: 'POST',
      url: '/api/auth/register',
      payload: {
        email: otherUserEmail,
        password: 'password123',
        passwordConfirm: 'password123',
      },
    });
    const otherUserBody = JSON.parse(registerResponse.body);
    const otherUserId = otherUserBody.user.id;

    // Create workout for other user
    const db = DatabaseManager.getInstance();
    const otherWorkoutId = randomUUID();
    const now = new Date().toISOString();
    db.prepare(`
      INSERT INTO workout_logs (id, user_id, exercise_id, weight, reps, sets, logged_at, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(otherWorkoutId, otherUserId, exerciseId, 200, 10, 1, now, now, now);

    const response = await app.inject({
      method: 'PATCH',
      url: `/api/workouts/${otherWorkoutId}`,
      headers: {
        authorization: `Bearer ${token}`,
      },
      payload: {
        weight: 105,
      },
    });

    expect(response.statusCode).toBe(403);
    const body = JSON.parse(response.body);
    expect(body).toHaveProperty('error');
  });

  it('should return 400 for invalid weight', async () => {
    const response = await app.inject({
      method: 'PATCH',
      url: `/api/workouts/${workoutId}`,
      headers: {
        authorization: `Bearer ${token}`,
      },
      payload: {
        weight: -10,
      },
    });

    expect(response.statusCode).toBe(400);
    const body = JSON.parse(response.body);
    expect(body).toHaveProperty('error');
  });

  it('should return 400 for invalid reps', async () => {
    const response = await app.inject({
      method: 'PATCH',
      url: `/api/workouts/${workoutId}`,
      headers: {
        authorization: `Bearer ${token}`,
      },
      payload: {
        reps: 101,
      },
    });

    expect(response.statusCode).toBe(400);
    const body = JSON.parse(response.body);
    expect(body).toHaveProperty('error');
  });

  it('should return 401 without auth header', async () => {
    const response = await app.inject({
      method: 'PATCH',
      url: `/api/workouts/${workoutId}`,
      payload: {
        weight: 105,
      },
    });

    expect(response.statusCode).toBe(401);
    const body = JSON.parse(response.body);
    expect(body).toHaveProperty('error');
  });
});

describe('DELETE /api/workouts/:id', () => {
  let app: ReturnType<typeof Fastify>;
  let token: string;
  let userId: string;
  let exerciseId: string;
  let workoutId: string;

  beforeAll(async () => {
    app = Fastify();
    await app.register(authRoutes, { prefix: '/api/auth' });
    await app.register(workoutRoutes, { prefix: '/api/workouts' });
    await app.ready();
    const authData = await getTestTokenAndUserId(app);
    token = authData.token;
    userId = authData.userId;
  });

  afterAll(async () => {
    await app.close();
  });

  beforeEach(() => {
    const db = DatabaseManager.getInstance();
    db.prepare('DELETE FROM workout_logs').run();
    db.prepare('DELETE FROM exercises').run();

    exerciseId = randomUUID();
    db.prepare(`
      INSERT INTO exercises (id, name, category, muscle_groups)
      VALUES (?, ?, ?, ?)
    `).run(exerciseId, 'Squat', 'Strength', JSON.stringify(['Legs']));

    workoutId = randomUUID();
    const now = new Date().toISOString();
    db.prepare(`
      INSERT INTO workout_logs (id, user_id, exercise_id, weight, reps, sets, logged_at, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(workoutId, userId, exerciseId, 100, 5, 1, now, now, now);
  });

  it('should delete workout successfully', async () => {
    const response = await app.inject({
      method: 'DELETE',
      url: `/api/workouts/${workoutId}`,
      headers: {
        authorization: `Bearer ${token}`,
      },
    });

    expect(response.statusCode).toBe(200);
    const body = JSON.parse(response.body);
    expect(body.success).toBe(true);

    // Verify workout is deleted
    const db = DatabaseManager.getInstance();
    const deleted = db.prepare('SELECT * FROM workout_logs WHERE id = ?').get(workoutId);
    expect(deleted).toBeUndefined();
  });

  it('should return 404 for non-existent workout', async () => {
    const nonExistentId = randomUUID();
    const response = await app.inject({
      method: 'DELETE',
      url: `/api/workouts/${nonExistentId}`,
      headers: {
        authorization: `Bearer ${token}`,
      },
    });

    expect(response.statusCode).toBe(404);
    const body = JSON.parse(response.body);
    expect(body).toHaveProperty('error');
  });

  it('should return 403 for workout owned by another user', async () => {
    // Create another user
    const otherUserEmail = `other-${Date.now()}@example.com`;
    const registerResponse = await app.inject({
      method: 'POST',
      url: '/api/auth/register',
      payload: {
        email: otherUserEmail,
        password: 'password123',
        passwordConfirm: 'password123',
      },
    });
    const otherUserBody = JSON.parse(registerResponse.body);
    const otherUserId = otherUserBody.user.id;

    // Create workout for other user
    const db = DatabaseManager.getInstance();
    const otherWorkoutId = randomUUID();
    const now = new Date().toISOString();
    db.prepare(`
      INSERT INTO workout_logs (id, user_id, exercise_id, weight, reps, sets, logged_at, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(otherWorkoutId, otherUserId, exerciseId, 200, 10, 1, now, now, now);

    const response = await app.inject({
      method: 'DELETE',
      url: `/api/workouts/${otherWorkoutId}`,
      headers: {
        authorization: `Bearer ${token}`,
      },
    });

    expect(response.statusCode).toBe(403);
    const body = JSON.parse(response.body);
    expect(body).toHaveProperty('error');
  });

  it('should return 401 without auth header', async () => {
    const response = await app.inject({
      method: 'DELETE',
      url: `/api/workouts/${workoutId}`,
    });

    expect(response.statusCode).toBe(401);
    const body = JSON.parse(response.body);
    expect(body).toHaveProperty('error');
  });
});

