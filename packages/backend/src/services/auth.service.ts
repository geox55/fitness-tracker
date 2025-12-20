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

  /**
   * Registers a new user with email and password
   * @param email - User email address (will be normalized to lowercase)
   * @param password - User password (min 8 characters)
   * @returns Authentication response with JWT token and user data
   * @throws {EmailAlreadyExistsError} If email is already registered
   * @throws {Error} For other registration failures
   */
  async register(email: string, password: string): Promise<AuthResponse> {
    // Normalize email to lowercase
    const normalizedEmail = email.toLowerCase().trim();

    // Try to create user directly - UNIQUE constraint in DB will prevent duplicates
    // This eliminates race condition between findByEmail check and create
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
      // Handle unique constraint violation (race condition or duplicate)
      if (error instanceof Error && error.message === 'Email already exists') {
        throw new EmailAlreadyExistsError();
      }
      throw error;
    }
  }

  /**
   * Authenticates a user with email and password
   * @param email - User email address (will be normalized to lowercase)
   * @param password - User password
   * @returns Authentication response with JWT token and user data
   * @throws {InvalidCredentialsError} If email or password is incorrect
   */
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

  /**
   * Refreshes a JWT token
   * @param token - Valid JWT token to refresh
   * @returns New JWT token
   * @throws {InvalidTokenError} If token is invalid, expired, or user not found
   */
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

