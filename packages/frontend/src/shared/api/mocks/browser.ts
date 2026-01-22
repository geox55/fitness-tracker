import { setupWorker } from 'msw/browser';

import { authHandlers } from './handlers/auth';
import { projectHandlers } from './handlers/project';

export const worker = setupWorker(...projectHandlers, ...authHandlers);
