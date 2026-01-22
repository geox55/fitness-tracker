import 'react-router';

export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  PROJECTS: '/projects',
  PROJECT: '/projects/:projectId',
} as const;

export type PathParams = {
  [ROUTES.PROJECT]: {
    projectId: string;
  };
};

declare module 'react-router' {
  interface Register {
    params: PathParams;
  }
}
