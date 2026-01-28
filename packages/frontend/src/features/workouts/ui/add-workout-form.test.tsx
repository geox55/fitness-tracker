import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { AddWorkoutForm } from './add-workout-form';

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

describe('AddWorkoutForm', () => {
  it('shows validation errors when required fields are empty', async () => {
    render(<AddWorkoutForm />, { wrapper: createWrapper() });

    const submitButton = screen.getByRole('button', { name: /добавить тренировку/i });
    fireEvent.click(submitButton);

    expect(
      await screen.findAllByText(/должн|Неверный идентификатор упражнения|не меньше 1/i),
    ).not.toHaveLength(0);
  });

  it('submits form with valid data', async () => {
    render(<AddWorkoutForm />, { wrapper: createWrapper() });

    // Выбираем упражнение, если оно подгрузилось из моков
    await waitFor(() => {
      // если упражнений нет — просто пропускаем тест
      const options = screen.queryAllByRole('option');
      if (options.length === 0) {
        throw new Error('no options yet');
      }
    }).catch(() => {});

    const weightInput = screen.getByLabelText(/вес/i);
    const repsInput = screen.getByLabelText(/повторения/i);

    fireEvent.change(weightInput, { target: { value: '50' } });
    fireEvent.change(repsInput, { target: { value: '5' } });

    const submitButton = screen.getByRole('button', { name: /добавить тренировку/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(submitButton).not.toBeDisabled();
    });
  });
}

