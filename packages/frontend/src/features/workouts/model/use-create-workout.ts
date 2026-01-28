import { rqClient } from '@/shared/api/instance';
import type { ApiSchemas } from '@/shared/api/schema';
import { useQueryClient } from '@tanstack/react-query';

export function useCreateWorkout() {
  const queryClient = useQueryClient();

  const mutation = rqClient.useMutation('post', '/workouts', {
    onSuccess: async () => {
      await queryClient.invalidateQueries(rqClient.queryOptions('get', '/workouts'));
    },
  });

  const createWorkout = (body: ApiSchemas['CreateWorkoutRequest']) => {
    mutation.mutate({ body });
  };

  const errorMessage = mutation.isError ? mutation.error.message : undefined;

  return {
    createWorkout,
    isPending: mutation.isPending,
    errorMessage,
  };
}

