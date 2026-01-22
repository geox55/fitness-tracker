import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { RouterProvider } from 'react-router';

import { router } from './router';

import './main.css';

async function enableMocking() {
  if (import.meta.env.MODE === 'production') {
    return;
  }

  const { worker } = await import('@/shared/api/mocks/browser');
  return worker.start();
}

const root = document.querySelector('#root');

if (root) {
  enableMocking().then(() => {
    createRoot(root).render(
      <StrictMode>
        <RouterProvider router={router} />
      </StrictMode>,
    );
  });
}
