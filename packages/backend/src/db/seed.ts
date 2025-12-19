import { DatabaseManager } from './database.js';
import { randomUUID } from 'crypto';

const db = DatabaseManager.getInstance();

// Seed exercises
const exercises = [
  { name: 'Squat', category: 'Strength', muscleGroups: JSON.stringify(['Legs', 'Core']) },
  { name: 'Bench Press', category: 'Strength', muscleGroups: JSON.stringify(['Chest', 'Arms']) },
  { name: 'Deadlift', category: 'Strength', muscleGroups: JSON.stringify(['Back', 'Legs']) },
  { name: 'Overhead Press', category: 'Strength', muscleGroups: JSON.stringify(['Shoulders', 'Arms']) },
  { name: 'Pull-ups', category: 'Strength', muscleGroups: JSON.stringify(['Back', 'Arms']) },
];

const insertExercise = db.prepare(`
  INSERT INTO exercises (id, name, category, muscle_groups)
  VALUES (?, ?, ?, ?)
`);

exercises.forEach((exercise) => {
  insertExercise.run(randomUUID(), exercise.name, exercise.category, exercise.muscleGroups);
});

console.log(`✅ Seeded ${exercises.length} exercises`);
DatabaseManager.close();

