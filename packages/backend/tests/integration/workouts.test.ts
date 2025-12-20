import { describe, it, expect, beforeAll, afterAll, beforeEach } from 'vitest';
import Fastify from 'fastify';
import workoutRoutes from '../../src/api/workouts/routes.js';
import authRoutes from '../../src/api/auth/routes.js';
import { DatabaseManager } from '../../src/db/database.js';

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
      FOREIGN KEY (user_id) REFERENCES users(id)
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
  });

  it('should create workout with valid data', async () => {
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
    const exerciseId = crypto.randomUUID();
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

