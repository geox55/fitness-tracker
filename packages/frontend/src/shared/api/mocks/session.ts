import { jwtVerify, SignJWT } from 'jose';
import { HttpResponse } from 'msw';

type Session = {
  userId: string;
  email: string;
};

const JWT_SECRET = new TextEncoder().encode('your-secret-key');
const ACCESS_TOKEN_EXPIRY = '3s';
const REFRESH_TOKEN_EXPIRY = '7d';

export function createRefreshTokenCookie(refreshToken: string) {
  return `refreshToken=${refreshToken}; Max-Age=604800`;
}

export async function generateTokens(session: Session) {
  const accessToken = await new SignJWT(session)
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt()
    .setExpirationTime(ACCESS_TOKEN_EXPIRY)
    .sign(JWT_SECRET);

  const refreshToken = await new SignJWT(session)
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt()
    .setExpirationTime(REFRESH_TOKEN_EXPIRY)
    .sign(JWT_SECRET);

  return { accessToken, refreshToken };
}

export async function verifyToken(token: string): Promise<Session> {
  const { payload } = await jwtVerify(token, JWT_SECRET);
  return payload as Session;
}

export async function verifyTokenOrThrow(request: Request): Promise<Session> {
  const token = request.headers.get('Authorization')?.split(' ')[1];
  const session = token ? await verifyToken(token).catch(() => null) : null;

  if (!session) {
    throw HttpResponse.json(
      {
        message: 'Invalid or expired token',
        code: 'INVALID_OR_EXPIRED_TOKEN',
      },
      { status: 401 },
    );
  }

  return session;
}
