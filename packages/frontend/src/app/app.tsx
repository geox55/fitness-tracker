import { Outlet } from 'react-router';

import { AppHeader } from '@/features/header';

export function App() {
  return (
    <div className="flex flex-col min-h-screen">
      <AppHeader />
      <Outlet />
    </div>
  );
};
