import { rqClient } from '@/shared/api/instance';
import type { ApiPaths, ApiSchemas } from '@/shared/api/schema';

type WorkoutsQueryParams = ApiPaths['/workouts']['get']['parameters']['query'];

type WorkoutListResponse = ApiSchemas['WorkoutListResponse'];

export function useWorkouts(params?: WorkoutsQueryParams) {
  const query = rqClient.useQuery('get', '/workouts', {
    query: params,
  });

  const data: WorkoutListResponse | undefined = query.data;

  return {
    workouts: data?.items ?? [],
    total: data?.total ?? 0,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
  };
}

