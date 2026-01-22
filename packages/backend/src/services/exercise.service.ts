import { ExerciseRepository } from '../repositories/exercise.repository.js';
import type { Exercise, ExerciseInput } from '@fitness/shared';

export interface ExerciseFilters {
  search?: string;
  muscleGroup?: string;
  status?: string;
}

export interface ExerciseApiResponse {
  id: string;
  name: string;
  category: string;
  muscleGroup: string;
}

export class ExerciseService {
  private repo = new ExerciseRepository();

  /**
   * Gets exercises with optional filters
   * @param filters - Optional search, muscleGroup, and status filters
   * @param userId - Optional user ID to show their pending exercises
   * @returns Array of exercises in API format
   */
  getExercises(filters?: ExerciseFilters, userId?: string): ExerciseApiResponse[] {
    const exercises = this.repo.findAll({ ...filters, userId });
    
    // Transform to API format: muscleGroups array -> muscleGroup string
    return exercises.map((exercise) => ({
      id: exercise.id,
      name: exercise.name,
      category: exercise.category,
      muscleGroup: exercise.muscleGroups.length > 0 ? exercise.muscleGroups[0] : '',
    }));
  }

  /**
   * Creates a new exercise with pending status
   */
  async createExercise(userId: string, data: ExerciseInput): Promise<Exercise> {
    // Validation
    if (!data.name || data.name.trim().length === 0) {
      throw new Error('Exercise name is required');
    }
    if (!data.category || data.category.trim().length === 0) {
      throw new Error('Exercise category is required');
    }
    if (!data.muscleGroups || data.muscleGroups.length === 0) {
      throw new Error('At least one muscle group is required');
    }

    return this.repo.create(userId, data);
  }

  /**
   * Approves an exercise (admin only)
   */
  async approveExercise(id: string, approvedBy: string): Promise<Exercise> {
    const exercise = await this.repo.approve(id, approvedBy);
    if (!exercise) {
      throw new Error('Exercise not found');
    }
    return exercise;
  }

  /**
   * Gets an exercise by ID
   */
  getExerciseById(id: string): Exercise | null {
    return this.repo.findById(id);
  }
}

