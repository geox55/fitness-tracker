import type { FastifyInstance, FastifyPluginOptions } from 'fastify';
import { ExerciseController } from './controller.js';

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
          },
        },
      },
    },
    controller.list.bind(controller)
  );
}

