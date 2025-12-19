import type { FastifyRequest, FastifyReply } from 'fastify';
import { AuthService } from '../../services/auth.service.js';
import { registerSchema, loginSchema } from '@fitness/shared';

export class AuthController {
  private service = new AuthService();

  async register(req: FastifyRequest, reply: FastifyReply) {
    try {
      const validated = registerSchema.parse(req.body);
      const result = await this.service.register(validated.email, validated.password);
      return reply.status(201).send(result);
    } catch (err: any) {
      if (err.name === 'ZodError') {
        return reply.status(400).send({
          error: 'Validation failed',
          details: err.errors,
        });
      }
      if (err.message === 'Email already exists') {
        return reply.status(409).send({
          error: 'Email already exists',
        });
      }
      return reply.status(500).send({
        error: err.message || 'Internal server error',
      });
    }
  }

  async login(req: FastifyRequest, reply: FastifyReply) {
    try {
      const validated = loginSchema.parse(req.body);
      const result = await this.service.login(validated.email, validated.password);
      return reply.status(200).send(result);
    } catch (err: any) {
      if (err.name === 'ZodError') {
        return reply.status(400).send({
          error: 'Validation failed',
          details: err.errors,
        });
      }
      if (err.message === 'Invalid credentials') {
        return reply.status(401).send({
          error: 'Invalid credentials',
        });
      }
      return reply.status(500).send({
        error: err.message || 'Internal server error',
      });
    }
  }

  async refresh(req: FastifyRequest, reply: FastifyReply) {
    try {
      const { refreshToken } = req.body as { refreshToken?: string };
      if (!refreshToken) {
        return reply.status(400).send({
          error: 'refreshToken is required',
        });
      }
      const result = await this.service.refresh(refreshToken);
      return reply.status(200).send(result);
    } catch (err: any) {
      if (err.message === 'Invalid token') {
        return reply.status(401).send({
          error: 'Invalid token',
        });
      }
      return reply.status(500).send({
        error: err.message || 'Internal server error',
      });
    }
  }
}

