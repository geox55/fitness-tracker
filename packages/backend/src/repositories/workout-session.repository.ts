import { DatabaseManager } from '../db/database.js';
import type {
  WorkoutSession,
  WorkoutSessionInput,
  WorkoutExercise,
  ExerciseSet,
  WarmupSet,
} from '@fitness/shared';

export class WorkoutSessionRepository {
  private db = DatabaseManager.getInstance();

  /**
   * Creates a new workout session with exercises and sets
   */
  async create(
    userId: string,
    data: WorkoutSessionInput
  ): Promise<WorkoutSession> {
    const sessionId = crypto.randomUUID();
    const now = new Date().toISOString();

    try {
      // Start transaction
      const transaction = this.db.transaction(() => {
        // Create session
        this.db
          .prepare(
            `INSERT INTO workout_sessions (id, user_id, logged_at, duration, notes, created_at, updated_at)
             VALUES (?, ?, ?, ?, ?, ?, ?)`
          )
          .run(
            sessionId,
            userId,
            data.loggedAt,
            data.duration || null,
            data.notes || null,
            now,
            now
          );

        // Create exercises and sets
        data.exercises.forEach((exerciseInput, index) => {
          const exerciseId = crypto.randomUUID();
          const exerciseName = this.getExerciseName(exerciseInput.exerciseId);

          // Insert workout exercise
          this.db
            .prepare(
              `INSERT INTO workout_exercises 
               (id, session_id, exercise_id, exercise_name, order_index, is_superset, superset_id, machine_settings_json, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`
            )
            .run(
              exerciseId,
              sessionId,
              exerciseInput.exerciseId,
              exerciseName,
              index,
              0, // is_superset
              null, // superset_id
              exerciseInput.machineSettings
                ? JSON.stringify(exerciseInput.machineSettings)
                : null,
              exerciseInput.notes || null
            );

          // Insert working sets
          exerciseInput.sets.forEach((set, setIndex) => {
            const setId = crypto.randomUUID();
            this.db
              .prepare(
                `INSERT INTO exercise_sets 
                 (id, workout_exercise_id, set_number, weight, reps, rpe, rest_time, is_warmup)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)`
              )
              .run(
                setId,
                exerciseId,
                setIndex + 1,
                set.weight,
                set.reps,
                set.rpe || null,
                set.restTime || null,
                0 // is_warmup
              );
          });

          // Insert warmup sets if any
          if (exerciseInput.warmupSets) {
            exerciseInput.warmupSets.forEach((warmupSet, warmupIndex) => {
              const warmupId = crypto.randomUUID();
              this.db
                .prepare(
                  `INSERT INTO exercise_sets 
                   (id, workout_exercise_id, set_number, weight, reps, rpe, rest_time, is_warmup)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)`
                )
                .run(
                  warmupId,
                  exerciseId,
                  warmupIndex + 1,
                  warmupSet.weight,
                  warmupSet.reps,
                  null, // rpe
                  null, // rest_time
                  1 // is_warmup
                );
            });
          }
        });
      });

      transaction();

      // Fetch and return created session
      const result = await this.findById(sessionId, userId);
      if (!result) {
        throw new Error('Failed to create workout session');
      }
      return result;
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      throw new Error(`Database error: ${errorMessage}`);
    }
  }

