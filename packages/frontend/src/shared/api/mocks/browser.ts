import { setupWorker } from 'msw/browser';

import { authHandlers } from './handlers/auth';
import { workoutHandlers } from './handlers/workouts';

export const worker = setupWorker(...authHandlers, ...workoutHandlers);
