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

  /**
   * Finds all workouts for a user with optional filters
   * @param userId - User ID
   * @param filters - Filter options (exerciseId, from, to, limit, offset)
   * @returns Object with data array and total count
   * @throws {Error} If database operation fails
   */
  async findAll(
    userId: string,
    filters: {
      exerciseId?: string;
      from?: string;
      to?: string;
      limit?: number;
      offset?: number;
    } = {}
  ): Promise<{ data: WorkoutLog[]; total: number }> {
    try {
      const limit = Math.min(filters.limit || 100, 1000);
      const offset = filters.offset || 0;

      // Build WHERE clause
      const conditions: string[] = ['user_id = ?'];
      const params: unknown[] = [userId];

      if (filters.exerciseId) {
        conditions.push('exercise_id = ?');
        params.push(filters.exerciseId);
      }

      if (filters.from) {
        conditions.push('logged_at >= ?');
        params.push(filters.from);
      }

      if (filters.to) {
        conditions.push('logged_at <= ?');
        params.push(filters.to);
      }

      const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';

      // Get total count
      const countQuery = `SELECT COUNT(*) as count FROM workout_logs ${whereClause}`;
      const countResult = this.db.prepare(countQuery).get(...params) as { count: number };
      const total = countResult.count;

      // Get data with pagination
      const dataQuery = `
        SELECT id, user_id, exercise_id, weight, reps, sets, notes, logged_at, created_at, updated_at
        FROM workout_logs
        ${whereClause}
        ORDER BY logged_at DESC, created_at DESC
        LIMIT ? OFFSET ?
      `;
      const rows = this.db.prepare(dataQuery).all(...params, limit, offset) as Array<{
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
      }>;

      return {
        data: rows.map((row) => this.mapRowToWorkout(row)),
        total,
      };
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      throw new Error(`Database error: ${errorMessage}`);
    }
  }

  /**
   * Updates a workout by ID (only if owned by userId)
   * @param id - Workout ID
   * @param userId - User ID (for ownership check)
   * @param data - Partial workout data to update
   * @returns Updated workout or null if not found or not owned
   * @throws {Error} If database operation fails
   */
  async update(
    id: string,
    userId: string,
    data: Partial<WorkoutInput>
  ): Promise<WorkoutLog | null> {
    try {
      // First check if workout exists and is owned by user
      const existing = await this.findById(id);
      if (!existing || existing.userId !== userId) {
        return null;
      }

      // Build UPDATE clause
      const updates: string[] = [];
      const params: unknown[] = [];

      if (data.weight !== undefined) {
        updates.push('weight = ?');
        params.push(data.weight);
      }

      if (data.reps !== undefined) {
        updates.push('reps = ?');
        params.push(data.reps);
      }

      if (data.sets !== undefined) {
        updates.push('sets = ?');
        params.push(data.sets);
      }

      if (data.notes !== undefined) {
        updates.push('notes = ?');
        params.push(data.notes || null);
      }

      if (data.loggedAt !== undefined) {
        updates.push('logged_at = ?');
        params.push(data.loggedAt);
      }

      if (updates.length === 0) {
        // No updates, return existing
        return existing;
      }

      // Always update updated_at
      updates.push('updated_at = ?');
      params.push(new Date().toISOString());

      params.push(id, userId);

      const updateQuery = `
        UPDATE workout_logs
        SET ${updates.join(', ')}
        WHERE id = ? AND user_id = ?
      `;

      this.db.prepare(updateQuery).run(...params);

      // Return updated workout
      return this.findById(id);
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      throw new Error(`Database error: ${errorMessage}`);
    }
  }

  /**
   * Deletes a workout by ID (only if owned by userId)
   * @param id - Workout ID
   * @param userId - User ID (for ownership check)
   * @returns true if deleted, false if not found or not owned
   * @throws {Error} If database operation fails
   */
  async delete(id: string, userId: string): Promise<boolean> {
    try {
      // First check if workout exists and is owned by user
      const existing = await this.findById(id);
      if (!existing || existing.userId !== userId) {
        return false;
      }

      const deleteQuery = 'DELETE FROM workout_logs WHERE id = ? AND user_id = ?';
      const result = this.db.prepare(deleteQuery).run(id, userId);

      return result.changes > 0;
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      throw new Error(`Database error: ${errorMessage}`);
    }
  }
}

