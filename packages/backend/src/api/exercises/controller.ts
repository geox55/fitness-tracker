import type { FastifyRequest, FastifyReply } from 'fastify';
import { ExerciseService } from '../../services/exercise.service.js';
import { exerciseInputSchema } from '@fitness/shared';
import { type AuthRequest } from '../../middleware/auth.middleware.js';
import { isZodError, sanitizeErrorForLogging } from '../../utils/error-utils.js';

export class ExerciseController {
  private service = new ExerciseService();

  /**
   * Lists exercises with optional search and filter
   * @param req - Fastify request with query parameters
   * @param reply - Fastify reply
   * @returns 200 with exercise array
   */
  async list(
    req: FastifyRequest<{
      Querystring: {
        search?: string;
        muscleGroup?: string;
        status?: string;
      };
    }> | AuthRequest,
    reply: FastifyReply
  ) {
    try {
      const query = req.query as {
        search?: string;
        muscleGroup?: string;
        status?: string;
      };
      const filters = {
        search: query.search,
        muscleGroup: query.muscleGroup,
        status: query.status,
      };

      const userId = 'user' in req && req.user ? req.user.userId : undefined;
      const exercises = this.service.getExercises(filters, userId);
      return reply.status(200).send(exercises);
    } catch (err) {
      req.log.error(
        sanitizeErrorForLogging(err),
        'Unexpected error in list exercises endpoint'
      );
      return reply.status(500).send({
        error: 'Internal server error',
      });
    }
  }

  /**
   * Creates a new exercise with pending status
   */
  async create(req: AuthRequest, reply: FastifyReply) {
    try {
      const validated = exerciseInputSchema.parse(req.body || {});
      const result = await this.service.createExercise(
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
        'Unexpected error in create exercise endpoint'
      );
      return reply.status(500).send({
        error: 'Internal server error',
      });
    }
  }

  /**
   * Approves an exercise (admin only)
   */
  async approve(req: AuthRequest, reply: FastifyReply) {
    try {
      const params = req.params as { id: string };
      const { id } = params;

      const result = await this.service.approveExercise(
        id,
        req.user!.userId
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
        'Unexpected error in approve exercise endpoint'
      );
      return reply.status(500).send({
        error: 'Internal server error',
      });
    }
  }
}

