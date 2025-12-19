import bcrypt from 'bcryptjs';
import { UserRepository } from '../repositories/user.repository.js';
import { signToken, verifyToken, type JWTPayload } from '../utils/jwt.js';
import { loginSchema, type AuthResponse } from '@fitness/shared';
import {
  EmailAlreadyExistsError,
  InvalidCredentialsError,
  InvalidTokenError,
} from '../errors/auth.errors.js';
import { BCRYPT_ROUNDS } from '../constants/index.js';

export class AuthService {
  private userRepository = new UserRepository();

  async register(email: string, password: string): Promise<AuthResponse> {
    // Normalize email to lowercase
    const normalizedEmail = email.toLowerCase().trim();

    const existingUser = await this.userRepository.findByEmail(normalizedEmail);
    if (existingUser) {
      throw new EmailAlreadyExistsError();
    }

    try {
      const passwordHash = await bcrypt.hash(password, BCRYPT_ROUNDS);
      const user = await this.userRepository.create(normalizedEmail, passwordHash);

      const token = await signToken({
        userId: user.id,
        email: user.email,
      });

      return {
        token,
        user: {
          id: user.id,
          email: user.email,
        },
      };
    } catch (error) {
      // Handle race condition - if email already exists due to concurrent requests
      if (error instanceof Error && error.message === 'Email already exists') {
        throw new EmailAlreadyExistsError();
      }
      throw error;
    }
  }

  async login(email: string, password: string): Promise<AuthResponse> {
    // Normalize email to lowercase
    const normalizedEmail = email.toLowerCase().trim();

    const user = await this.userRepository.findByEmail(normalizedEmail);
    if (!user) {
      throw new InvalidCredentialsError();
    }

    const isPasswordValid = await bcrypt.compare(password, user.passwordHash);
    if (!isPasswordValid) {
      throw new InvalidCredentialsError();
    }

    const token = await signToken({
      userId: user.id,
      email: user.email,
    });

    return {
      token,
      user: {
        id: user.id,
        email: user.email,
      },
    };
  }

  async refresh(token: string): Promise<{ token: string }> {
    try {
      const payload = await verifyToken(token);

      const user = await this.userRepository.findById(payload.userId);
      if (!user) {
        throw new InvalidTokenError();
      }

      const newToken = await signToken({
        userId: user.id,
        email: user.email,
      });

      return { token: newToken };
    } catch (error) {
      if (error instanceof InvalidTokenError) {
        throw error;
      }
      throw new InvalidTokenError();
    }
  }
}

