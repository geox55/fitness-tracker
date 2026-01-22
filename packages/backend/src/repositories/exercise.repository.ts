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
  findAll(filters?: ExerciseFilters & { status?: string; userId?: string }): Exercise[] {
    try {
      let query = 'SELECT id, name, category, muscle_groups, created_by, status, approved_by, approved_at, created_at FROM exercises WHERE 1=1';
      const params: unknown[] = [];

      if (filters?.search) {
        query += ' AND LOWER(name) LIKE ?';
        params.push(`%${filters.search.toLowerCase()}%`);
      }

      if (filters?.status) {
        query += ' AND status = ?';
        params.push(filters.status);
      } else {
        // By default, show approved exercises OR user's own pending exercises
        if (filters?.userId) {
          query += ' AND (status = ? OR (status = ? AND created_by = ?))';
          params.push('approved', 'pending', filters.userId);
        } else {
          query += ' AND status = ?';
          params.push('approved');
        }
      }

      query += ' ORDER BY name ASC';

      const rows = this.db.prepare(query).all(...params) as Array<{
        id: string;
        name: string;
        category: string;
        muscle_groups: string;
        created_by: string | null;
        status: string;
        approved_by: string | null;
        approved_at: string | null;
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
    created_by: string | null;
    status: string;
    approved_by: string | null;
    approved_at: string | null;
    created_at: string;
  }): Exercise {
    // Parse muscle_groups JSON array
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
      createdBy: row.created_by || undefined,
      status: row.status as 'pending' | 'approved' | 'rejected',
      approvedBy: row.approved_by || undefined,
      approvedAt: row.approved_at || undefined,
      createdAt: row.created_at,
    };
  }

  /**
   * Creates a new exercise
   */
  async create(
    userId: string,
    data: { name: string; category: string; muscleGroups: string[] }
  ): Promise<Exercise> {
    const id = crypto.randomUUID();
    const now = new Date().toISOString();

    try {
      this.db
        .prepare(
          `INSERT INTO exercises (id, name, category, muscle_groups, created_by, status, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)`
        )
        .run(
          id,
          data.name,
          data.category,
          JSON.stringify(data.muscleGroups),
          userId,
          'pending',
          now
        );

      return this.findById(id)!;
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      throw new Error(`Database error: ${errorMessage}`);
    }
  }

  /**
   * Finds an exercise by ID
   */
  findById(id: string): Exercise | null {
    try {
      const row = this.db
        .prepare(
          `SELECT id, name, category, muscle_groups, created_by, status, approved_by, approved_at, created_at
           FROM exercises WHERE id = ?`
        )
        .get(id) as
        | {
            id: string;
            name: string;
            category: string;
            muscle_groups: string;
            created_by: string | null;
            status: string;
            approved_by: string | null;
            approved_at: string | null;
            created_at: string;
          }
        | undefined;

      if (!row) {
        return null;
      }

      return this.mapRowToExercise(row);
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      throw new Error(`Database error: ${errorMessage}`);
    }
  }

  /**
   * Approves an exercise
   */
  async approve(id: string, approvedBy: string): Promise<Exercise | null> {
    const now = new Date().toISOString();

    try {
      this.db
        .prepare(
          `UPDATE exercises SET status = ?, approved_by = ?, approved_at = ?
           WHERE id = ?`
        )
        .run('approved', approvedBy, now, id);

      return this.findById(id);
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      throw new Error(`Database error: ${errorMessage}`);
    }
  }
}

