import { SignJWT, jwtVerify } from 'jose';
import { JWT_SECRET_MIN_LENGTH } from '../constants/index.js';

const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret';
const JWT_EXPIRY = process.env.JWT_EXPIRY || '7d';

// Validate JWT_SECRET in production
if (process.env.NODE_ENV === 'production') {
  if (!process.env.JWT_SECRET) {
    throw new Error('JWT_SECRET environment variable is required in production');
  }
  if (JWT_SECRET === 'dev-secret') {
    throw new Error('JWT_SECRET cannot be "dev-secret" in production. Use a strong random secret.');
  }
  if (JWT_SECRET.length < JWT_SECRET_MIN_LENGTH) {
    throw new Error(
      `JWT_SECRET must be at least ${JWT_SECRET_MIN_LENGTH} characters long in production. Current length: ${JWT_SECRET.length}`
    );
  }
}

export interface JWTPayload {
  userId: string;
  email: string;
  [key: string]: unknown;
}

const secretKey = new TextEncoder().encode(JWT_SECRET);

export async function signToken(payload: JWTPayload): Promise<string> {
  const token = await new SignJWT(payload as Record<string, unknown>)
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt()
    .setExpirationTime(JWT_EXPIRY)
    .sign(secretKey);

  return token;
}

export async function verifyToken(token: string): Promise<JWTPayload> {
  try {
    const { payload } = await jwtVerify(token, secretKey);
    return {
      userId: payload.userId as string,
      email: payload.email as string,
    };
  } catch (error) {
    throw new Error('Invalid token');
  }
}

