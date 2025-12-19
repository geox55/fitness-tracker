import type { FastifyRequest, FastifyReply } from 'fastify';
import { verifyToken } from '../utils/jwt.js';

export interface AuthRequest extends FastifyRequest {
  user?: {
    userId: string;
    email: string;
  };
}

export async function authMiddleware(
  req: AuthRequest,
  reply: FastifyReply
): Promise<void> {
  try {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return reply.status(401).send({ error: 'Unauthorized' });
    }

    const token = authHeader.substring(7);
    const payload = await verifyToken(token);

    req.user = {
      userId: payload.userId,
      email: payload.email,
    };
  } catch (error) {
    return reply.status(401).send({ error: 'Unauthorized' });
  }
}

