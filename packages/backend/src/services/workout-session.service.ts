import { WorkoutSessionRepository } from '../repositories/workout-session.repository.js';
import type {
  WorkoutSession,
  WorkoutSessionInput,
} from '@fitness/shared';

export class WorkoutSessionService {
  private repo = new WorkoutSessionRepository();

  /**
   * Creates a new workout session
   */
  async createWorkoutSession(
    userId: string,
    data: WorkoutSessionInput
  ): Promise<WorkoutSession> {
    // Validation
    if (!data.loggedAt) {
      throw new Error('loggedAt is required');
    }

    if (!data.exercises || data.exercises.length === 0) {
      throw new Error('At least one exercise is required');
    }

    // Validate each exercise has at least one set
    for (const exercise of data.exercises) {
      if (!exercise.sets || exercise.sets.length === 0) {
        throw new Error('Each exercise must have at least one set');
      }

      // Validate sets
      for (const set of exercise.sets) {
        if (set.weight <= 0) {
          throw new Error('Weight must be positive');
        }
        if (set.reps < 1 || set.reps > 100) {
          throw new Error('Reps must be between 1 and 100');
        }
        if (set.rpe !== undefined && (set.rpe < 1 || set.rpe > 10)) {
          throw new Error('RPE must be between 1 and 10');
        }
      }

      // Validate warmup sets if present
      if (exercise.warmupSets) {
        for (const warmupSet of exercise.warmupSets) {
          if (warmupSet.weight <= 0) {
            throw new Error('Warmup weight must be positive');
          }
          if (warmupSet.reps < 1 || warmupSet.reps > 100) {
            throw new Error('Warmup reps must be between 1 and 100');
          }
        }
      }
    }

    return this.repo.create(userId, data);
  }

  /**
   * Gets workout sessions for a user with optional filters
   */
  async getWorkoutSessions(
    userId: string,
    filters: {
      from?: string;
      to?: string;
      limit?: number;
      offset?: number;
    } = {}
  ): Promise<{ data: WorkoutSession[]; total: number; hasMore: boolean }> {
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
   * Gets a workout session by ID
   */
  async getWorkoutSessionById(
    id: string,
    userId: string
  ): Promise<WorkoutSession | null> {
    return this.repo.findById(id, userId);
  }

  /**
   * Updates a workout session
   */
  async updateWorkoutSession(
    id: string,
    userId: string,
    data: Partial<{
      loggedAt?: string;
      duration?: number;
      notes?: string;
    }>
  ): Promise<WorkoutSession> {
    const updated = await this.repo.update(id, userId, data);
    if (!updated) {
      // Check if session exists
      const existing = await this.repo.findById(id, userId);
      if (!existing) {
        throw new Error('Workout session not found');
      }
      throw new Error('Failed to update workout session');
    }

    return updated;
  }

  /**
   * Deletes a workout session
   */
  async deleteWorkoutSession(id: string, userId: string): Promise<void> {
    const deleted = await this.repo.delete(id, userId);
    if (!deleted) {
      // Check if session exists
      const existing = await this.repo.findById(id, userId);
      if (!existing) {
        throw new Error('Workout session not found');
      }
      throw new Error('Failed to delete workout session');
    }
  }
}
