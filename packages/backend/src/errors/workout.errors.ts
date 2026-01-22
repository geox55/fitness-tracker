export class InvalidWeightError extends Error {
  constructor(message = 'Weight must be positive') {
    super(message);
    this.name = 'InvalidWeightError';
  }
}

export class InvalidRepsError extends Error {
  constructor(message = 'Reps must be between 1 and 100') {
    super(message);
    this.name = 'InvalidRepsError';
  }
}

export class WorkoutNotFoundError extends Error {
  constructor(message = 'Workout not found') {
    super(message);
    this.name = 'WorkoutNotFoundError';
  }
}

export class WorkoutAccessDeniedError extends Error {
  constructor(message = 'Access denied to this workout') {
    super(message);
    this.name = 'WorkoutAccessDeniedError';
  }
}

export class InvalidSetsError extends Error {
  constructor(message = 'Sets must be between 1 and 10') {
    super(message);
    this.name = 'InvalidSetsError';
  }
}

