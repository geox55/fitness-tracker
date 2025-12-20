import type { FastifyInstance, FastifyPluginOptions } from 'fastify';
import { WorkoutController } from './controller.js';
import { authMiddleware } from '../../middleware/auth.middleware.js';

export default async function workoutRoutes(
  fastify: FastifyInstance,
  options: FastifyPluginOptions
) {
  const controller = new WorkoutController();

  fastify.post('/', {
    preHandler: authMiddleware,
  }, controller.create.bind(controller));
}

