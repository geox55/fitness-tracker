import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { Component as WorkoutsPage } from '../workouts.page';

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return function Wrapper({ children }: { children: React.ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  };
}

describe('WorkoutsPage', () => {
  it('renders header and add workout form', () => {
    render(<WorkoutsPage />, { wrapper: createWrapper() });

    expect(screen.getByRole('heading', { name: /мои тренировки/i })).toBeInTheDocument();
    expect(screen.getByText(/добавить тренировку/i)).toBeInTheDocument();
  });

  it('shows empty state when there are no workouts', async () => {
    render(<WorkoutsPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(
        screen.getByText(/пока нет тренировок/i),
      ).toBeInTheDocument();
    });
  });
}

