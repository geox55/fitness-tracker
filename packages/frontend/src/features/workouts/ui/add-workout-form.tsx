import { useForm } from 'react-hook-form';

import { zodResolver } from '@hookform/resolvers/zod';

import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/shared/ui/kit/form';
import { Input } from '@/shared/ui/kit/input';
import { Button } from '@/shared/ui/kit/button';
import { Spinner } from '@/shared/ui/kit/spinner';

import { useCreateWorkout } from '../model/use-create-workout';
import { useExercises } from '../model/use-exercises';
import { workoutFormSchema, type WorkoutFormValues } from '../model/workout-form.schema';
import { workoutFormMessages } from './messages';

export interface AddWorkoutFormProps {
  onSuccess?: () => void;
}

export function AddWorkoutForm({ onSuccess }: AddWorkoutFormProps) {
  const t = workoutFormMessages.ru;

  const form = useForm<WorkoutFormValues>({
    resolver: zodResolver(workoutFormSchema),
    defaultValues: {
      exerciseId: '',
      weight: 0,
      reps: 0,
      sets: null,
      notes: '',
      loggedAt: '',
    },
  });

  const { exercises, isLoading: isExercisesLoading, isError: isExercisesError } = useExercises();
  const { createWorkout, isPending, errorMessage } = useCreateWorkout();

  const onSubmit = form.handleSubmit((values) => {
    const payload: WorkoutFormValues = {
      ...values,
      // Приводим loggedAt к строке в ISO-формате, если поле заполнено
      loggedAt: values.loggedAt ? new Date(values.loggedAt).toISOString() : null,
    };

    createWorkout(payload);

    if (onSuccess) {
      onSuccess();
    }
  });

  return (
    <Form {...form}>
      <form onSubmit={onSubmit} className="flex flex-col gap-4 max-w-md">
        <h2 className="text-lg font-semibold">{t.title}</h2>

        <FormField
          control={form.control}
          name="exerciseId"
          render={({ field }) => (
            <FormItem>
              <FormLabel>{t.exerciseLabel}</FormLabel>
              <FormControl>
                <select
                  {...field}
                  disabled={isExercisesLoading || isPending}
                  className="file:text-foreground placeholder:text-muted-foreground selection:bg-primary selection:text-primary-foreground dark:bg-input/30 border-input h-9 w-full min-w-0 rounded-md border bg-transparent px-3 py-1 text-base shadow-xs transition-[color,box-shadow] outline-none disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]"
                >
                  <option value="">{t.exercisePlaceholder}</option>
                  {exercises.map((exercise) => (
                    <option key={exercise.id} value={exercise.id}>
                      {exercise.name}
                    </option>
                  ))}
                </select>
              </FormControl>
              {isExercisesError && (
                <p className="text-destructive text-sm">{t.loadExercisesError}</p>
              )}
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="weight"
          render={({ field }) => (
            <FormItem>
              <FormLabel>{t.weightLabel}</FormLabel>
              <FormControl>
                <Input
                  {...field}
                  type="number"
                  step="0.5"
                  min={0}
                  disabled={isPending}
                  onChange={(event) => field.onChange(event.target.value)}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="reps"
          render={({ field }) => (
            <FormItem>
              <FormLabel>{t.repsLabel}</FormLabel>
              <FormControl>
                <Input
                  {...field}
                  type="number"
                  min={1}
                  max={100}
                  disabled={isPending}
                  onChange={(event) => field.onChange(event.target.value)}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="sets"
          render={({ field }) => (
            <FormItem>
              <FormLabel>{t.setsLabel}</FormLabel>
              <FormControl>
                <Input
                  {...field}
                  type="number"
                  min={1}
                  max={10}
                  disabled={isPending}
                  onChange={(event) => field.onChange(event.target.value || null)}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="notes"
          render={({ field }) => (
            <FormItem>
              <FormLabel>{t.notesLabel}</FormLabel>
              <FormControl>
                <Input
                  {...field}
                  type="text"
                  disabled={isPending}
                  onChange={(event) => field.onChange(event.target.value)}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="loggedAt"
          render={({ field }) => (
            <FormItem>
              <FormLabel>{t.loggedAtLabel}</FormLabel>
              <FormControl>
                <Input
                  {...field}
                  type="datetime-local"
                  disabled={isPending}
                  onChange={(event) => field.onChange(event.target.value)}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {errorMessage && <p className="text-destructive text-sm">{t.commonError}</p>}

        <Button type="submit" disabled={isPending}>
          {isPending && <Spinner />}
          {t.submit}
        </Button>
      </form>
    </Form>
  );
}

