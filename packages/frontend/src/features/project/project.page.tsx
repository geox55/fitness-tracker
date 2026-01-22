import { useParams } from 'react-router';

import { rqClient } from '@/shared/api/instance';
import type { PathParams, ROUTES } from '@/shared/model/routes';

function ProjectPage() {
  const params = useParams<PathParams[typeof ROUTES.PROJECT]>();

  const projectQuery = rqClient.useQuery('get', '/projects/{projectId}', {
    params: {
      path: {
        projectId: params.projectId ?? '',
      },
    },
  });

  return (
    <main className="grow container mx-auto p-4 flex flex-col gap-4">
      <h1 className="text-2xl font-bold">{projectQuery.data?.name}</h1>
    </main>
  );
}

export const Component = ProjectPage;
