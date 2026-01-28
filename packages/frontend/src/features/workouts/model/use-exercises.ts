import { rqClient } from '@/shared/api/instance';

export function useExercises() {
  const query = rqClient.useQuery('get', '/exercises');

  const exercises = Array.isArray(query.data)
    ? [...query.data].sort((a, b) => a.name.localeCompare(b.name))
    : [];

  return {
    exercises,
    isLoading: query.isLoading,
    isError: query.isError,
  };
}

