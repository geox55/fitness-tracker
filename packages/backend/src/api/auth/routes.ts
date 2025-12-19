import type { FastifyInstance, FastifyPluginOptions } from 'fastify';
import { AuthController } from './controller.js';

export default async function authRoutes(
  fastify: FastifyInstance,
  options: FastifyPluginOptions
) {
  const controller = new AuthController();

  fastify.post('/register', controller.register.bind(controller));
  fastify.post('/login', controller.login.bind(controller));
  fastify.post('/refresh', controller.refresh.bind(controller));
}

