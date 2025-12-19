import { describe, it, expect, beforeEach } from 'vitest';
import { AuthService } from '../../src/services/auth.service.js';

describe('AuthService', () => {
  let service: AuthService;

  beforeEach(() => {
    service = new AuthService();
  });

  describe('register', () => {
    it('should successfully register a new user', async () => {
      const email = `test-${Date.now()}@example.com`;
      const password = 'password123';

      const result = await service.register(email, password);

      expect(result).toHaveProperty('token');
      expect(result).toHaveProperty('user');
      expect(result.user.email).toBe(email);
      expect(result.user).toHaveProperty('id');
    });

    it('should throw error if email already exists', async () => {
      const email = `existing-${Date.now()}@example.com`;
      const password = 'password123';

      await service.register(email, password);

      await expect(service.register(email, password)).rejects.toThrow('Email already exists');
    });

    it('should hash password before storing', async () => {
      const email = `test2-${Date.now()}@example.com`;
      const password = 'password123';

      const result = await service.register(email, password);

      expect(result.token).toBeTruthy();
      expect(result.user.email).toBe(email);
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
      expect(result.user.email).toBe(email);
    });

    it('should throw error if email does not exist', async () => {
      const email = 'nonexistent@example.com';
      const password = 'password123';

      await expect(service.login(email, password)).rejects.toThrow('Invalid credentials');
    });

    it('should throw error if password is incorrect', async () => {
      const email = `wrongpass-${Date.now()}@example.com`;
      const password = 'password123';
      const wrongPassword = 'wrongpassword';

      await service.register(email, password);

      await expect(service.login(email, wrongPassword)).rejects.toThrow('Invalid credentials');
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

    it('should throw error if token is invalid', async () => {
      const invalidToken = 'invalid.token.here';

      await expect(service.refresh(invalidToken)).rejects.toThrow('Invalid token');
    });

    it('should throw error if token is expired', async () => {
      const expiredToken = 'expired.token.here';

      await expect(service.refresh(expiredToken)).rejects.toThrow('Invalid token');
    });
  });
});

