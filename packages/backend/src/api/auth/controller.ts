import type { FastifyRequest, FastifyReply } from 'fastify';
import { ZodError } from 'zod';
import { AuthService } from '../../services/auth.service.js';
import { registerSchema, loginSchema } from '@fitness/shared';
import {
  EmailAlreadyExistsError,
  InvalidCredentialsError,
  InvalidTokenError,
} from '../../errors/auth.errors.js';

export class AuthController {
  private service = new AuthService();

  async register(req: FastifyRequest, reply: FastifyReply) {
    try {
      const validated = registerSchema.parse(req.body || {});
      const result = await this.service.register(validated.email, validated.password);
      return reply.status(201).send(result);
    } catch (err) {
      // Check if it's a ZodError by checking the name property as well
      if (err instanceof ZodError || (err as any)?.name === 'ZodError') {
        return reply.status(400).send({
          error: 'Validation failed',
          details: (err as ZodError).errors,
        });
      }
      if (err instanceof EmailAlreadyExistsError) {
        return reply.status(409).send({
          error: 'Email already exists',
        });
      }
      // Log unexpected errors
      req.log.error({ err }, 'Unexpected error in register endpoint');
      return reply.status(500).send({
        error: 'Internal server error',
      });
    }
  }

  async login(req: FastifyRequest, reply: FastifyReply) {
    try {
      const validated = loginSchema.parse(req.body || {});
      const result = await this.service.login(validated.email, validated.password);
      return reply.status(200).send(result);
    } catch (err) {
      // Check if it's a ZodError by checking the name property as well
      if (err instanceof ZodError || (err as any)?.name === 'ZodError') {
        return reply.status(400).send({
          error: 'Validation failed',
          details: (err as ZodError).errors,
        });
      }
      if (err instanceof InvalidCredentialsError) {
        return reply.status(401).send({
          error: 'Invalid credentials',
        });
      }
      // Log unexpected errors
      req.log.error({ err }, 'Unexpected error in login endpoint');
      return reply.status(500).send({
        error: 'Internal server error',
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
    } catch (err) {
      if (err instanceof InvalidTokenError) {
        return reply.status(401).send({
          error: 'Invalid token',
        });
      }
      // Log unexpected errors
      req.log.error({ err }, 'Unexpected error in refresh endpoint');
      return reply.status(500).send({
        error: 'Internal server error',
      });
    }
  }
}

