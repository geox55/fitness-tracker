import { describe, it, expect, beforeAll, afterAll, beforeEach } from 'vitest';
import Fastify from 'fastify';
import exerciseRoutes from '../../src/api/exercises/routes.js';
import { DatabaseManager } from '../../src/db/database.js';
import { randomUUID } from 'crypto';

// Setup database before all tests
beforeAll(() => {
  const db = DatabaseManager.getInstance();
  const migrateSql = `
    CREATE TABLE IF NOT EXISTS exercises (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      category TEXT NOT NULL,
      muscle_groups TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_exercises_name ON exercises(name);
  `;
  db.exec(migrateSql);
});

afterAll(() => {
  DatabaseManager.close();
});

describe('GET /api/exercises', () => {
  let app: ReturnType<typeof Fastify>;

  beforeAll(async () => {
    app = Fastify();
    await app.register(exerciseRoutes, { prefix: '/api/exercises' });
    await app.ready();
  });

  afterAll(async () => {
    await app.close();
  });

  beforeEach(() => {
    // Clean up and seed test data before each test
    const db = DatabaseManager.getInstance();
    db.prepare('DELETE FROM exercises').run();

    // Seed test exercises
    const exercises = [
      {
        id: randomUUID(),
        name: 'Squat',
        category: 'Strength',
        muscleGroups: JSON.stringify(['Legs', 'Core']),
      },
      {
        id: randomUUID(),
        name: 'Bench Press',
        category: 'Strength',
        muscleGroups: JSON.stringify(['Chest', 'Arms']),
      },
      {
        id: randomUUID(),
        name: 'Deadlift',
        category: 'Strength',
        muscleGroups: JSON.stringify(['Back', 'Legs']),
      },
      {
        id: randomUUID(),
        name: 'Overhead Press',
        category: 'Strength',
        muscleGroups: JSON.stringify(['Shoulders', 'Arms']),
      },
      {
        id: randomUUID(),
        name: 'Pull-ups',
        category: 'Strength',
        muscleGroups: JSON.stringify(['Back', 'Arms']),
      },
      {
        id: randomUUID(),
        name: 'Leg Press',
        category: 'Strength',
        muscleGroups: JSON.stringify(['Legs']),
      },
    ];

    const insertExercise = db.prepare(`
      INSERT INTO exercises (id, name, category, muscle_groups)
      VALUES (?, ?, ?, ?)
    `);

    exercises.forEach((exercise) => {
      insertExercise.run(
        exercise.id,
        exercise.name,
        exercise.category,
        exercise.muscleGroups
      );
    });
  });

  it('should return all exercises when no filters provided', async () => {
    const response = await app.inject({
      method: 'GET',
      url: '/api/exercises',
    });

    expect(response.statusCode).toBe(200);
    const body = JSON.parse(response.body);
    expect(Array.isArray(body)).toBe(true);
    expect(body.length).toBe(6);
    expect(body[0]).toHaveProperty('id');
    expect(body[0]).toHaveProperty('name');
    expect(body[0]).toHaveProperty('category');
    expect(body[0]).toHaveProperty('muscleGroup');
  });

  it('should filter exercises by search term (case-insensitive partial match)', async () => {
    const response = await app.inject({
      method: 'GET',
      url: '/api/exercises?search=squat',
    });

    expect(response.statusCode).toBe(200);
    const body = JSON.parse(response.body);
    expect(Array.isArray(body)).toBe(true);
    expect(body.length).toBe(1);
    expect(body[0].name).toBe('Squat');
  });

  it('should filter exercises by search term (case-insensitive)', async () => {
    const response = await app.inject({
      method: 'GET',
      url: '/api/exercises?search=SQUAT',
    });

    expect(response.statusCode).toBe(200);
    const body = JSON.parse(response.body);
    expect(Array.isArray(body)).toBe(true);
    expect(body.length).toBe(1);
    expect(body[0].name).toBe('Squat');
  });

  it('should filter exercises by partial search term', async () => {
    const response = await app.inject({
      method: 'GET',
      url: '/api/exercises?search=press',
    });

    expect(response.statusCode).toBe(200);
    const body = JSON.parse(response.body);
    expect(Array.isArray(body)).toBe(true);
    expect(body.length).toBe(3);
    expect(body.map((e: { name: string }) => e.name)).toContain('Bench Press');
    expect(body.map((e: { name: string }) => e.name)).toContain('Overhead Press');
    expect(body.map((e: { name: string }) => e.name)).toContain('Leg Press');
  });

  it('should filter exercises by muscleGroup', async () => {
    const response = await app.inject({
      method: 'GET',
      url: '/api/exercises?muscleGroup=Legs',
    });

    expect(response.statusCode).toBe(200);
    const body = JSON.parse(response.body);
    expect(Array.isArray(body)).toBe(true);
    expect(body.length).toBeGreaterThan(0);
    // Should include Squat, Deadlift, and Leg Press (all have Legs)
    const names = body.map((e: { name: string }) => e.name);
    expect(names).toContain('Squat');
    expect(names).toContain('Deadlift');
    expect(names).toContain('Leg Press');
  });

  it('should combine search and muscleGroup filters', async () => {
    const response = await app.inject({
      method: 'GET',
      url: '/api/exercises?search=press&muscleGroup=Arms',
    });

    expect(response.statusCode).toBe(200);
    const body = JSON.parse(response.body);
    expect(Array.isArray(body)).toBe(true);
    expect(body.length).toBe(2);
    const names = body.map((e: { name: string }) => e.name);
    expect(names).toContain('Bench Press');
    expect(names).toContain('Overhead Press');
  });

  it('should return empty array when no matches found', async () => {
    const response = await app.inject({
      method: 'GET',
      url: '/api/exercises?search=nonexistent',
    });

    expect(response.statusCode).toBe(200);
    const body = JSON.parse(response.body);
    expect(Array.isArray(body)).toBe(true);
    expect(body.length).toBe(0);
  });

  it('should return empty array when muscleGroup filter has no matches', async () => {
    const response = await app.inject({
      method: 'GET',
      url: '/api/exercises?muscleGroup=Abs',
    });

    expect(response.statusCode).toBe(200);
    const body = JSON.parse(response.body);
    expect(Array.isArray(body)).toBe(true);
    expect(body.length).toBe(0);
  });

  it('should handle special characters in search term', async () => {
    const response = await app.inject({
      method: 'GET',
      url: '/api/exercises?search=overhead%20press',
    });

    expect(response.statusCode).toBe(200);
    const body = JSON.parse(response.body);
    expect(Array.isArray(body)).toBe(true);
    expect(body.length).toBe(1);
    expect(body[0].name).toBe('Overhead Press');
  });
});

