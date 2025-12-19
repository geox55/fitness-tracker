import { DatabaseManager } from '../db/database.js';
import type { User } from '@fitness/shared';

export class UserRepository {
  private db = DatabaseManager.getInstance();

  async create(email: string, passwordHash: string): Promise<User> {
    const id = crypto.randomUUID();
    const now = new Date().toISOString();

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
  }

  async findByEmail(email: string): Promise<User | null> {
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

    return {
      id: row.id,
      email: row.email,
      passwordHash: row.passwordHash,
      createdAt: row.createdAt,
      updatedAt: row.updatedAt,
    };
  }

  async findById(id: string): Promise<User | null> {
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

    return {
      id: row.id,
      email: row.email,
      passwordHash: row.passwordHash,
      createdAt: row.createdAt,
      updatedAt: row.updatedAt,
    };
  }
}