  /**
   * Finds a workout session by ID
   */
  async findById(
    id: string,
    userId: string
  ): Promise<WorkoutSession | null> {
    try {
      const sessionRow = this.db
        .prepare(
          `SELECT id, user_id, logged_at, duration, notes, created_at, updated_at
           FROM workout_sessions WHERE id = ? AND user_id = ?`
        )
        .get(id, userId) as
        | {
            id: string;
            user_id: string;
            logged_at: string;
            duration: number | null;
            notes: string | null;
            created_at: string;
            updated_at: string;
          }
        | undefined;

      if (!sessionRow) {
        return null;
      }

      // Fetch exercises
      const exerciseRows = this.db
        .prepare(
          `SELECT id, exercise_id, exercise_name, order_index, is_superset, superset_id, machine_settings_json, notes
           FROM workout_exercises WHERE session_id = ? ORDER BY order_index`
        )
        .all(id) as Array<{
          id: string;
          exercise_id: string;
          exercise_name: string;
          order_index: number;
          is_superset: number;
          superset_id: string | null;
          machine_settings_json: string | null;
          notes: string | null;
        }>;

      const exercises: WorkoutExercise[] = [];

      for (const exerciseRow of exerciseRows) {
        // Fetch sets
        const setRows = this.db
          .prepare(
            `SELECT set_number, weight, reps, rpe, rest_time, is_warmup
             FROM exercise_sets WHERE workout_exercise_id = ? ORDER BY set_number`
          )
          .all(exerciseRow.id) as Array<{
            set_number: number;
            weight: number;
            reps: number;
            rpe: number | null;
            rest_time: number | null;
            is_warmup: number;
          }>;

        const sets: ExerciseSet[] = [];
        const warmupSets: WarmupSet[] = [];

        setRows.forEach((setRow) => {
          const setData = {
            setNumber: setRow.set_number,
            weight: setRow.weight,
            reps: setRow.reps,
            rpe: setRow.rpe || undefined,
            restTime: setRow.rest_time || undefined,
          };

          if (setRow.is_warmup === 1) {
            warmupSets.push(setData);
          } else {
            sets.push(setData);
          }
        });

        exercises.push({
          id: exerciseRow.id,
          exerciseId: exerciseRow.exercise_id,
          exerciseName: exerciseRow.exercise_name,
          order: exerciseRow.order_index,
          isSuperset: exerciseRow.is_superset === 1,
          supersetId: exerciseRow.superset_id || undefined,
          sets,
          warmupSets: warmupSets.length > 0 ? warmupSets : undefined,
          machineSettings: exerciseRow.machine_settings_json
            ? JSON.parse(exerciseRow.machine_settings_json)
            : undefined,
          notes: exerciseRow.notes || undefined,
        });
      }

      return {
        id: sessionRow.id,
        userId: sessionRow.user_id,
        loggedAt: sessionRow.logged_at,
        duration: sessionRow.duration || undefined,
        notes: sessionRow.notes || undefined,
        exercises,
        createdAt: sessionRow.created_at,
        updatedAt: sessionRow.updated_at,
      };
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      throw new Error(`Database error: ${errorMessage}`);
    }
  }

  /**
   * Lists workout sessions for a user with filters
   */
  async findAll(
    userId: string,
    filters: {
      from?: string;
      to?: string;
      limit?: number;
      offset?: number;
    } = {}
  ): Promise<{ data: WorkoutSession[]; total: number }> {
    try {
      let query = `SELECT id FROM workout_sessions WHERE user_id = ?`;
      const params: unknown[] = [userId];

      if (filters.from) {
        query += ' AND logged_at >= ?';
        params.push(filters.from);
      }

      if (filters.to) {
        query += ' AND logged_at <= ?';
        params.push(filters.to);
      }

      query += ' ORDER BY logged_at DESC';

      // Get total count
      const countQuery = query.replace('SELECT id', 'SELECT COUNT(*) as count');
      const countResult = this.db
        .prepare(countQuery)
        .get(...params) as { count: number };
      const total = countResult.count;

      // Apply pagination
      if (filters.limit) {
        query += ' LIMIT ?';
        params.push(filters.limit);
      }

      if (filters.offset) {
        query += ' OFFSET ?';
        params.push(filters.offset);
      }

      const rows = this.db.prepare(query).all(...params) as Array<{ id: string }>;

      const data: WorkoutSession[] = [];
      for (const row of rows) {
        const session = await this.findById(row.id, userId);
        if (session) {
          data.push(session);
        }
      }

      return { data, total };
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      throw new Error(`Database error: ${errorMessage}`);
    }
  }

  /**
   * Updates a workout session
   */
  async update(
    id: string,
    userId: string,
    data: Partial<{
      loggedAt?: string;
      duration?: number;
      notes?: string;
    }>
  ): Promise<WorkoutSession | null> {
    try {
      const now = new Date().toISOString();
      const updates: string[] = [];
      const params: unknown[] = [];

      if (data.loggedAt !== undefined) {
        updates.push('logged_at = ?');
        params.push(data.loggedAt);
      }

      if (data.duration !== undefined) {
        updates.push('duration = ?');
        params.push(data.duration);
      }

      if (data.notes !== undefined) {
        updates.push('notes = ?');
        params.push(data.notes);
      }

      if (updates.length === 0) {
        return this.findById(id, userId);
      }

      updates.push('updated_at = ?');
      params.push(now);
      params.push(id, userId);

      this.db
        .prepare(
          `UPDATE workout_sessions SET ${updates.join(', ')} 
           WHERE id = ? AND user_id = ?`
        )
        .run(...params);

      return this.findById(id, userId);
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      throw new Error(`Database error: ${errorMessage}`);
    }
  }

  /**
   * Deletes a workout session
   */
  async delete(id: string, userId: string): Promise<boolean> {
    try {
      const result = this.db
        .prepare(
          `DELETE FROM workout_sessions WHERE id = ? AND user_id = ?`
        )
        .run(id, userId);

      return result.changes > 0;
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      throw new Error(`Database error: ${errorMessage}`);
    }
  }

  /**
   * Helper to get exercise name by ID
   */
  private getExerciseName(exerciseId: string): string {
    const row = this.db
      .prepare('SELECT name FROM exercises WHERE id = ?')
      .get(exerciseId) as { name: string } | undefined;

    return row?.name || 'Unknown Exercise';
  }
}
