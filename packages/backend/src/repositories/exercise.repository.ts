import { DatabaseManager } from '../db/database.js';
import type { Exercise } from '@fitness/shared';

export interface ExerciseFilters {
  search?: string;
  muscleGroup?: string;
}

export class ExerciseRepository {
  private db = DatabaseManager.getInstance();

  /**
   * Finds all exercises with optional filters
   * @param filters - Optional search and muscleGroup filters
   * @returns Array of exercises
   * @throws {Error} If database operation fails
   */
  findAll(filters?: ExerciseFilters): Exercise[] {
    try {
      let query = 'SELECT id, name, category, muscle_groups, created_at FROM exercises WHERE 1=1';
      const params: unknown[] = [];

      if (filters?.search) {
        query += ' AND LOWER(name) LIKE ?';
        params.push(`%${filters.search.toLowerCase()}%`);
      }

      query += ' ORDER BY name ASC';

      const rows = this.db.prepare(query).all(...params) as Array<{
        id: string;
        name: string;
        category: string;
        muscle_groups: string;
        created_at: string;
      }>;

      let exercises = rows.map((row) => this.mapRowToExercise(row));

      // Filter by muscleGroup in memory (since SQLite JSON functions may vary)
      if (filters?.muscleGroup) {
        const targetGroup = filters.muscleGroup.toLowerCase();
        exercises = exercises.filter((exercise) =>
          exercise.muscleGroups.some(
            (mg: string) => mg.toLowerCase() === targetGroup
          )
        );
      }

      return exercises;
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      throw new Error(`Database error: ${errorMessage}`);
    }
  }

  private mapRowToExercise(row: {
    id: string;
    name: string;
    category: string;
    muscle_groups: string;
    created_at: string;
  }): Exercise {
    // Parse muscle_groups JSON array and take first group for API compatibility
    let muscleGroups: string[] = [];
    try {
      muscleGroups = JSON.parse(row.muscle_groups);
    } catch {
      // If parsing fails, use empty array
      muscleGroups = [];
    }

    return {
      id: row.id,
      name: row.name,
      category: row.category,
      muscleGroups: muscleGroups,
      createdAt: row.created_at,
    };
  }
}

