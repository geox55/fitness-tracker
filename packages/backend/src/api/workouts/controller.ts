import type { FastifyRequest, FastifyReply } from 'fastify';
import { ZodError } from 'zod';
import { WorkoutService } from '../../services/workout.service.js';
import { workoutSchema } from '@fitness/shared';
import { authMiddleware, type AuthRequest } from '../../middleware/auth.middleware.js';

interface ErrorWithName extends Error {
  name: string;
}

function isZodError(err: unknown): err is ZodError {
  return (
    err instanceof ZodError ||
    (err !== null &&
      typeof err === 'object' &&
      'name' in err &&
      (err as ErrorWithName).name === 'ZodError')
  );
}

function sanitizeErrorForLogging(err: unknown): {
  error: string;
  stack?: string;
  name: string;
} {
  if (err instanceof Error) {
    return {
      error: err.message,
      stack: process.env.NODE_ENV === 'development' ? err.stack : undefined,
      name: err.name,
    };
  }
  return {
    error: String(err),
    name: 'UnknownError',
  };
}

export class WorkoutController {
  private service = new WorkoutService();

  /**
   * Creates a new workout
   * @param req - Fastify request with workout data
   * @param reply - Fastify reply
   * @returns 201 with workout data on success, 400/500 on error
   */
  async create(req: AuthRequest, reply: FastifyReply) {
    try {
      const validated = workoutSchema.parse(req.body || {});
      const result = await this.service.createWorkout(
        req.user!.userId,
        validated
      );
      return reply.status(201).send(result);
    } catch (err) {
      if (isZodError(err)) {
        return reply.status(400).send({
          error: 'Validation failed',
          details: err.errors,
        });
      }
      if (err instanceof Error && err.message.includes('must be')) {
        return reply.status(400).send({
          error: err.message,
        });
      }
      req.log.error(
        sanitizeErrorForLogging(err),
        'Unexpected error in create workout endpoint'
      );
      return reply.status(500).send({
        error: 'Internal server error',
      });
    }
  }
}

