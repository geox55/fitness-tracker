import type { FastifyReply } from 'fastify';
import { SupersetService } from '../../services/superset.service.js';
import { supersetInputSchema } from '@fitness/shared';
import { type AuthRequest } from '../../middleware/auth.middleware.js';
import { isZodError, sanitizeErrorForLogging } from '../../utils/error-utils.js';

export class SupersetController {
  private service = new SupersetService();

  /**
   * Creates a new superset in a workout session
   */
  async create(req: AuthRequest, reply: FastifyReply) {
    try {
      const params = req.params as { sessionId: string };
      const { sessionId } = params;

      const validated = supersetInputSchema.parse(req.body || {});
      const result = await this.service.createSuperset(
        sessionId,
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
      if (err instanceof Error && err.message.includes('not found')) {
        return reply.status(404).send({
          error: err.message,
        });
      }
      if (err instanceof Error && err.message.includes('must')) {
        return reply.status(400).send({
          error: err.message,
        });
      }
      req.log.error(
        sanitizeErrorForLogging(err),
        'Unexpected error in create superset endpoint'
      );
      return reply.status(500).send({
        error: 'Internal server error',
      });
    }
  }
}
