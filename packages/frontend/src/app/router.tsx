import { createBrowserRouter, redirect } from 'react-router';

import { ROUTES } from '@/shared/model/routes';

import { ProtectedRoute } from './protected-toute';
import { RootErrorBoundary } from './root-error-boundary';
import { App } from './app';
import { Providers } from './providers';

export const router = createBrowserRouter([
  {
    element: (
      <Providers>
        <App />
      </Providers>
    ),
    ErrorBoundary: RootErrorBoundary,
    children: [
      {
        element: <ProtectedRoute />,
        children: [
          {
            path: ROUTES.PROJECTS,
            lazy: () => import('@/features/projects-list/projects-list.page'),
          },
          {
            path: ROUTES.PROJECT,
            lazy: () => import('@/features/project/project.page'),
          },
        ],
      },
      {
        path: ROUTES.LOGIN,
        lazy: () => import('@/features/auth/login.page'),
      },
      {
        path: ROUTES.REGISTER,
        lazy: () => import('@/features/auth/register.page'),
      },
      {
        path: ROUTES.HOME,
        loader: () => redirect(ROUTES.PROJECTS),
      },
    ],
  },
]);
