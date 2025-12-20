import { ZodError } from 'zod';

interface ErrorWithName extends Error {
  name: string;
}

export function isZodError(err: unknown): err is ZodError {
  return (
    err instanceof ZodError ||
    (err !== null &&
      typeof err === 'object' &&
      'name' in err &&
      (err as ErrorWithName).name === 'ZodError')
  );
}

export function sanitizeErrorForLogging(err: unknown): {
  error: string;
  stack?: string;
  name: string;
} {
  if (err instanceof Error) {
    return {
      error: err.message,
      stack: process.env.NODE_ENV === 'development' ? err.stack : undefined,
      name: err.name,
    };
  }
  return {
    error: String(err),
    name: 'UnknownError',
  };
}

