import { ExerciseRepository } from '../repositories/exercise.repository.js';
import type { Exercise } from '@fitness/shared';

export interface ExerciseFilters {
  search?: string;
  muscleGroup?: string;
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
   * @param filters - Optional search and muscleGroup filters
   * @returns Array of exercises in API format
   */
  getExercises(filters?: ExerciseFilters): ExerciseApiResponse[] {
    const exercises = this.repo.findAll(filters);
    
    // Transform to API format: muscleGroups array -> muscleGroup string
    return exercises.map((exercise) => ({
      id: exercise.id,
      name: exercise.name,
      category: exercise.category,
      muscleGroup: exercise.muscleGroups.length > 0 ? exercise.muscleGroups[0] : '',
    }));
  }
}

