import { Navigate, Outlet } from 'react-router';

import { ROUTES } from '@/shared/model/routes';
import { useSession } from '@/shared/model/session';

export function ProtectedRoute() {
  const { session } = useSession();

  if (!session) {
    return <Navigate to={ROUTES.LOGIN} />;
  }

  return <Outlet />;
}
