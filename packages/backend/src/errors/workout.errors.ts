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

