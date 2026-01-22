// User types
export interface User {
  id: string;
  email: string;
  passwordHash: string;
  createdAt: string;
  updatedAt: string;
}

// Exercise types
export interface Exercise {
  id: string;
  name: string;
  category: string;
  muscleGroups: string[];
  createdBy?: string; // userId создателя (null для системных)
  status: 'pending' | 'approved' | 'rejected'; // Статус модерации
  approvedBy?: string; // userId администратора, подтвердившего
  approvedAt?: string;
  createdAt: string;
}

// Workout types
export interface WorkoutLog {
  id: string;
  userId: string;
  exerciseId: string;
  weight: number;
  reps: number;
  sets: number;
  notes?: string;
  loggedAt: string;
  createdAt: string;
  updatedAt: string;
}

export interface WorkoutInput {
  exerciseId: string;
  weight: number;
  reps: number;
  sets?: number;
  notes?: string;
  loggedAt?: string;
}

export interface WorkoutFilters {
  exerciseId?: string;
  startDate?: string;
  endDate?: string;
  limit?: number;
  offset?: number;
}

// Analytics types
export interface ProgressData {
  date: string;
  weight: number;
  reps: number;
  volume: number;
}

export interface ProgressStats {
  maxWeight: number;
  avgWeight: number;
  maxReps: number;
  avgReps: number;
  totalVolume: number;
  personalRecord: boolean;
}

// Template types
export interface WorkoutTemplate {
  id: string;
  userId: string;
  name: string;
  exercises: TemplateExercise[];
  createdAt: string;
  updatedAt: string;
}

export interface TemplateExercise {
  exerciseId: string;
  sets: number;
  targetReps?: number;
  targetWeight?: number;
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface ApiError {
  error: string;
  details?: unknown;
  code?: string;
}

// Auth types
export interface LoginInput {
  email: string;
  password: string;
}

export interface RegisterInput {
  email: string;
  password: string;
  passwordConfirm: string;
}

export interface AuthResponse {
  token: string;
  user: {
    id: string;
    email: string;
  };
}

// Workout Session types
export interface WorkoutSession {
  id: string;
  userId: string;
  loggedAt: string; // Дата тренировки (ISO datetime)
  duration?: number; // Длительность в минутах (опционально)
  notes?: string; // Общие заметки к тренировке
  exercises: WorkoutExercise[]; // Список упражнений
  createdAt: string;
  updatedAt: string;
}

export interface WorkoutExercise {
  id: string;
  exerciseId: string; // ID из таблицы exercises
  exerciseName: string; // Кэшированное имя для быстрого отображения
  order: number; // Порядок выполнения в тренировке
  isSuperset: boolean; // Является ли частью суперсета
  supersetId?: string; // ID суперсета, если упражнение в суперсете
  sets: ExerciseSet[]; // Список подходов
  warmupSets?: WarmupSet[]; // Разминочные подходы (опционально)
  machineSettings?: MachineSettings; // Настройки тренажера (опционально)
  notes?: string; // Заметки к упражнению
}

export interface ExerciseSet {
  setNumber: number; // Номер подхода (1, 2, 3...)
  weight: number; // Вес в кг
  reps: number; // Количество повторений
  rpe?: number; // RPE 1-10 (опционально)
  restTime?: number; // Время отдыха в секундах (опционально)
}

export interface WarmupSet {
  setNumber: number;
  weight: number;
  reps: number;
  percentage?: number; // Процент от рабочего веса (опционально)
}

export interface MachineSettings {
  seatHeight?: number; // Высота сиденья (см или позиция)
  footPlacement?: string; // Позиция ног (текст или enum)
  backAngle?: number; // Угол спинки (градусы)
  gripWidth?: string; // Ширина хвата (узкий/средний/широкий)
  customSettings?: Record<string, string | number>; // Дополнительные настройки
}

export interface Superset {
  id: string;
  exerciseIds: string[]; // ID упражнений в суперсете
  sets: SupersetSet[]; // Подходы суперсета
  restTime?: number; // Время отдыха между суперсетами
}

export interface SupersetSet {
  setNumber: number;
  exercises: SupersetExerciseData[]; // Данные для каждого упражнения в подходе
}

export interface SupersetExerciseData {
  exerciseId: string;
  weight: number;
  reps: number;
  rpe?: number;
}

// Workout Session Input types
export interface WorkoutSessionInput {
  loggedAt: string;
  duration?: number;
  notes?: string;
  exercises: WorkoutExerciseInput[];
}

export interface WorkoutExerciseInput {
  exerciseId: string;
  sets: ExerciseSetInput[];
  warmupSets?: WarmupSetInput[];
  machineSettings?: MachineSettings;
  notes?: string;
}

export interface ExerciseSetInput {
  weight: number;
  reps: number;
  rpe?: number;
  restTime?: number;
}

export interface WarmupSetInput {
  weight: number;
  reps: number;
  percentage?: number;
}

export interface SupersetInput {
  exerciseIds: string[];
  sets: SupersetSetInput[];
  restTime?: number;
}

export interface SupersetSetInput {
  exercises: SupersetExerciseDataInput[];
}

export interface SupersetExerciseDataInput {
  exerciseId: string;
  weight: number;
  reps: number;
  rpe?: number;
}

export interface ExerciseInput {
  name: string;
  category: string;
  muscleGroups: string[];
}

