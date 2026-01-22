import type { FastifyInstance, FastifyPluginOptions } from 'fastify';
import { ExerciseController } from './controller.js';
import { authMiddleware } from '../../middleware/auth.middleware.js';

export default async function exerciseRoutes(
  fastify: FastifyInstance,
  options: FastifyPluginOptions
) {
  const controller = new ExerciseController();

  fastify.get(
    '/',
    {
      schema: {
        querystring: {
          type: 'object',
          properties: {
            search: { type: 'string', maxLength: 100 },
            muscleGroup: { type: 'string', maxLength: 50 },
            status: { type: 'string', enum: ['pending', 'approved', 'rejected'] },
          },
        },
      },
      preHandler: authMiddleware,
    },
    controller.list.bind(controller)
  );

  fastify.post('/', {
    preHandler: authMiddleware,
  }, controller.create.bind(controller));

  fastify.patch('/:id/approve', {
    schema: {
      params: {
        type: 'object',
        properties: {
          id: { type: 'string', format: 'uuid' },
        },
        required: ['id'],
      },
    },
    preHandler: authMiddleware,
  }, controller.approve.bind(controller));
}

