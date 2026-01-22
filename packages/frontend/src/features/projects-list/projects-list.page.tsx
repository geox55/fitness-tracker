import { href, Link } from 'react-router';

import { ExternalLinkIcon } from 'lucide-react';

import { rqClient } from '@/shared/api/instance';
import { ROUTES } from '@/shared/model/routes';
import {
  Card,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/shared/ui/kit/card';

import { CreateProjectForm } from './create-project-form';
import { DeleteProjectButton } from './delete-project-button';

function ProjectsListPage() {
  const projectsQuery = rqClient.useQuery('get', '/projects');

  return (
    <main className="grow container mx-auto p-4 flex flex-col gap-4">
      <h1 className="text-2xl font-bold">Projects list</h1>
      <CreateProjectForm />
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {projectsQuery.data?.map((project) => (
          <Card key={project.id}>
            <CardHeader className="flex items-center justify-between">
              <CardTitle>{project.name}</CardTitle>
              <Link to={href(ROUTES.PROJECT, { projectId: project.id })}>
                <ExternalLinkIcon className="size-4 text-muted-foreground" />
              </Link>
            </CardHeader>
            <CardFooter>
              <DeleteProjectButton projectId={project.id} />
            </CardFooter>
          </Card>
        ))}
      </div>
    </main>
  );
}

export const Component = ProjectsListPage;
