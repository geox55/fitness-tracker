import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/theme/app_spacing.dart';
import '../../data/api/failure.dart';
import '../../data/api/workouts_api.dart';
import 'workout_actions.dart';

class TrainingTabScreen extends ConsumerWidget {
  const TrainingTabScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final active = ref.watch(activeWorkoutProvider);
    final history = ref.watch(workoutHistoryProvider);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Тренировка')),
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: () async {
            ref.invalidate(activeWorkoutProvider);
            ref.invalidate(workoutHistoryProvider);
            await ref.read(activeWorkoutProvider.future);
            await ref.read(workoutHistoryProvider.future);
          },
          child: ListView(
            padding: const EdgeInsets.fromLTRB(
              AppSpacing.lg,
              AppSpacing.lg,
              AppSpacing.lg,
              AppSpacing.xxxl * 2,
            ),
            children: [
              active.when(
                loading: () => const _ActiveSkeleton(),
                error: (e, _) => _ErrorBanner(error: e),
                data: (w) => w == null
                    ? const _StartCard()
                    : _ActiveCard(workout: w),
              ),
              const SizedBox(height: AppSpacing.md),
              const _PlanCard(),
              const SizedBox(height: AppSpacing.xl),
              Text(
                'История'.toUpperCase(),
                style: theme.textTheme.labelSmall?.copyWith(
                  color: theme.colorScheme.primary,
                  letterSpacing: 1.6,
                ),
              ),
              const SizedBox(height: AppSpacing.md),
              history.when(
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (e, _) => _ErrorBanner(error: e),
                data: (items) {
                  final completed = items
                      .where((w) => w.status != 'in_progress')
                      .toList();
                  if (completed.isEmpty) {
                    return Padding(
                      padding: const EdgeInsets.all(AppSpacing.xl),
                      child: Text(
                        'Завершённых тренировок пока нет',
                        textAlign: TextAlign.center,
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                    );
                  }
                  // AutoClose: открыт может быть только один свайп за раз —
                  // типовой UX iOS Mail / TG.
                  return WorkoutActionsAutoClose(
                    child: Column(
                      children: [
                        for (final w in completed) ...[
                          _HistoryTile(workout: w),
                          const SizedBox(height: AppSpacing.sm),
                        ],
                      ],
                    ),
                  );
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _PlanCard extends StatelessWidget {
  const _PlanCard();

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Material(
      color: theme.colorScheme.surfaceContainerHigh,
      borderRadius: BorderRadius.circular(AppRadius.lg),
      child: InkWell(
        borderRadius: BorderRadius.circular(AppRadius.lg),
        onTap: () => context.push('/plan'),
        child: Container(
          padding: const EdgeInsets.all(AppSpacing.lg),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(AppRadius.lg),
            border: Border.all(color: theme.colorScheme.outline),
          ),
          child: Row(
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: theme.colorScheme.primary.withValues(alpha: 0.16),
                  borderRadius: BorderRadius.circular(AppRadius.md),
                ),
                child: Icon(
                  Icons.auto_awesome,
                  color: theme.colorScheme.primary,
                  size: 24,
                ),
              ),
              const SizedBox(width: AppSpacing.md),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Мой план', style: theme.textTheme.titleMedium),
                    Text(
                      'AI-программа на 4 недели по вашим целям',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ],
                ),
              ),
              Icon(
                Icons.chevron_right,
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _StartCard extends ConsumerWidget {
  const _StartCard();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.all(AppSpacing.xl),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHigh,
        borderRadius: BorderRadius.circular(AppRadius.lg),
        border: Border.all(color: theme.colorScheme.outline),
      ),
      child: Column(
        children: [
          Container(
            width: 72,
            height: 72,
            decoration: BoxDecoration(
              color: theme.colorScheme.primary.withValues(alpha: 0.16),
              borderRadius: BorderRadius.circular(AppRadius.lg),
            ),
            child: Icon(
              Icons.play_arrow,
              size: 40,
              color: theme.colorScheme.primary,
            ),
          ),
          const SizedBox(height: AppSpacing.lg),
          Text('Готов к новой тренировке?',
              style: theme.textTheme.titleLarge, textAlign: TextAlign.center),
          const SizedBox(height: AppSpacing.sm),
          Text(
            'Начни тренировку — сможешь добавлять упражнения и фиксировать подходы',
            style: theme.textTheme.bodyMedium?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: AppSpacing.lg),
          ElevatedButton.icon(
            onPressed: () async {
              try {
                final w = await ref.read(workoutsApiProvider).start();
                ref.invalidate(activeWorkoutProvider);
                if (!context.mounted) return;
                context.go('/training/active/${w.id}');
              } on AppFailure catch (f) {
                if (!context.mounted) return;
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text(f.message)),
                );
              }
            },
            icon: const Icon(Icons.play_arrow),
            label: const Text('Начать тренировку'),
          ),
        ],
      ),
    );
  }
}

class _ActiveCard extends StatelessWidget {
  const _ActiveCard({required this.workout});
  final WorkoutDto workout;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final elapsed = DateTime.now().toUtc().difference(workout.performedAt);
    final mins = elapsed.inMinutes;
    final hours = elapsed.inHours;
    final elapsedLabel = hours > 0 ? '$hours ч ${mins.remainder(60)} мин' : '$mins мин';

    return Container(
      padding: const EdgeInsets.all(AppSpacing.lg),
      decoration: BoxDecoration(
        color: theme.colorScheme.primary.withValues(alpha: 0.10),
        borderRadius: BorderRadius.circular(AppRadius.lg),
        border: Border.all(color: theme.colorScheme.primary.withValues(alpha: 0.4)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.bolt, color: theme.colorScheme.primary),
              const SizedBox(width: AppSpacing.sm),
              Text(
                'АКТИВНАЯ ТРЕНИРОВКА',
                style: theme.textTheme.labelSmall?.copyWith(
                  color: theme.colorScheme.primary,
                  letterSpacing: 1.6,
                ),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.sm),
          Text('Идёт уже $elapsedLabel · ${workout.logs.length} подходов',
              style: theme.textTheme.titleMedium),
          const SizedBox(height: AppSpacing.lg),
          ElevatedButton(
            onPressed: () => context.go('/training/active/${workout.id}'),
            child: const Text('Продолжить'),
          ),
        ],
      ),
    );
  }
}

