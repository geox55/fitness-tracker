import { SupersetRepository } from '../repositories/superset.repository.js';
import { WorkoutSessionRepository } from '../repositories/workout-session.repository.js';
import type { Superset, SupersetInput } from '@fitness/shared';

export class SupersetService {
  private repo = new SupersetRepository();
  private sessionRepo = new WorkoutSessionRepository();

  /**
   * Creates a new superset in a workout session
   */
  async createSuperset(
    sessionId: string,
    userId: string,
    data: SupersetInput
  ): Promise<Superset> {
    // Validation
    if (data.exerciseIds.length < 2 || data.exerciseIds.length > 4) {
      throw new Error('Superset must contain 2-4 exercises');
    }

    if (!data.sets || data.sets.length === 0) {
      throw new Error('At least one set is required');
    }

    // Validate that session exists and belongs to user
    const session = await this.sessionRepo.findById(sessionId, userId);
    if (!session) {
      throw new Error('Workout session not found');
    }

    // Validate each set has data for all exercises
    for (const set of data.sets) {
      if (set.exercises.length !== data.exerciseIds.length) {
        throw new Error('Each set must have data for all exercises');
      }

      for (const exerciseData of set.exercises) {
        if (exerciseData.weight <= 0) {
          throw new Error('Weight must be positive');
        }
        if (exerciseData.reps < 1 || exerciseData.reps > 100) {
          throw new Error('Reps must be between 1 and 100');
        }
        if (exerciseData.rpe !== undefined && (exerciseData.rpe < 1 || exerciseData.rpe > 10)) {
          throw new Error('RPE must be between 1 and 10');
        }

        // Validate exercise ID is in the list
        if (!data.exerciseIds.includes(exerciseData.exerciseId)) {
          throw new Error('Exercise ID in set does not match superset exercise IDs');
        }
      }
    }

    return this.repo.create(sessionId, data);
  }

  /**
   * Gets a superset by ID
   */
  async getSupersetById(id: string): Promise<Superset | null> {
    return this.repo.findById(id);
  }
}
