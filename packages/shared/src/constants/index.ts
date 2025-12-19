// API endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    REFRESH: '/api/auth/refresh',
  },
  WORKOUTS: '/api/workouts',
  EXERCISES: '/api/exercises',
  ANALYTICS: {
    PROGRESS: '/api/analytics/progress',
    EXPORT: '/api/analytics/export',
  },
  TEMPLATES: '/api/templates',
  HEALTH: '/api/health',
} as const;

// Exercise categories
export const EXERCISE_CATEGORIES = [
  'Strength',
  'Cardio',
  'Flexibility',
  'Balance',
  'Sports',
] as const;

// Muscle groups
export const MUSCLE_GROUPS = [
  'Chest',
  'Back',
  'Shoulders',
  'Arms',
  'Legs',
  'Core',
  'Full Body',
] as const;

// Default pagination
export const DEFAULT_PAGE_SIZE = 20;
export const MAX_PAGE_SIZE = 100;

// Chart limits
export const MAX_CHART_DATA_POINTS = 180; // ~6 months daily

// Validation limits
export const MIN_WEIGHT = 0.1;
export const MAX_WEIGHT = 1000;
export const MIN_REPS = 1;
export const MAX_REPS = 100;