class _HistoryTile extends ConsumerWidget {
  const _HistoryTile({required this.workout});
  final WorkoutSummaryDto workout;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final dur = workout.finishedAt
        ?.difference(workout.performedAt)
        .inMinutes;

    return WorkoutActionsSlidable(
      workoutId: workout.id,
      onDeleted: () {
        ref.invalidate(workoutHistoryProvider);
        ref.invalidate(activeWorkoutProvider);
      },
      borderRadius: AppRadius.lg,
      child: Material(
        color: theme.colorScheme.surfaceContainerHigh,
        borderRadius: BorderRadius.circular(AppRadius.lg),
        child: InkWell(
          onTap: workout.status == 'in_progress'
              ? () => context.go('/training/active/${workout.id}')
              : () => context.push('/training/view/${workout.id}'),
          borderRadius: BorderRadius.circular(AppRadius.lg),
          child: Container(
            padding: const EdgeInsets.symmetric(
              horizontal: AppSpacing.lg,
              vertical: AppSpacing.md,
            ),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(AppRadius.lg),
              border: Border.all(color: theme.colorScheme.outline),
            ),
            child: Row(
              children: [
                Container(
                  width: 44,
                  height: 44,
                  decoration: BoxDecoration(
                    color: theme.colorScheme.primary.withValues(alpha: 0.16),
                    borderRadius: BorderRadius.circular(AppRadius.md),
                  ),
                  child: Icon(Icons.fitness_center,
                      color: theme.colorScheme.primary, size: 22),
                ),
                const SizedBox(width: AppSpacing.md),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        _formatDate(workout.performedAt),
                        style: theme.textTheme.titleMedium,
                      ),
                      Text(
                        [
                          '${workout.setsCount} подходов',
                          if (dur != null) '$dur мин',
                        ].join(' · '),
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                    ],
                  ),
                ),
                Icon(
                  Icons.chevron_right,
                  color: theme.colorScheme.onSurfaceVariant,
                  size: 18,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  static String _formatDate(DateTime utc) {
    final local = utc.toLocal();
    const months = [
      'янв',
      'фев',
      'мар',
      'апр',
      'мая',
      'июн',
      'июл',
      'авг',
      'сен',
      'окт',
      'ноя',
      'дек',
    ];
    return '${local.day} ${months[local.month - 1]} '
        '${local.hour.toString().padLeft(2, "0")}:${local.minute.toString().padLeft(2, "0")}';
  }
}

class _ActiveSkeleton extends StatelessWidget {
  const _ActiveSkeleton();
  @override
  Widget build(BuildContext context) =>
      const Center(child: CircularProgressIndicator());
}

class _ErrorBanner extends StatelessWidget {
  const _ErrorBanner({required this.error});
  final Object error;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final msg = error is AppFailure
        ? (error as AppFailure).message
        : 'Ошибка загрузки';
    return Container(
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: theme.colorScheme.error.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(AppRadius.md),
      ),
      child: Text(msg, style: TextStyle(color: theme.colorScheme.error)),
    );
  }
}
