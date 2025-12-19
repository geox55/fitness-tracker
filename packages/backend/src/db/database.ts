import Database from 'better-sqlite3';
import path from 'path';
import fs from 'fs';

export class DatabaseManager {
  private static instance: Database.Database | null = null;

  static getInstance(): Database.Database {
    if (!DatabaseManager.instance) {
      const dbPath = process.env.DATABASE_PATH || './data/fitness.db';
      const dbDir = path.dirname(dbPath);

      // Ensure directory exists
      if (!fs.existsSync(dbDir)) {
        fs.mkdirSync(dbDir, { recursive: true });
      }

      DatabaseManager.instance = new Database(dbPath);
      DatabaseManager.instance.pragma('journal_mode = WAL');
      DatabaseManager.instance.pragma('foreign_keys = ON');
      DatabaseManager.instance.pragma('busy_timeout = 5000');
    }

    return DatabaseManager.instance;
  }

  static close(): void {
    if (DatabaseManager.instance) {
      DatabaseManager.instance.close();
      DatabaseManager.instance = null;
    }
  }
}

