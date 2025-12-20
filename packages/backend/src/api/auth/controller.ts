import type { FastifyRequest, FastifyReply } from 'fastify';
import { AuthService } from '../../services/auth.service.js';
import {
  registerSchema,
  loginSchema,
  refreshTokenSchema,
} from '@fitness/shared';
import {
  EmailAlreadyExistsError,
  InvalidCredentialsError,
  InvalidTokenError,
} from '../../errors/auth.errors.js';
import { isZodError, sanitizeErrorForLogging } from '../../utils/error-utils.js';

export class AuthController {
  private service = new AuthService();

  /**
   * Registers a new user
   * @param req - Fastify request with email, password, and passwordConfirm
   * @param reply - Fastify reply
   * @returns 201 with token and user data on success, 400/409/500 on error
   */
  async register(req: FastifyRequest, reply: FastifyReply) {
    try {
      const validated = registerSchema.parse(req.body || {});
      const result = await this.service.register(validated.email, validated.password);
      return reply.status(201).send(result);
    } catch (err) {
      if (isZodError(err)) {
        return reply.status(400).send({
          error: 'Validation failed',
          details: err.errors,
        });
      }
      if (err instanceof EmailAlreadyExistsError) {
        return reply.status(409).send({
          error: 'Email already exists',
        });
      }
      req.log.error(
        sanitizeErrorForLogging(err),
        'Unexpected error in register endpoint'
      );
      return reply.status(500).send({
        error: 'Internal server error',
      });
    }
  }

  /**
   * Authenticates a user and returns JWT token
   * @param req - Fastify request with email and password
   * @param reply - Fastify reply
   * @returns 200 with token and user data on success, 400/401/500 on error
   */
  async login(req: FastifyRequest, reply: FastifyReply) {
    try {
      const validated = loginSchema.parse(req.body || {});
      const result = await this.service.login(validated.email, validated.password);
      return reply.status(200).send(result);
    } catch (err) {
      if (isZodError(err)) {
        return reply.status(400).send({
          error: 'Validation failed',
          details: err.errors,
        });
      }
      if (err instanceof InvalidCredentialsError) {
        return reply.status(401).send({
          error: 'Invalid credentials',
        });
      }
      req.log.error(
        sanitizeErrorForLogging(err),
        'Unexpected error in login endpoint'
      );
      return reply.status(500).send({
        error: 'Internal server error',
      });
    }
  }

  /**
   * Refreshes JWT token
   * @param req - Fastify request with refreshToken
   * @param reply - Fastify reply
   * @returns 200 with new token on success, 400/401/500 on error
   */
  async refresh(req: FastifyRequest, reply: FastifyReply) {
    try {
      const validated = refreshTokenSchema.parse(req.body || {});
      const result = await this.service.refresh(validated.refreshToken);
      return reply.status(200).send(result);
    } catch (err) {
      if (isZodError(err)) {
        return reply.status(400).send({
          error: 'Validation failed',
          details: err.errors,
        });
      }
      if (err instanceof InvalidTokenError) {
        return reply.status(401).send({
          error: 'Invalid token',
        });
      }
      req.log.error(
        sanitizeErrorForLogging(err),
        'Unexpected error in refresh endpoint'
      );
      return reply.status(500).send({
        error: 'Internal server error',
      });
    }
  }
}

