import bcrypt from 'bcryptjs';
import { UserRepository } from '../repositories/user.repository.js';
import { signToken, verifyToken, type JWTPayload } from '../utils/jwt.js';
import { loginSchema, type AuthResponse } from '@fitness/shared';

export class AuthService {
  private userRepository = new UserRepository();
  private readonly BCRYPT_ROUNDS = 10;

  async register(email: string, password: string): Promise<AuthResponse> {

    const existingUser = await this.userRepository.findByEmail(email);
    if (existingUser) {
      throw new Error('Email already exists');
    }

    const passwordHash = await bcrypt.hash(password, this.BCRYPT_ROUNDS);
    const user = await this.userRepository.create(email, passwordHash);

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

  async login(email: string, password: string): Promise<AuthResponse> {
    loginSchema.parse({ email, password });

    const user = await this.userRepository.findByEmail(email);
    if (!user) {
      throw new Error('Invalid credentials');
    }

    const isPasswordValid = await bcrypt.compare(password, user.passwordHash);
    if (!isPasswordValid) {
      throw new Error('Invalid credentials');
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
    const payload = await verifyToken(token);

    const user = await this.userRepository.findById(payload.userId);
    if (!user) {
      throw new Error('Invalid token');
    }

    const newToken = await signToken({
      userId: user.id,
      email: user.email,
    });

    return { token: newToken };
  }
}

