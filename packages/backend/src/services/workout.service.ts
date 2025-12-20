import { WorkoutRepository } from '../repositories/workout.repository.js';
import type { WorkoutLog, WorkoutInput } from '@fitness/shared';
import { InvalidWeightError, InvalidRepsError } from '../errors/workout.errors.js';

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
}

