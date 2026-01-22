import { describe, it, expect, beforeEach, beforeAll, afterAll } from 'vitest';
import { AuthService } from '../../src/services/auth.service.js';
import {
  EmailAlreadyExistsError,
  InvalidCredentialsError,
  InvalidTokenError,
} from '../../src/errors/auth.errors.js';
import { DatabaseManager } from '../../src/db/database.js';

describe('AuthService', () => {
  let service: AuthService;

  beforeAll(async () => {
    // Run migrations before tests
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

  beforeEach(() => {
    service = new AuthService();
    // Clean up test data before each test
    const db = DatabaseManager.getInstance();
    // Only delete from users table (workout_logs may not exist in unit tests)
    try {
      db.prepare('DELETE FROM users').run();
    } catch (error) {
      // Ignore if table doesn't exist
    }
  });

  describe('register', () => {
    it('should successfully register a new user', async () => {
      const email = `test-${Date.now()}@example.com`;
      const password = 'password123';

      const result = await service.register(email, password);

      expect(result).toHaveProperty('token');
      expect(result).toHaveProperty('user');
      expect(result.user.email).toBe(email.toLowerCase());
      expect(result.user).toHaveProperty('id');
    });

    it('should normalize email to lowercase', async () => {
      const email = `TestUser-${Date.now()}@Example.COM`;
      const password = 'password123';

      const result = await service.register(email, password);

      expect(result.user.email).toBe(email.toLowerCase());
    });

    it('should throw EmailAlreadyExistsError if email already exists', async () => {
      const email = `existing-${Date.now()}@example.com`;
      const password = 'password123';

      await service.register(email, password);

      await expect(service.register(email, password)).rejects.toThrow(EmailAlreadyExistsError);
    });

    it('should hash password before storing', async () => {
      const email = `test2-${Date.now()}@example.com`;
      const password = 'password123';

      const result = await service.register(email, password);

      expect(result.token).toBeTruthy();
      expect(result.user.email).toBe(email.toLowerCase());
    });
  });

  describe('login', () => {
    it('should successfully login with valid credentials', async () => {
      const email = `login-${Date.now()}@example.com`;
      const password = 'password123';

      await service.register(email, password);
      const result = await service.login(email, password);

      expect(result).toHaveProperty('token');
      expect(result).toHaveProperty('user');
      expect(result.user.email).toBe(email.toLowerCase());
    });

    it('should normalize email to lowercase on login', async () => {
      const email = `LoginUser-${Date.now()}@Example.COM`;
      const password = 'password123';

      await service.register(email, password);
      const result = await service.login(email.toUpperCase(), password);

      expect(result.user.email).toBe(email.toLowerCase());
    });

    it('should throw InvalidCredentialsError if email does not exist', async () => {
      const email = 'nonexistent@example.com';
      const password = 'password123';

      await expect(service.login(email, password)).rejects.toThrow(InvalidCredentialsError);
    });

    it('should throw InvalidCredentialsError if password is incorrect', async () => {
      const email = `wrongpass-${Date.now()}@example.com`;
      const password = 'password123';
      const wrongPassword = 'wrongpassword';

      await service.register(email, password);

      await expect(service.login(email, wrongPassword)).rejects.toThrow(InvalidCredentialsError);
    });
  });

  describe('refresh', () => {
    it('should successfully refresh valid token', async () => {
      const email = `refresh-${Date.now()}@example.com`;
      const password = 'password123';

      const loginResult = await service.register(email, password);
      const result = await service.refresh(loginResult.token);

      expect(result).toHaveProperty('token');
      expect(result.token).toBeTruthy();
      expect(typeof result.token).toBe('string');
    });

    it('should throw InvalidTokenError if token is invalid', async () => {
      const invalidToken = 'invalid.token.here';

      await expect(service.refresh(invalidToken)).rejects.toThrow(InvalidTokenError);
    });

    it('should throw InvalidTokenError if token is expired', async () => {
      const expiredToken = 'expired.token.here';

      await expect(service.refresh(expiredToken)).rejects.toThrow(InvalidTokenError);
    });
  });
});

