import { describe, it, expect, beforeEach, beforeAll, afterAll } from 'vitest';
import { WorkoutService } from '../../src/services/workout.service.js';
import { DatabaseManager } from '../../src/db/database.js';

function createTestUser(userId: string): void {
  const db = DatabaseManager.getInstance();
  const now = new Date().toISOString();
  db.prepare(
    `INSERT INTO users (id, email, password_hash, created_at, updated_at)
     VALUES (?, ?, ?, ?, ?)`
  ).run(userId, `test-${userId}@example.com`, 'hashed-password', now, now);
}

describe('WorkoutService', () => {
  let service: WorkoutService;

  beforeAll(async () => {
    // Run migrations before tests
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

  beforeEach(() => {
    service = new WorkoutService();
    // Clean up test data before each test
    const db = DatabaseManager.getInstance();
    db.prepare('DELETE FROM workout_logs').run();
    db.prepare('DELETE FROM users').run();
  });

  describe('createWorkout', () => {
    it('should reject negative weight', async () => {
      const userId = crypto.randomUUID();
      const exerciseId = crypto.randomUUID();
      const inputData = { exerciseId, weight: -10, reps: 5 };

      await expect(service.createWorkout(userId, inputData)).rejects.toThrow(
        'Weight must be positive'
      );
    });

    it('should reject zero weight', async () => {
      const userId = crypto.randomUUID();
      const exerciseId = crypto.randomUUID();
      const inputData = { exerciseId, weight: 0, reps: 5 };

      await expect(service.createWorkout(userId, inputData)).rejects.toThrow(
        'Weight must be positive'
      );
    });

    it('should reject reps less than 1', async () => {
      const userId = crypto.randomUUID();
      const exerciseId = crypto.randomUUID();
      const inputData = { exerciseId, weight: 100, reps: 0 };

      await expect(service.createWorkout(userId, inputData)).rejects.toThrow(
        'Reps must be between 1 and 100'
      );
    });

    it('should reject reps greater than 100', async () => {
      const userId = crypto.randomUUID();
      const exerciseId = crypto.randomUUID();
      const inputData = { exerciseId, weight: 100, reps: 101 };

      await expect(service.createWorkout(userId, inputData)).rejects.toThrow(
        'Reps must be between 1 and 100'
      );
    });

    it('should accept valid data', async () => {
      const userId = crypto.randomUUID();
      createTestUser(userId);
      const exerciseId = crypto.randomUUID();
      const inputData = { exerciseId, weight: 100, reps: 5 };

      const result = await service.createWorkout(userId, inputData);

      expect(result).toHaveProperty('id');
      expect(result.weight).toBe(100);
      expect(result.reps).toBe(5);
      expect(result.sets).toBe(1); // Default value
      expect(result.userId).toBe(userId);
      expect(result.exerciseId).toBe(exerciseId);
    });

    it('should accept valid data with all optional fields', async () => {
      const userId = crypto.randomUUID();
      createTestUser(userId);
      const exerciseId = crypto.randomUUID();
      const inputData = {
        exerciseId,
        weight: 150,
        reps: 8,
        sets: 3,
        notes: 'Felt strong today',
      };

      const result = await service.createWorkout(userId, inputData);

      expect(result).toHaveProperty('id');
      expect(result.weight).toBe(150);
      expect(result.reps).toBe(8);
      expect(result.sets).toBe(3);
      expect(result.notes).toBe('Felt strong today');
    });

    it('should set default sets to 1 if not provided', async () => {
      const userId = crypto.randomUUID();
      createTestUser(userId);
      const exerciseId = crypto.randomUUID();
      const inputData = { exerciseId, weight: 100, reps: 5 };

      const result = await service.createWorkout(userId, inputData);

      expect(result.sets).toBe(1);
    });
  });
});

