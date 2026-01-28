import { delay, HttpResponse } from 'msw';

import type { ApiSchemas } from '../../schema';
import { http } from '../http';

const workouts: ApiSchemas['Workout'][] = [];

export const workoutHandlers = [
  http.get('/workouts', () => {
    return HttpResponse.json<ApiSchemas['WorkoutListResponse']>({
      items: workouts,
      total: workouts.length,
    });
  }),
  http.post('/workouts', async ({ request }) => {
    const body = (await request.json()) as ApiSchemas['CreateWorkoutRequest'];

    await delay(500);

    const workout: ApiSchemas['Workout'] = {
      id: crypto.randomUUID(),
      exerciseId: body.exerciseId,
      weight: body.weight,
      reps: body.reps,
      sets: body.sets ?? null,
      notes: body.notes ?? null,
      loggedAt: body.loggedAt ?? null,
      createdAt: new Date().toISOString(),
    };

    workouts.push(workout);

    return HttpResponse.json(workout, { status: 201 });
  }),
];

