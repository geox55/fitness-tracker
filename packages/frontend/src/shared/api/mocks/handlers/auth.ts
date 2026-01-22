import { delay, HttpResponse } from 'msw';

import type { ApiSchemas } from '../../schema';
import { http } from '../http';
import { createRefreshTokenCookie, generateTokens, verifyToken } from '../session';

const mockUsers: ApiSchemas['User'][] = [
  {
    id: '1',
    email: 'admin@gmail.com',
  },
];

const userPasswords = new Map<string, string>();
userPasswords.set('admin@gmail.com', '123456');

export const authHandlers = [
  http.post('/auth/login', async ({ request }) => {
    const body = await request.json();

    const user = mockUsers.find((user) => user.email === body.email);
    const storedPassword = userPasswords.get(body.email);

    await delay(1000);

    if (!user || !storedPassword || storedPassword !== body.password) {
      return HttpResponse.json(
        {
          message: 'Неверный email или пароль',
          code: 'INVALID_CREDENTIALS',
        },
        { status: 401 },
      );
    }

    const { accessToken, refreshToken } = await generateTokens({
      userId: user.id,
      email: user.email,
    });

    return HttpResponse.json(
      { accessToken, user },
      {
        status: 200,
        headers: {
          'Set-Cookie': createRefreshTokenCookie(refreshToken),
        },
      },
    );
  }),
  http.post('/auth/register', async ({ request }) => {
    const body = await request.json();

    await delay(1000);

    if (mockUsers.some((u) => u.email === body.email)) {
      return HttpResponse.json(
        { message: 'Пользователь уже существует', code: 'USER_ALREADY_EXISTS' },
        { status: 400 },
      );
    }

    const newUser: ApiSchemas['User'] = {
      id: crypto.randomUUID(),
      email: body.email,
    };
    const { accessToken, refreshToken } = await generateTokens({
      userId: newUser.id,
      email: newUser.email,
    });

    mockUsers.push(newUser);
    userPasswords.set(body.email, body.password);

    return HttpResponse.json(
      { accessToken, user: newUser },
      {
        status: 201,
        headers: {
          'Set-Cookie': createRefreshTokenCookie(refreshToken),
        },
      },
    );
  }),
  http.post('/auth/refresh', async ({ cookies }) => {
    const refreshToken = cookies.refreshToken;

    if (!refreshToken) {
      return HttpResponse.json(
        { message: 'Токен обновления не найден', code: 'REFRESH_TOKEN_NOT_FOUND' },
        { status: 401 },
      );
    }

    try {
      const session = await verifyToken(refreshToken);
      const user = mockUsers.find((u) => u.id === session.userId);
      if (!user) {
        throw new Error('Пользователь не найден');
      }
      const { accessToken, refreshToken: newRefreshToken } = await generateTokens({
        userId: user.id,
        email: user.email,
      });
      return HttpResponse.json(
        { accessToken, user },
        {
          status: 200,
          headers: {
            'Set-Cookie': createRefreshTokenCookie(newRefreshToken),
          },
        },
      );
    } catch (error) {
      console.error('Ошибка при обновлении токена', error);
      return HttpResponse.json(
        { message: 'Неверный токен обновления', code: 'INVALID_REFRESH_TOKEN' },
        { status: 401 },
      );
    }
  }),
];
