import { z } from 'zod';

// Auth schemas
export const loginSchema = z.object({
  email: z.string().email('Invalid email format'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

export const registerSchema = z
  .object({
    email: z.string().email('Invalid email format'),
    password: z.string().min(8, 'Password must be at least 8 characters'),
    passwordConfirm: z.string().min(8, 'Password confirmation must be at least 8 characters'),
  })
  .refine((data) => data.password === data.passwordConfirm, {
    message: 'Passwords do not match',
    path: ['passwordConfirm'],
  });

export const refreshTokenSchema = z.object({
  refreshToken: z.string().min(1, 'refreshToken is required'),
});

// Workout schemas
export const workoutSchema = z.object({
  exerciseId: z.string().uuid('Invalid exercise ID'),
  weight: z.number().positive('Weight must be positive'),
  reps: z.number().int().min(1).max(100, 'Reps must be between 1 and 100'),
  sets: z.number().int().positive().optional(),
  notes: z.string().max(500).optional(),
  loggedAt: z.string().datetime().optional(),
});

// Exercise schemas
export const exerciseSchema = z.object({
  name: z.string().min(1).max(100),
  category: z.string().min(1).max(50),
  muscleGroups: z.array(z.string()).min(1),
});

// Template schemas
export const templateSchema = z.object({
  name: z.string().min(1).max(100),
  exercises: z.array(
    z.object({
      exerciseId: z.string().uuid(),
      sets: z.number().int().positive(),
      targetReps: z.number().int().positive().optional(),
      targetWeight: z.number().positive().optional(),
    })
  ).min(1),
});

// Query schemas
export const workoutFiltersSchema = z.object({
  exerciseId: z.string().uuid().optional(),
  startDate: z.string().datetime().optional(),
  endDate: z.string().datetime().optional(),
  limit: z.number().int().positive().max(100).optional(),
  offset: z.number().int().nonnegative().optional(),
});

