// Экран «День плана» — spec 006 §8 Screen: День плана.
//
// Принимает `dayId`, ищет день внутри активного плана (provider уже
// загружен на overview-экране, и тут нам не нужно отдельный endpoint).
// Список упражнений со sets×reps/RPE/отдыхом. CTA «Начать тренировку» —
// стаб: REQ-12 spec 005 (plan_day_id в Workout) ещё не реализован,
// поэтому переходим на freestyle-старт.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/theme/app_spacing.dart';
import '../../data/api/failure.dart';
import '../../data/api/plans_api.dart';

class PlanDayScreen extends ConsumerWidget {
  const PlanDayScreen({super.key, required this.dayId});
  final String dayId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(activePlanProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('День плана')),
      body: SafeArea(
        child: async.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (e, _) => _ErrorView(
            error: e,
            onRetry: () => ref.invalidate(activePlanProvider),
          ),
          data: (plan) {
            if (plan == null) return const _NoPlanView();
            final day = _findDay(plan, dayId);
            if (day == null) return const _DayNotFoundView();
            return _DayBody(day: day);
          },
        ),
      ),
    );
  }
}

PlanDayDto? _findDay(PlanDto plan, String dayId) {
  for (final week in plan.weeks) {
    for (final day in week.days) {
      if (day.id == dayId) return day;
    }
  }
  return null;
}

class _DayBody extends StatelessWidget {
  const _DayBody({required this.day});
  final PlanDayDto day;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final exercises = [...day.exercises]
      ..sort((a, b) => a.orderNo.compareTo(b.orderNo));
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(
            AppSpacing.lg,
            AppSpacing.md,
            AppSpacing.lg,
            AppSpacing.sm,
          ),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'День ${day.dayNo}',
                      style: theme.textTheme.labelSmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                        letterSpacing: 1.1,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(day.name, style: theme.textTheme.headlineSmall),
                  ],
                ),
              ),
            ],
          ),
        ),
        Expanded(
          child: ListView.separated(
            padding: const EdgeInsets.all(AppSpacing.lg),
            itemCount: exercises.length,
            separatorBuilder: (_, __) =>
                const SizedBox(height: AppSpacing.sm),
            itemBuilder: (_, i) => _ExerciseCard(exercise: exercises[i]),
          ),
        ),
        SafeArea(
          minimum: const EdgeInsets.fromLTRB(
            AppSpacing.lg,
            0,
            AppSpacing.lg,
            AppSpacing.lg,
          ),
          child: SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              icon: const Icon(Icons.play_arrow),
              label: const Text('Начать тренировку'),
              onPressed: () => _onStart(context),
            ),
          ),
        ),
      ],
    );
  }

  void _onStart(BuildContext context) {
    // TODO: spec 005 REQ-12 — связь plan_day_id с активной тренировкой.
    // Пока перенаправляем в Training-таб; пользователь стартует freestyle.
    GoRouter.of(context).go('/training');
  }
}

class _ExerciseCard extends StatelessWidget {
  const _ExerciseCard({required this.exercise});
  final PlanExerciseDto exercise;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.all(AppSpacing.lg),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHigh,
        borderRadius: BorderRadius.circular(AppRadius.lg),
        border: Border.all(color: theme.colorScheme.outline),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              CircleAvatar(
                radius: 14,
                backgroundColor: theme.colorScheme.primary.withValues(alpha: 0.18),
                child: Text(
                  '${exercise.orderNo}',
                  style: theme.textTheme.labelMedium?.copyWith(
                    color: theme.colorScheme.primary,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
              const SizedBox(width: AppSpacing.md),
              Expanded(
                child: Text(
                  exercise.exerciseName,
                  style: theme.textTheme.titleMedium,
                ),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.md),
          Wrap(
            spacing: AppSpacing.sm,
            runSpacing: AppSpacing.xs,
            children: [
              _Pill(
                icon: Icons.repeat,
                text:
                    '${exercise.targetSets}×${exercise.targetRepsMin}-${exercise.targetRepsMax}',
              ),
              if (exercise.targetWeightKg != null)
                _Pill(
                  icon: Icons.fitness_center,
                  text: '${_fmtWeight(exercise.targetWeightKg!)} кг',
                ),
              if (exercise.targetRpe != null)
                _Pill(
                  icon: Icons.speed,
                  text: 'RPE ${exercise.targetRpe}',
                ),
              if (exercise.restSeconds != null)
                _Pill(
                  icon: Icons.timer_outlined,
                  text: '${exercise.restSeconds} с',
                ),
            ],
          ),
          if (exercise.notes != null && exercise.notes!.isNotEmpty) ...[
            const SizedBox(height: AppSpacing.sm),
            Text(
              exercise.notes!,
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _Pill extends StatelessWidget {
  const _Pill({required this.icon, required this.text});
  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.md,
        vertical: AppSpacing.xs,
      ),
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        borderRadius: BorderRadius.circular(AppRadius.pill),
        border: Border.all(
          color: theme.colorScheme.outline.withValues(alpha: 0.6),
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: theme.colorScheme.onSurfaceVariant),
          const SizedBox(width: 4),
          Text(
            text,
            style: theme.textTheme.labelMedium?.copyWith(
              color: theme.colorScheme.onSurface,
            ),
          ),
        ],
      ),
    );
  }
}

String _fmtWeight(double v) =>
    v.toStringAsFixed(v.truncateToDouble() == v ? 0 : 1);

class _DayNotFoundView extends StatelessWidget {
  const _DayNotFoundView();

  @override
  Widget build(BuildContext context) {
    return const _MessageView(
      icon: Icons.search_off,
      title: 'День не найден',
      subtitle: 'Похоже, план был перегенерирован. Вернитесь к обзору.',
    );
  }
}

class _NoPlanView extends StatelessWidget {
  const _NoPlanView();

  @override
  Widget build(BuildContext context) {
    return const _MessageView(
      icon: Icons.event_busy,
      title: 'Активного плана нет',
      subtitle: 'Сгенерируйте план на вкладке «Мой план».',
    );
  }
}

class _MessageView extends StatelessWidget {
  const _MessageView({
    required this.icon,
    required this.title,
    required this.subtitle,
  });
  final IconData icon;
  final String title;
  final String subtitle;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.xxl),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 56, color: theme.colorScheme.onSurfaceVariant),
            const SizedBox(height: AppSpacing.md),
            Text(
              title,
              style: theme.textTheme.titleMedium,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: AppSpacing.sm),
            Text(
              subtitle,
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.error, required this.onRetry});
  final Object error;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final message =
        error is AppFailure ? (error as AppFailure).message : 'Ошибка';
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.cloud_off, color: theme.colorScheme.error, size: 40),
          const SizedBox(height: AppSpacing.md),
          Text(message),
          const SizedBox(height: AppSpacing.md),
          OutlinedButton(onPressed: onRetry, child: const Text('Повторить')),
        ],
      ),
    );
  }
}
