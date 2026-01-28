import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/kit/card';

import { useWorkouts } from '../model/use-workouts';

function formatWorkoutDate(date: string | null | undefined) {
  if (!date) return '';
  const d = new Date(date);
  if (Number.isNaN(d.getTime())) return '';
  return d.toLocaleString();
}

export function WorkoutList() {
  const { workouts, total, isLoading, isError } = useWorkouts();

  if (isLoading) {
    return (
      <Card>
        <CardContent className="py-6 text-center text-muted-foreground">
          Загрузка тренировок...
        </CardContent>
      </Card>
    );
  }

  if (isError) {
    return (
      <Card>
        <CardContent className="py-6 text-center text-destructive">
          Не удалось загрузить тренировки. Попробуйте обновить страницу.
        </CardContent>
      </Card>
    );
  }

  if (!total) {
    return (
      <Card>
        <CardContent className="py-12 text-center text-muted-foreground">
          Пока нет тренировок. Добавьте первую тренировку с помощью формы выше.
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {workouts.map((workout) => (
        <Card key={workout.id}>
          <CardHeader className="flex flex-row items-center justify-between gap-4">
            <CardTitle className="text-base font-semibold">
              Тренировка
            </CardTitle>
            <div className="text-xs text-muted-foreground">
              {formatWorkoutDate(workout.loggedAt ?? workout.createdAt)}
            </div>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-4 md:grid-cols-4">
            <div>
              <p className="text-xs text-muted-foreground">Вес</p>
              <p className="font-medium">
                {workout.weight}
                {' '}
                кг
              </p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Повторения</p>
              <p className="font-medium">{workout.reps}</p>
            </div>
            {workout.sets != null && (
              <div>
                <p className="text-xs text-muted-foreground">Подходы</p>
                <p className="font-medium">{workout.sets}</p>
              </div>
            )}
            {workout.notes && (
              <div className="md:col-span-2">
                <p className="text-xs text-muted-foreground">Заметки</p>
                <p className="text-sm">{workout.notes}</p>
              </div>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

