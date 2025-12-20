import { DatabaseManager } from '../db/database.js';
import type { User } from '@fitness/shared';

export class UserRepository {
  private db = DatabaseManager.getInstance();

  /**
   * Creates a new user in the database
   * @param email - User email address (should be normalized to lowercase)
   * @param passwordHash - Bcrypt hashed password
   * @returns Created user object
   * @throws {Error} If email already exists (UNIQUE constraint) or other database errors
   */
  async create(email: string, passwordHash: string): Promise<User> {
    const id = crypto.randomUUID();
    const now = new Date().toISOString();

    try {
      this.db
        .prepare(
          `INSERT INTO users (id, email, password_hash, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?)`
        )
        .run(id, email, passwordHash, now, now);

      return {
        id,
        email,
        passwordHash,
        createdAt: now,
        updatedAt: now,
      };
    } catch (error: unknown) {
      // Handle unique constraint violation (race condition or duplicate)
      if (
        error !== null &&
        typeof error === 'object' &&
        ('code' in error || 'message' in error)
      ) {
        const errorCode = 'code' in error ? String(error.code) : '';
        const errorMessage =
          'message' in error && typeof error.message === 'string'
            ? error.message
            : '';

        if (
          errorCode === 'SQLITE_CONSTRAINT_UNIQUE' ||
          errorMessage.includes('UNIQUE constraint')
        ) {
          throw new Error('Email already exists');
        }
      }
      // Re-throw other database errors
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      throw new Error(`Database error: ${errorMessage}`);
    }
  }

  private mapRowToUser(row: {
    id: string;
    email: string;
    passwordHash: string;
    createdAt: string;
    updatedAt: string;
  }): User {
    return {
      id: row.id,
      email: row.email,
      passwordHash: row.passwordHash,
      createdAt: row.createdAt,
      updatedAt: row.updatedAt,
    };
  }

  /**
   * Finds a user by email address
   * @param email - User email address (should be normalized to lowercase)
   * @returns User object if found, null if not found
   * @throws {Error} If database is not initialized or other database errors occur
   */
  async findByEmail(email: string): Promise<User | null> {
    try {
      const row = this.db
        .prepare(`SELECT id, email, password_hash as passwordHash, created_at as createdAt, updated_at as updatedAt
                   FROM users WHERE email = ?`)
        .get(email) as
        | {
            id: string;
            email: string;
            passwordHash: string;
            createdAt: string;
            updatedAt: string;
          }
        | undefined;

      if (!row) {
        return null;
      }

      return this.mapRowToUser(row);
    } catch (error: unknown) {
      // If table doesn't exist, it's a configuration issue
      if (
        error !== null &&
        typeof error === 'object' &&
        'message' in error &&
        typeof error.message === 'string' &&
        error.message.includes('no such table')
      ) {
        throw new Error('Database not initialized. Run migrations first.');
      }
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      throw new Error(
        `Database error while finding user by email: ${errorMessage}`
      );
    }
  }

  /**
   * Finds a user by ID
   * @param id - User UUID
   * @returns User object if found, null if not found
   * @throws {Error} If database is not initialized or other database errors occur
   */
  async findById(id: string): Promise<User | null> {
    try {
      const row = this.db
        .prepare(`SELECT id, email, password_hash as passwordHash, created_at as createdAt, updated_at as updatedAt
                   FROM users WHERE id = ?`)
        .get(id) as
        | {
            id: string;
            email: string;
            passwordHash: string;
            createdAt: string;
            updatedAt: string;
          }
        | undefined;

      if (!row) {
        return null;
      }

      return this.mapRowToUser(row);
    } catch (error: unknown) {
      // If table doesn't exist, it's a configuration issue
      if (
        error !== null &&
        typeof error === 'object' &&
        'message' in error &&
        typeof error.message === 'string' &&
        error.message.includes('no such table')
      ) {
        throw new Error('Database not initialized. Run migrations first.');
      }
      const errorMessage =
        error instanceof Error ? error.message : 'Unknown error';
      throw new Error(`Database error while finding user by id: ${errorMessage}`);
    }
  }
}

