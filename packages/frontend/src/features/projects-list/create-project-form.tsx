import { useForm } from 'react-hook-form';

import { zodResolver } from '@hookform/resolvers/zod';
import { useQueryClient } from '@tanstack/react-query';
import z from 'zod';

import { rqClient } from '@/shared/api/instance';
import { Button } from '@/shared/ui/kit/button';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/shared/ui/kit/form';
import { Input } from '@/shared/ui/kit/input';
import { Spinner } from '@/shared/ui/kit/spinner';

const createProjectSchema = z.object({
  name: z.string().min(1, 'Название проекта является обязательным'),
});

export function CreateProjectForm() {
  const queryClient = useQueryClient();

  const form = useForm({
    resolver: zodResolver(createProjectSchema),
    defaultValues: {
      name: '',
    },
  });

  const createProjectMutation = rqClient.useMutation('post', '/projects', {
    onSuccess: () => {
      form.reset();
    },
    onSettled: async () => {
      await queryClient.invalidateQueries(rqClient.queryOptions('get', '/projects'));
    },
  });

  const onSubmit = form.handleSubmit((body) => {
    createProjectMutation.mutate({ body });
  });

  return (
    <Form {...form}>
      <form onSubmit={onSubmit} className="flex flex-col gap-2 w-full max-w-[400px]">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Project name</FormLabel>
              <FormControl>
                <Input
                  {...field}
                  disabled={createProjectMutation.isPending}
                  placeholder="Мой проект"
                  autoComplete="off"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" disabled={createProjectMutation.isPending}>
          {createProjectMutation.isPending && <Spinner />}
          Create project
        </Button>
      </form>
    </Form>
  );
}
