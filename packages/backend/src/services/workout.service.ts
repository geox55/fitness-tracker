import { WorkoutRepository } from '../repositories/workout.repository.js';
import type { WorkoutLog, WorkoutInput } from '@fitness/shared';
import {
  InvalidWeightError,
  InvalidRepsError,
  InvalidSetsError,
  WorkoutNotFoundError,
  WorkoutAccessDeniedError,
} from '../errors/workout.errors.js';

export class WorkoutService {
  private repo = new WorkoutRepository();

  /**
   * Creates a new workout for a user
   * @param userId - User ID
   * @param data - Workout input data
   * @returns Created workout
   * @throws {InvalidWeightError} If weight is invalid
   * @throws {InvalidRepsError} If reps are invalid
   * @throws {Error} If database operation fails
   */
  async createWorkout(userId: string, data: WorkoutInput): Promise<WorkoutLog> {
    // Business validation
    if (data.weight <= 0) {
      throw new InvalidWeightError();
    }
    if (data.reps < 1 || data.reps > 100) {
      throw new InvalidRepsError();
    }

    return this.repo.create(userId, data);
  }

  /**
   * Gets workouts for a user with optional filters
   * @param userId - User ID
   * @param filters - Filter options
   * @returns Object with data, total, and hasMore flag
   * @throws {Error} If database operation fails
   */
  async getWorkouts(
    userId: string,
    filters: {
      exerciseId?: string;
      from?: string;
      to?: string;
      limit?: number;
      offset?: number;
    } = {}
  ): Promise<{ data: WorkoutLog[]; total: number; hasMore: boolean }> {
    const limit = filters.limit || 100;
    const { data, total } = await this.repo.findAll(userId, filters);
    const hasMore = (filters.offset || 0) + data.length < total;

    return {
      data,
      total,
      hasMore,
    };
  }

  /**
   * Updates a workout by ID
   * @param id - Workout ID
   * @param userId - User ID
   * @param data - Partial workout data to update
   * @returns Updated workout
   * @throws {InvalidWeightError} If weight is invalid
   * @throws {InvalidRepsError} If reps are invalid
   * @throws {InvalidSetsError} If sets are invalid
   * @throws {WorkoutNotFoundError} If workout not found
   * @throws {WorkoutAccessDeniedError} If workout not owned by user
   */
  async updateWorkout(
    id: string,
    userId: string,
    data: Partial<WorkoutInput>
  ): Promise<WorkoutLog> {
    // Business validation
    if (data.weight !== undefined && data.weight <= 0) {
      throw new InvalidWeightError();
    }
    if (data.reps !== undefined && (data.reps < 1 || data.reps > 100)) {
      throw new InvalidRepsError();
    }
    if (data.sets !== undefined && (data.sets < 1 || data.sets > 10)) {
      throw new InvalidSetsError();
    }

    const updated = await this.repo.update(id, userId, data);
    if (!updated) {
      // Check if workout exists but belongs to another user
      const existing = await this.repo.findById(id);
      if (!existing) {
        throw new WorkoutNotFoundError();
      }
      throw new WorkoutAccessDeniedError();
    }

    return updated;
  }

  /**
   * Deletes a workout by ID
   * @param id - Workout ID
   * @param userId - User ID
   * @throws {WorkoutNotFoundError} If workout not found
   * @throws {WorkoutAccessDeniedError} If workout not owned by user
   */
  async deleteWorkout(id: string, userId: string): Promise<void> {
    const deleted = await this.repo.delete(id, userId);
    if (!deleted) {
      // Check if workout exists but belongs to another user
      const existing = await this.repo.findById(id);
      if (!existing) {
        throw new WorkoutNotFoundError();
      }
      throw new WorkoutAccessDeniedError();
    }
  }
}

