import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import Fastify from 'fastify';
import authRoutes from '../../src/api/auth/routes.js';
import { DatabaseManager } from '../../src/db/database.js';

// Setup database before all tests
beforeAll(() => {
  const db = DatabaseManager.getInstance();
  const migrateSql = `
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
  `;
  db.exec(migrateSql);
});

afterAll(() => {
  DatabaseManager.close();
});

describe('POST /api/auth/register', () => {
  let app: ReturnType<typeof Fastify>;

  beforeAll(async () => {
    app = Fastify();
    await app.register(authRoutes, { prefix: '/api/auth' });
    await app.ready();
  });

  afterAll(async () => {
    await app.close();
  });

  it('should return 201 with token and user on successful registration', async () => {
    const email = `newuser-${Date.now()}@example.com`;
    const response = await app.inject({
      method: 'POST',
      url: '/api/auth/register',
      payload: {
        email,
        password: 'password123',
        passwordConfirm: 'password123',
      },
    });

    expect(response.statusCode).toBe(201);
    const body = JSON.parse(response.body);
    expect(body).toHaveProperty('token');
    expect(body).toHaveProperty('user');
    expect(body.user.email).toBe(email);
    expect(body.user).toHaveProperty('id');
  });

  it('should return 400 for invalid email format', async () => {
    const response = await app.inject({
      method: 'POST',
      url: '/api/auth/register',
      payload: {
        email: 'invalid-email',
        password: 'password123',
        passwordConfirm: 'password123',
      },
    });

    expect(response.statusCode).toBe(400);
    const body = JSON.parse(response.body);
    expect(body).toHaveProperty('error');
  });

  it('should return 400 for password less than 8 characters', async () => {
    const response = await app.inject({
      method: 'POST',
      url: '/api/auth/register',
      payload: {
        email: 'test@example.com',
        password: 'short',
        passwordConfirm: 'short',
      },
    });

    expect(response.statusCode).toBe(400);
    const body = JSON.parse(response.body);
    expect(body).toHaveProperty('error');
  });

  it('should return 400 if passwords do not match', async () => {
    const response = await app.inject({
      method: 'POST',
      url: '/api/auth/register',
      payload: {
        email: 'test@example.com',
        password: 'password123',
        passwordConfirm: 'password456',
      },
    });

    expect(response.statusCode).toBe(400);
    const body = JSON.parse(response.body);
    expect(body).toHaveProperty('error');
  });

  it('should return 409 if email already exists', async () => {
    const email = `existing-${Date.now()}@example.com`;
    const password = 'password123';

    await app.inject({
      method: 'POST',
      url: '/api/auth/register',
      payload: {
        email,
        password,
        passwordConfirm: password,
      },
    });

    const response = await app.inject({
      method: 'POST',
      url: '/api/auth/register',
      payload: {
        email,
        password,
        passwordConfirm: password,
      },
    });

    expect(response.statusCode).toBe(409);
    const body = JSON.parse(response.body);
    expect(body).toHaveProperty('error');
    expect(body.error).toContain('already exists');
  });
});

describe('POST /api/auth/login', () => {
  let app: ReturnType<typeof Fastify>;

  beforeAll(async () => {
    app = Fastify();
    await app.register(authRoutes, { prefix: '/api/auth' });
    await app.ready();
  });

  afterAll(async () => {
    await app.close();
  });

  it('should return 200 with token and user on successful login', async () => {
    const email = `loginuser-${Date.now()}@example.com`;
    const password = 'password123';

    await app.inject({
      method: 'POST',
      url: '/api/auth/register',
      payload: {
        email,
        password,
        passwordConfirm: password,
      },
    });

    const response = await app.inject({
      method: 'POST',
      url: '/api/auth/login',
      payload: {
        email,
        password,
      },
    });

    expect(response.statusCode).toBe(200);
    const body = JSON.parse(response.body);
    expect(body).toHaveProperty('token');
    expect(body).toHaveProperty('user');
    expect(body.user.email).toBe(email);
  });

  it('should return 400 if email is missing', async () => {
    const response = await app.inject({
      method: 'POST',
      url: '/api/auth/login',
      payload: {
        password: 'password123',
      },
    });

    expect(response.statusCode).toBe(400);
    const body = JSON.parse(response.body);
    expect(body).toHaveProperty('error');
  });

  it('should return 400 if password is missing', async () => {
    const response = await app.inject({
      method: 'POST',
      url: '/api/auth/login',
      payload: {
        email: 'test@example.com',
      },
    });

    expect(response.statusCode).toBe(400);
    const body = JSON.parse(response.body);
    expect(body).toHaveProperty('error');
  });

  it('should return 401 for non-existent email', async () => {
    const response = await app.inject({
      method: 'POST',
      url: '/api/auth/login',
      payload: {
        email: 'nonexistent@example.com',
        password: 'password123',
      },
    });

    expect(response.statusCode).toBe(401);
    const body = JSON.parse(response.body);
    expect(body).toHaveProperty('error');
    expect(body.error).toContain('Invalid credentials');
  });

  it('should return 401 for incorrect password', async () => {
    const email = `wrongpass-${Date.now()}@example.com`;
    const password = 'password123';

    await app.inject({
      method: 'POST',
      url: '/api/auth/register',
      payload: {
        email,
        password,
        passwordConfirm: password,
      },
    });

    const response = await app.inject({
      method: 'POST',
      url: '/api/auth/login',
      payload: {
        email,
        password: 'wrongpassword',
      },
    });

    expect(response.statusCode).toBe(401);
    const body = JSON.parse(response.body);
    expect(body).toHaveProperty('error');
    expect(body.error).toContain('Invalid credentials');
  });
});

describe('POST /api/auth/refresh', () => {
  let app: ReturnType<typeof Fastify>;

  beforeAll(async () => {
    app = Fastify();
    await app.register(authRoutes, { prefix: '/api/auth' });
    await app.ready();
  });

  afterAll(async () => {
    await app.close();
  });

  it('should return 200 with new token on successful refresh', async () => {
    const email = `refreshuser-${Date.now()}@example.com`;
    const password = 'password123';

    const registerResponse = await app.inject({
      method: 'POST',
      url: '/api/auth/register',
      payload: {
        email,
        password,
        passwordConfirm: password,
      },
    });

    const registerBody = JSON.parse(registerResponse.body);
    const originalToken = registerBody.token;

    const response = await app.inject({
      method: 'POST',
      url: '/api/auth/refresh',
      payload: {
        refreshToken: originalToken,
      },
    });

    expect(response.statusCode).toBe(200);
    const body = JSON.parse(response.body);
    expect(body).toHaveProperty('token');
    expect(body.token).toBeTruthy();
    expect(typeof body.token).toBe('string');
  });

  it('should return 401 for invalid token', async () => {
    const response = await app.inject({
      method: 'POST',
      url: '/api/auth/refresh',
      payload: {
        refreshToken: 'invalid.token.here',
      },
    });

    expect(response.statusCode).toBe(401);
    const body = JSON.parse(response.body);
    expect(body).toHaveProperty('error');
    expect(body.error).toContain('Invalid token');
  });

  it('should return 400 if refreshToken is missing', async () => {
    const response = await app.inject({
      method: 'POST',
      url: '/api/auth/refresh',
      payload: {},
    });

    expect(response.statusCode).toBe(400);
    const body = JSON.parse(response.body);
    expect(body).toHaveProperty('error');
  });
});

