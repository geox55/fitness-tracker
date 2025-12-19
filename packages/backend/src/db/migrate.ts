import { DatabaseManager } from './database.js';

const db = DatabaseManager.getInstance();

// Create tables
db.exec(`
  -- Users
  CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  -- Exercises master data
  CREATE TABLE IF NOT EXISTS exercises (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    muscle_groups TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );
  CREATE INDEX IF NOT EXISTS idx_exercises_name ON exercises(name);

  -- Workout logs
  CREATE TABLE IF NOT EXISTS workout_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    exercise_id TEXT NOT NULL,
    weight DECIMAL(10, 2) NOT NULL CHECK (weight > 0),
    reps INTEGER NOT NULL CHECK (reps > 0 AND reps <= 100),
    sets INTEGER DEFAULT 1 CHECK (sets > 0),
    notes TEXT,
    logged_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (exercise_id) REFERENCES exercises(id)
  );
  CREATE INDEX IF NOT EXISTS idx_workout_logs_user_date ON workout_logs(user_id, logged_at DESC);
  CREATE INDEX IF NOT EXISTS idx_workout_logs_user_exercise ON workout_logs(user_id, exercise_id);

  -- Analytics aggregates
  CREATE TABLE IF NOT EXISTS analytics_aggregates (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    exercise_id TEXT NOT NULL,
    period_date DATE NOT NULL,
    max_weight DECIMAL(10, 2),
    avg_weight DECIMAL(10, 2),
    total_volume DECIMAL(15, 2),
    personal_record DECIMAL(10, 2),
    UNIQUE (user_id, exercise_id, period_date),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (exercise_id) REFERENCES exercises(id)
  );

  -- Workout templates
  CREATE TABLE IF NOT EXISTS workout_templates (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    exercises_json TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
  );
`);

console.log('✅ Database migrations completed');
DatabaseManager.close();

