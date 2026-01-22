import type { FastifyReply } from 'fastify';
import { WorkoutService } from '../../services/workout.service.js';
import { workoutSchema } from '@fitness/shared';
import { type AuthRequest } from '../../middleware/auth.middleware.js';
import { isZodError, sanitizeErrorForLogging } from '../../utils/error-utils.js';
import {
  InvalidWeightError,
  InvalidRepsError,
  InvalidSetsError,
  WorkoutNotFoundError,
  WorkoutAccessDeniedError,
} from '../../errors/workout.errors.js';

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

  /**
   * Lists workouts for the authenticated user
   * @param req - Fastify request with query parameters
   * @param reply - Fastify reply
   * @returns 200 with workouts list
   */
  async list(req: AuthRequest, reply: FastifyReply) {
    try {
      const query = req.query as {
        exerciseId?: string;
        from?: string;
        to?: string;
        limit?: number;
        offset?: number;
      };
      const filters = {
        exerciseId: query.exerciseId,
        from: query.from,
        to: query.to,
        limit: query.limit,
        offset: query.offset,
      };

      const result = await this.service.getWorkouts(req.user!.userId, filters);
      return reply.status(200).send(result);
    } catch (err) {
      req.log.error(
        sanitizeErrorForLogging(err),
        'Unexpected error in list workouts endpoint'
      );
      return reply.status(500).send({
        error: 'Internal server error',
      });
    }
  }

  /**
   * Updates a workout
   * @param req - Fastify request with workout ID and update data
   * @param reply - Fastify reply
   * @returns 200 with updated workout, 404/403/400 on error
   */
  async update(req: AuthRequest, reply: FastifyReply) {
    try {
      const params = req.params as { id: string };
      const { id } = params;
      const updateData = req.body as Partial<{
        weight?: number;
        reps?: number;
        sets?: number;
        notes?: string;
      }>;

      const result = await this.service.updateWorkout(
        id,
        req.user!.userId,
        updateData
      );
      return reply.status(200).send(result);
    } catch (err) {
      if (err instanceof WorkoutNotFoundError) {
        return reply.status(404).send({
          error: err.message,
        });
      }
      if (err instanceof WorkoutAccessDeniedError) {
        return reply.status(403).send({
          error: err.message,
        });
      }
      if (
        err instanceof InvalidWeightError ||
        err instanceof InvalidRepsError ||
        err instanceof InvalidSetsError
      ) {
        return reply.status(400).send({
          error: err.message,
        });
      }
      req.log.error(
        sanitizeErrorForLogging(err),
        'Unexpected error in update workout endpoint'
      );
      return reply.status(500).send({
        error: 'Internal server error',
      });
    }
  }

  /**
   * Deletes a workout
   * @param req - Fastify request with workout ID
   * @param reply - Fastify reply
   * @returns 200 with success message, 404/403 on error
   */
  async delete(req: AuthRequest, reply: FastifyReply) {
    try {
      const params = req.params as { id: string };
      const { id } = params;
      await this.service.deleteWorkout(id, req.user!.userId);
      return reply.status(200).send({
        success: true,
      });
    } catch (err) {
      if (err instanceof WorkoutNotFoundError) {
        return reply.status(404).send({
          error: err.message,
        });
      }
      if (err instanceof WorkoutAccessDeniedError) {
        return reply.status(403).send({
          error: err.message,
        });
      }
      req.log.error(
        sanitizeErrorForLogging(err),
        'Unexpected error in delete workout endpoint'
      );
      return reply.status(500).send({
        error: 'Internal server error',
      });
    }
  }
}

