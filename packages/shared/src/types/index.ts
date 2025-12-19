// User types
export interface User {
  id: string;
  email: string;
  passwordHash: string;
  createdAt: string;
  updatedAt: string;
}

// Exercise types
export interface Exercise {
  id: string;
  name: string;
  category: string;
  muscleGroups: string[];
  createdAt: string;
}

// Workout types
export interface WorkoutLog {
  id: string;
  userId: string;
  exerciseId: string;
  weight: number;
  reps: number;
  sets: number;
  notes?: string;
  loggedAt: string;
  createdAt: string;
  updatedAt: string;
}

export interface WorkoutInput {
  exerciseId: string;
  weight: number;
  reps: number;
  sets?: number;
  notes?: string;
  loggedAt?: string;
}

export interface WorkoutFilters {
  exerciseId?: string;
  startDate?: string;
  endDate?: string;
  limit?: number;
  offset?: number;
}

// Analytics types
export interface ProgressData {
  date: string;
  weight: number;
  reps: number;
  volume: number;
}

export interface ProgressStats {
  maxWeight: number;
  avgWeight: number;
  maxReps: number;
  avgReps: number;
  totalVolume: number;
  personalRecord: boolean;
}

// Template types
export interface WorkoutTemplate {
  id: string;
  userId: string;
  name: string;
  exercises: TemplateExercise[];
  createdAt: string;
  updatedAt: string;
}

export interface TemplateExercise {
  exerciseId: string;
  sets: number;
  targetReps?: number;
  targetWeight?: number;
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface ApiError {
  error: string;
  details?: unknown;
  code?: string;
}

// Auth types
export interface LoginInput {
  email: string;
  password: string;
}

export interface RegisterInput {
  email: string;
  password: string;
  passwordConfirm: string;
}

export interface AuthResponse {
  token: string;
  user: {
    id: string;
    email: string;
  };
}

