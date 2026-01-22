import { delay, HttpResponse } from 'msw';

import type { ApiSchemas } from '../../schema';
import { http } from '../http';

const projects: ApiSchemas['Project'][] = Array.from({ length: 10 }, (_, i) => ({
  id: crypto.randomUUID(),
  name: `Project ${i + 1}`,
}));

export const projectHandlers = [
  http.get('/projects', () => {
    return HttpResponse.json(projects);
  }),
  http.post('/projects', async (ctx) => {
    const body = await ctx.request.json();

    await delay(1000);

    const project = {
      id: crypto.randomUUID(),
      name: body.name,
    };
    projects.push(project);
    return HttpResponse.json(project, { status: 201 });
  }),
  http.get('/projects/{projectId}', (ctx) => {
    const projectId = ctx.params.projectId;
    const project = projects.find((project) => project.id === projectId);
    if (!project) {
      return HttpResponse.json({ message: 'Project not found', code: 'NOT_FOUND' }, { status: 404 });
    }
    return HttpResponse.json(project);
  }),
  http.delete('/projects/{projectId}', async (ctx) => {
    const projectId = ctx.params.projectId;
    const index = projects.findIndex((project) => project.id === projectId);

    await delay(1000);

    if (index === -1) {
      return HttpResponse.json({ message: 'Project not found', code: 'NOT_FOUND' }, { status: 404 });
    }
    projects.splice(index, 1);
    return HttpResponse.json(null, { status: 204 });
  }),
];
