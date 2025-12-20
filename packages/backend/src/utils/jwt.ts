import { SignJWT, jwtVerify, type JWTPayload as JosePayload } from 'jose';
import { JWT_SECRET_MIN_LENGTH } from '../constants/index.js';
import { InvalidTokenError } from '../errors/auth.errors.js';

const DEFAULT_JWT_SECRET = 'dev-secret';
const DEFAULT_JWT_EXPIRY = '7d';

const JWT_SECRET = process.env.JWT_SECRET || DEFAULT_JWT_SECRET;
const JWT_EXPIRY = process.env.JWT_EXPIRY || DEFAULT_JWT_EXPIRY;

// Validate JWT_SECRET in production
if (process.env.NODE_ENV === 'production') {
  if (!process.env.JWT_SECRET) {
    throw new Error('JWT_SECRET environment variable is required in production');
  }
  if (JWT_SECRET === DEFAULT_JWT_SECRET) {
    throw new Error(
      'JWT_SECRET cannot be "dev-secret" in production. Use a strong random secret.'
    );
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

/**
 * Signs a JWT token with user payload
 * @param payload - User data to include in token (userId, email)
 * @returns Signed JWT token string
 */
export async function signToken(payload: JWTPayload): Promise<string> {
  const token = await new SignJWT(payload as Record<string, unknown>)
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt()
    .setExpirationTime(JWT_EXPIRY)
    .sign(secretKey);

  return token;
}

/**
 * Verifies and decodes a JWT token
 * @param token - JWT token string to verify
 * @returns Decoded token payload with userId and email
 * @throws {InvalidTokenError} If token is invalid, expired, or malformed
 */
export async function verifyToken(token: string): Promise<JWTPayload> {
  try {
    const { payload } = await jwtVerify(token, secretKey);
    return {
      userId: payload.userId as string,
      email: payload.email as string,
    };
  } catch (error) {
    // Provide more specific error messages in development
    const message =
      process.env.NODE_ENV === 'development' && error instanceof Error
        ? `Token verification failed: ${error.message}`
        : 'Invalid token';
    throw new InvalidTokenError(message);
  }
}

