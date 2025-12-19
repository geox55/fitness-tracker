import { DatabaseManager } from '../db/database.js';
import type { User } from '@fitness/shared';

export class UserRepository {
  private db = DatabaseManager.getInstance();

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
    } catch (error: any) {
      // Handle unique constraint violation (race condition)
      if (error?.code === 'SQLITE_CONSTRAINT_UNIQUE' || error?.message?.includes('UNIQUE constraint')) {
        throw new Error('Email already exists');
      }
      // Re-throw other database errors
      throw new Error(`Database error: ${error?.message || 'Unknown error'}`);
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
    } catch (error: any) {
      // If table doesn't exist, it's a setup issue - return null instead of throwing
      if (error?.message?.includes('no such table')) {
        return null;
      }
      throw new Error(`Database error while finding user by email: ${error?.message || 'Unknown error'}`);
    }
  }

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
    } catch (error: any) {
      // If table doesn't exist, it's a setup issue - return null instead of throwing
      if (error?.message?.includes('no such table')) {
        return null;
      }
      throw new Error(`Database error while finding user by id: ${error?.message || 'Unknown error'}`);
    }
  }
}

