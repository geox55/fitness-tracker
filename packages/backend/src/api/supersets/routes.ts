import type { FastifyInstance, FastifyPluginOptions } from 'fastify';
import { SupersetController } from './controller.js';
import { authMiddleware } from '../../middleware/auth.middleware.js';

export default async function supersetRoutes(
  fastify: FastifyInstance,
  options: FastifyPluginOptions
) {
  const controller = new SupersetController();

  fastify.post('/:sessionId/supersets', {
    schema: {
      params: {
        type: 'object',
        properties: {
          sessionId: { type: 'string', format: 'uuid' },
        },
        required: ['sessionId'],
      },
    },
    preHandler: authMiddleware,
  }, controller.create.bind(controller));
}
