import z from 'zod';

export const workoutFormSchema = z.object({
  exerciseId: z.string().uuid('Неверный идентификатор упражнения'),
  weight: z
    .coerce
    .number()
    .positive('Вес должен быть больше нуля'),
  reps: z
    .coerce
    .number()
    .int()
    .min(1, 'Повторения должны быть не меньше 1')
    .max(100, 'Повторения должны быть не больше 100'),
  sets: z
    .coerce
    .number()
    .int()
    .min(1, 'Подходы должны быть не меньше 1')
    .max(10, 'Подходы должны быть не больше 10')
    .optional()
    .nullable(),
  notes: z
    .string()
    .max(500, 'Заметка не должна превышать 500 символов')
    .optional()
    .nullable(),
  loggedAt: z
    .string()
    .datetime('Неверный формат даты и времени')
    .optional()
    .nullable(),
});

export type WorkoutFormValues = z.infer<typeof workoutFormSchema>;

