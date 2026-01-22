import type { FastifyInstance, FastifyPluginOptions } from 'fastify';
import { WorkoutSessionController } from './controller.js';
import { authMiddleware } from '../../middleware/auth.middleware.js';

export default async function workoutSessionRoutes(
  fastify: FastifyInstance,
  options: FastifyPluginOptions
) {
  const controller = new WorkoutSessionController();

  fastify.get('/', {
    schema: {
      querystring: {
        type: 'object',
        properties: {
          from: { type: 'string', format: 'date-time' },
          to: { type: 'string', format: 'date-time' },
          limit: { type: 'integer', minimum: 1, maximum: 1000 },
          offset: { type: 'integer', minimum: 0 },
        },
      },
    },
    preHandler: authMiddleware,
  }, controller.list.bind(controller));

  fastify.post('/', {
    preHandler: authMiddleware,
  }, controller.create.bind(controller));

  fastify.get('/:id', {
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
  }, controller.getById.bind(controller));

  fastify.patch('/:id', {
    schema: {
      params: {
        type: 'object',
        properties: {
          id: { type: 'string', format: 'uuid' },
        },
        required: ['id'],
      },
      body: {
        type: 'object',
        properties: {
          loggedAt: { type: 'string', format: 'date-time' },
          duration: { type: 'integer', minimum: 1 },
          notes: { type: 'string', maxLength: 1000 },
        },
      },
    },
    preHandler: authMiddleware,
  }, controller.update.bind(controller));

  fastify.delete('/:id', {
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
  }, controller.delete.bind(controller));
}
