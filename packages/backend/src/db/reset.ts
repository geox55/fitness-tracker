import { DatabaseManager } from './database.js';
import fs from 'fs';
import path from 'path';

const db = DatabaseManager.getInstance();
const dbPath = process.env.DATABASE_PATH || './data/fitness.db';

// Drop all tables
db.exec(`
  DROP TABLE IF EXISTS workout_templates;
  DROP TABLE IF EXISTS analytics_aggregates;
  DROP TABLE IF EXISTS workout_logs;
  DROP TABLE IF EXISTS exercises;
  DROP TABLE IF EXISTS users;
`);

console.log('✅ Database reset completed');

// Optionally delete database file
if (process.argv.includes('--delete-file')) {
  DatabaseManager.close();
  if (fs.existsSync(dbPath)) {
    fs.unlinkSync(dbPath);
    console.log('🗑️  Database file deleted');
  }
} else {
  DatabaseManager.close();
}

