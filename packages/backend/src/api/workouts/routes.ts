import type { FastifyInstance, FastifyPluginOptions } from 'fastify';
import { WorkoutController } from './controller.js';
import { authMiddleware } from '../../middleware/auth.middleware.js';

export default async function workoutRoutes(
  fastify: FastifyInstance,
  options: FastifyPluginOptions
) {
  const controller = new WorkoutController();

  fastify.get('/', {
    preHandler: authMiddleware,
  }, controller.list.bind(controller));

  fastify.post('/', {
    preHandler: authMiddleware,
  }, controller.create.bind(controller));

  fastify.patch('/:id', {
    preHandler: authMiddleware,
  }, controller.update.bind(controller));

  fastify.delete('/:id', {
    preHandler: authMiddleware,
  }, controller.delete.bind(controller));
}

