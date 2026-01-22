import { useQueryClient } from '@tanstack/react-query';
import { TrashIcon } from 'lucide-react';

import { rqClient } from '@/shared/api/instance';
import { Button } from '@/shared/ui/kit/button';

export function DeleteProjectButton({ projectId }: { projectId: string; }) {
  const queryClient = useQueryClient();

  const deleteProjectMutation = rqClient.useMutation('delete', '/projects/{projectId}', {
    onSettled: async () => {
      await queryClient.invalidateQueries(rqClient.queryOptions('get', '/projects'));
    },
  });

  return (
    <Button
      variant="destructive"
      size="icon"
      disabled={deleteProjectMutation.isPending}
      onClick={() => deleteProjectMutation.mutate({
        params: {
          path: {
            projectId,
          },
        },
      })}
    >
      <TrashIcon className="size-4" />
    </Button>
  );
}
