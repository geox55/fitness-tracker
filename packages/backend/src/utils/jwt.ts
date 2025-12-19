import { SignJWT, jwtVerify } from 'jose';

const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret';
const JWT_EXPIRY = process.env.JWT_EXPIRY || '7d';

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

