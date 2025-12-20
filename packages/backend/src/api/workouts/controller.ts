import type { FastifyReply } from 'fastify';
import { WorkoutService } from '../../services/workout.service.js';
import { workoutSchema } from '@fitness/shared';
import { type AuthRequest } from '../../middleware/auth.middleware.js';
import { isZodError, sanitizeErrorForLogging } from '../../utils/error-utils.js';
import { InvalidWeightError, InvalidRepsError } from '../../errors/workout.errors.js';

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
      if (err instanceof InvalidWeightError || err instanceof InvalidRepsError) {
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

