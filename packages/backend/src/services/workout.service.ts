import { WorkoutRepository } from '../repositories/workout.repository.js';
import type { WorkoutLog, WorkoutInput } from '@fitness/shared';

export class WorkoutService {
  private repo = new WorkoutRepository();

  /**
   * Creates a new workout for a user
   * @param userId - User ID
   * @param data - Workout input data
   * @returns Created workout
   * @throws {Error} If validation fails or database operation fails
   */
  async createWorkout(userId: string, data: WorkoutInput): Promise<WorkoutLog> {
    // Business validation
    if (data.weight <= 0) {
      throw new Error('Weight must be positive');
    }
    if (data.reps < 1 || data.reps > 100) {
      throw new Error('Reps must be between 1 and 100');
    }

    return this.repo.create(userId, data);
  }
}

