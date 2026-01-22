import type { FastifyReply } from 'fastify';
import { WorkoutSessionService } from '../../services/workout-session.service.js';
import { workoutSessionInputSchema } from '@fitness/shared';
import { type AuthRequest } from '../../middleware/auth.middleware.js';
import { isZodError, sanitizeErrorForLogging } from '../../utils/error-utils.js';

export class WorkoutSessionController {
  private service = new WorkoutSessionService();

  /**
   * Creates a new workout session
   */
  async create(req: AuthRequest, reply: FastifyReply) {
    try {
      const validated = workoutSessionInputSchema.parse(req.body || {});
      const result = await this.service.createWorkoutSession(
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
      if (err instanceof Error && err.message.includes('required')) {
        return reply.status(400).send({
          error: err.message,
        });
      }
      req.log.error(
        sanitizeErrorForLogging(err),
        'Unexpected error in create workout session endpoint'
      );
      return reply.status(500).send({
        error: 'Internal server error',
      });
    }
  }

  /**
   * Lists workout sessions for the authenticated user
   */
  async list(req: AuthRequest, reply: FastifyReply) {
    try {
      const query = req.query as {
        from?: string;
        to?: string;
        limit?: number;
        offset?: number;
      };
      const filters = {
        from: query.from,
        to: query.to,
        limit: query.limit,
        offset: query.offset,
      };

      const result = await this.service.getWorkoutSessions(
        req.user!.userId,
        filters
      );
      return reply.status(200).send(result);
    } catch (err) {
      req.log.error(
        sanitizeErrorForLogging(err),
        'Unexpected error in list workout sessions endpoint'
      );
      return reply.status(500).send({
        error: 'Internal server error',
      });
    }
  }

  /**
   * Gets a workout session by ID
   */
  async getById(req: AuthRequest, reply: FastifyReply) {
    try {
      const params = req.params as { id: string };
      const { id } = params;

      const result = await this.service.getWorkoutSessionById(
        id,
        req.user!.userId
      );

      if (!result) {
        return reply.status(404).send({
          error: 'Workout session not found',
        });
      }

      return reply.status(200).send(result);
    } catch (err) {
      req.log.error(
        sanitizeErrorForLogging(err),
        'Unexpected error in get workout session endpoint'
      );
      return reply.status(500).send({
        error: 'Internal server error',
      });
    }
  }

  /**
   * Updates a workout session
   */
  async update(req: AuthRequest, reply: FastifyReply) {
    try {
      const params = req.params as { id: string };
      const { id } = params;
      const updateData = req.body as Partial<{
        loggedAt?: string;
        duration?: number;
        notes?: string;
      }>;

      const result = await this.service.updateWorkoutSession(
        id,
        req.user!.userId,
        updateData
      );
      return reply.status(200).send(result);
    } catch (err) {
      if (err instanceof Error && err.message.includes('not found')) {
        return reply.status(404).send({
          error: err.message,
        });
      }
      req.log.error(
        sanitizeErrorForLogging(err),
        'Unexpected error in update workout session endpoint'
      );
      return reply.status(500).send({
        error: 'Internal server error',
      });
    }
  }

  /**
   * Deletes a workout session
   */
  async delete(req: AuthRequest, reply: FastifyReply) {
    try {
      const params = req.params as { id: string };
      const { id } = params;

      await this.service.deleteWorkoutSession(id, req.user!.userId);
      return reply.status(200).send({
        success: true,
      });
    } catch (err) {
      if (err instanceof Error && err.message.includes('not found')) {
        return reply.status(404).send({
          error: err.message,
        });
      }
      req.log.error(
        sanitizeErrorForLogging(err),
        'Unexpected error in delete workout session endpoint'
      );
      return reply.status(500).send({
        error: 'Internal server error',
      });
    }
  }
}
