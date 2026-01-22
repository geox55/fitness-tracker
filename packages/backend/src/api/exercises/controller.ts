import type { FastifyRequest, FastifyReply } from 'fastify';
import { ExerciseService } from '../../services/exercise.service.js';
import { sanitizeErrorForLogging } from '../../utils/error-utils.js';

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
      };
    }>,
    reply: FastifyReply
  ) {
    try {
      const filters = {
        search: req.query.search,
        muscleGroup: req.query.muscleGroup,
      };

      const exercises = this.service.getExercises(filters);
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
}

