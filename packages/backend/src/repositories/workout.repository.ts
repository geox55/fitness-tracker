import { DatabaseManager } from '../db/database.js';
import type { WorkoutLog, WorkoutInput } from '@fitness/shared';

export class WorkoutRepository {
  private db = DatabaseManager.getInstance();

  /**
   * Creates a new workout log entry in the database
   * @param userId - User ID
   * @param data - Workout input data
   * @returns Created workout log
   * @throws {Error} If database operation fails
   */
  async create(userId: string, data: WorkoutInput): Promise<WorkoutLog> {
    const id = crypto.randomUUID();
    const now = new Date().toISOString();
    const loggedAt = data.loggedAt || now;
    const sets = data.sets || 1;

    try {
      this.db
        .prepare(
          `INSERT INTO workout_logs (id, user_id, exercise_id, weight, reps, sets, notes, logged_at, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
        )
        .run(
          id,
          userId,
          data.exerciseId,
          data.weight,
          data.reps,
          sets,
          data.notes || null,
          loggedAt,
          now,
          now
        );

      return {
        id,
        userId,
        exerciseId: data.exerciseId,
        weight: data.weight,
        reps: data.reps,
        sets,
        notes: data.notes,
        loggedAt,
        createdAt: now,
        updatedAt: now,
      };
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      throw new Error(`Database error: ${errorMessage}`);
    }
  }

  private mapRowToWorkout(row: {
    id: string;
    user_id: string;
    exercise_id: string;
    weight: number;
    reps: number;
    sets: number;
    notes: string | null;
    logged_at: string;
    created_at: string;
    updated_at: string;
  }): WorkoutLog {
    return {
      id: row.id,
      userId: row.user_id,
      exerciseId: row.exercise_id,
      weight: row.weight,
      reps: row.reps,
      sets: row.sets,
      notes: row.notes || undefined,
      loggedAt: row.logged_at,
      createdAt: row.created_at,
      updatedAt: row.updated_at,
    };
  }

  /**
   * Finds a workout by ID
   * @param id - Workout ID
   * @returns Workout if found, null otherwise
   * @throws {Error} If database is not initialized (not null on missing table)
   */
  async findById(id: string): Promise<WorkoutLog | null> {
    try {
      const row = this.db
        .prepare(
          `SELECT id, user_id, exercise_id, weight, reps, sets, notes, logged_at, created_at, updated_at
           FROM workout_logs WHERE id = ?`
        )
        .get(id) as
        | {
            id: string;
            user_id: string;
            exercise_id: string;
            weight: number;
            reps: number;
            sets: number;
            notes: string | null;
            logged_at: string;
            created_at: string;
            updated_at: string;
          }
        | undefined;

      if (!row) {
        return null;
      }

      return this.mapRowToWorkout(row);
    } catch (error: unknown) {
      if (
        error !== null &&
        typeof error === 'object' &&
        'message' in error &&
        typeof error.message === 'string' &&
        error.message.includes('no such table')
      ) {
        throw new Error('Database not initialized. Run migrations first.');
      }
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      throw new Error(`Database error: ${errorMessage}`);
    }
  }
}

