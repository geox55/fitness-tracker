import { DatabaseManager } from '../db/database.js';
import type { Superset, SupersetInput } from '@fitness/shared';

export class SupersetRepository {
  private db = DatabaseManager.getInstance();

  /**
   * Creates a new superset
   */
  async create(
    sessionId: string,
    data: SupersetInput
  ): Promise<Superset> {
    const supersetId = crypto.randomUUID();

    try {
      const transaction = this.db.transaction(() => {
        // Create superset
        this.db
          .prepare(
            `INSERT INTO supersets (id, session_id, exercise_ids_json, rest_time)
             VALUES (?, ?, ?, ?)`
          )
          .run(
            supersetId,
            sessionId,
            JSON.stringify(data.exerciseIds),
            data.restTime || null
          );

        // Create superset sets
        data.sets.forEach((set, setIndex) => {
          const setId = crypto.randomUUID();
          this.db
            .prepare(
              `INSERT INTO superset_sets (id, superset_id, set_number, sets_data_json)
               VALUES (?, ?, ?, ?)`
            )
            .run(
              setId,
              supersetId,
              setIndex + 1,
              JSON.stringify(set.exercises)
            );
        });

        // Create workout exercises for each exercise in superset
        data.exerciseIds.forEach((exerciseId, exerciseIndex) => {
          const workoutExerciseId = crypto.randomUUID();
          const exerciseName = this.getExerciseName(exerciseId);

          this.db
            .prepare(
              `INSERT INTO workout_exercises 
               (id, session_id, exercise_id, exercise_name, order_index, is_superset, superset_id, machine_settings_json, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`
            )
            .run(
              workoutExerciseId,
              sessionId,
              exerciseId,
              exerciseName,
              exerciseIndex,
              1, // is_superset
              supersetId,
              null, // machine_settings_json
              null // notes
            );
        });
      });

      transaction();

      const result = await this.findById(supersetId);
      if (!result) {
        throw new Error('Failed to create superset');
      }
      return result;
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      throw new Error(`Database error: ${errorMessage}`);
    }
  }

  /**
   * Finds a superset by ID
   */
  async findById(id: string): Promise<Superset | null> {
    try {
      const supersetRow = this.db
        .prepare(
          `SELECT id, session_id, exercise_ids_json, rest_time
           FROM supersets WHERE id = ?`
        )
        .get(id) as
        | {
            id: string;
            session_id: string;
            exercise_ids_json: string;
            rest_time: number | null;
          }
        | undefined;

      if (!supersetRow) {
        return null;
      }

      const exerciseIds = JSON.parse(supersetRow.exercise_ids_json) as string[];

      // Fetch sets
      const setRows = this.db
        .prepare(
          `SELECT set_number, sets_data_json
           FROM superset_sets WHERE superset_id = ? ORDER BY set_number`
        )
        .all(id) as Array<{
          set_number: number;
          sets_data_json: string;
        }>;

      const sets = setRows.map((row) => ({
        setNumber: row.set_number,
        exercises: JSON.parse(row.sets_data_json),
      }));

      return {
        id: supersetRow.id,
        exerciseIds,
        sets,
        restTime: supersetRow.rest_time || undefined,
      };
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
