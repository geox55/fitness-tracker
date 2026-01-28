import { AddWorkoutForm } from '@/features/workouts';
import { WorkoutList } from '@/features/workouts/ui/workout-list';
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/kit/card';

function WorkoutsPage() {
  return (
    <main className="grow container mx-auto px-4 py-6 max-w-4xl flex flex-col gap-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold tracking-tight">Мои тренировки</h1>
        <p className="text-sm text-muted-foreground">
          Логируйте свои силовые тренировки и отслеживайте прогресс.
        </p>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>Добавить тренировку</CardTitle>
        </CardHeader>
        <CardContent>
          <AddWorkoutForm />
        </CardContent>
      </Card>

      <section aria-label="История тренировок">
        <WorkoutList />
      </section>
    </main>
  );
}

export const Component = WorkoutsPage;

