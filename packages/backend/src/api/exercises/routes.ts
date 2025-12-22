import type { FastifyInstance, FastifyPluginOptions } from 'fastify';
import { ExerciseController } from './controller.js';

export default async function exerciseRoutes(
  fastify: FastifyInstance,
  options: FastifyPluginOptions
) {
  const controller = new ExerciseController();

  fastify.get('/', controller.list.bind(controller));
}

