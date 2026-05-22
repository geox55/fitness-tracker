// Экран «Мой план» — spec 006 §8 Screen: Мой план (обзор).
//
// Структура:
//   - empty state с CTA на /plan/generate, если активного плана нет;
//   - шапка с goal / training_level / frequency / valid_until;
//   - 4 вкладки (по неделям) с карточками дней;
//   - в меню — «Сгенерировать заново» (REQ-12) с подтверждением.
//
// Тап по дню → /plan/day/:id (см. plan_day_screen.dart).

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../app/l10n/generated/app_localizations.dart';
import '../../app/theme/app_colors.dart';
import '../../app/theme/app_spacing.dart';
import '../../data/api/failure.dart';
import '../../data/api/plans_api.dart';

class PlanOverviewScreen extends ConsumerWidget {
  const PlanOverviewScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(activePlanProvider);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Мой план'),
        actions: async.maybeWhen(
          data: (plan) => plan == null
              ? null
              : [
                  IconButton(
                    icon: const Icon(Icons.refresh),
                    tooltip: 'Сгенерировать заново',
                    onPressed: () => _onRegenerate(context, ref),
                  ),
                ],
          orElse: () => null,
        ),
      ),
      body: SafeArea(
        child: async.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (e, _) => _ErrorView(
            error: e,
            onRetry: () => ref.invalidate(activePlanProvider),
          ),
          data: (plan) => plan == null
              ? const _EmptyState()
              : _PlanBody(plan: plan),
        ),
      ),
    );
  }

  Future<void> _onRegenerate(BuildContext context, WidgetRef ref) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Сгенерировать заново?'),
        content: const Text(
          'Текущий план будет архивирован, история тренировок сохранится.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(false),
            child: const Text('Отмена'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.of(ctx).pop(true),
            child: const Text('Сгенерировать'),
          ),
        ],
      ),
    );
    if (confirmed != true || !context.mounted) return;
    context.push('/plan/generate');
  }
}

class _EmptyState extends StatelessWidget {
  const _EmptyState();

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.xxl),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 96,
              height: 96,
              decoration: BoxDecoration(
                color: theme.colorScheme.primary.withValues(alpha: 0.16),
                borderRadius: BorderRadius.circular(AppRadius.xl),
              ),
              child: Icon(
                Icons.auto_awesome,
                size: 48,
                color: theme.colorScheme.primary,
              ),
            ),
            const SizedBox(height: AppSpacing.lg),
            Text(
              'У вас пока нет активного плана',
              style: theme.textTheme.titleLarge,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: AppSpacing.sm),
            Text(
              'Сгенерируем план на 4 недели по вашим целям, '
              'уровню и доступному оборудованию.',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: AppSpacing.xl),
            ElevatedButton.icon(
              icon: const Icon(Icons.auto_awesome),
              label: const Text('Сгенерировать план'),
              onPressed: () => GoRouter.of(context).push('/plan/generate'),
            ),
          ],
        ),
      ),
    );
  }
}

class _PlanBody extends StatelessWidget {
  const _PlanBody({required this.plan});
  final PlanDto plan;

  @override
  Widget build(BuildContext context) {
    final weeks = [...plan.weeks]..sort((a, b) => a.weekNo.compareTo(b.weekNo));
    return DefaultTabController(
      length: weeks.length,
      child: Column(
        children: [
          _PlanHeader(plan: plan),
          TabBar(
            isScrollable: true,
            tabs: [for (final w in weeks) Tab(text: 'Неделя ${w.weekNo}')],
          ),
          Expanded(
            child: TabBarView(
              children: [for (final w in weeks) _WeekView(week: w)],
            ),
          ),
        ],
      ),
    );
  }
}

class _PlanHeader extends StatelessWidget {
  const _PlanHeader({required this.plan});
  final PlanDto plan;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final goalLabel = _goalLabels[plan.goal] ?? plan.goal;
    final levelLabel = _levelLabels[plan.trainingLevel] ?? plan.trainingLevel;
    return Container(
      padding: const EdgeInsets.fromLTRB(
        AppSpacing.lg,
        AppSpacing.md,
        AppSpacing.lg,
        AppSpacing.lg,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              _Chip(text: goalLabel),
              const SizedBox(width: AppSpacing.sm),
              _Chip(text: levelLabel),
              const SizedBox(width: AppSpacing.sm),
              _Chip(text: '${plan.frequency} тр./нед'),
            ],
          ),
          const SizedBox(height: AppSpacing.sm),
          Text(
            'Активен до ${DateFormat('d MMM yyyy', 'ru').format(plan.validUntil)}',
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
          if (plan.warnings.isNotEmpty) ...[
            const SizedBox(height: AppSpacing.sm),
            for (final w in plan.warnings)
              Padding(
                padding: const EdgeInsets.only(bottom: AppSpacing.xs),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(
                      Icons.info_outline,
                      size: 16,
                      color: AppPalette.warning,
                    ),
                    const SizedBox(width: AppSpacing.xs),
                    Expanded(
                      child: Text(
                        w,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: AppPalette.warning,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
          ],
        ],
      ),
    );
  }
}

class _Chip extends StatelessWidget {
  const _Chip({required this.text});
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
        color: theme.colorScheme.primary.withValues(alpha: 0.16),
        borderRadius: BorderRadius.circular(AppRadius.pill),
      ),
      child: Text(
        text,
        style: theme.textTheme.labelMedium?.copyWith(
          color: theme.colorScheme.primary,
        ),
      ),
    );
  }
}

class _WeekView extends StatelessWidget {
  const _WeekView({required this.week});
  final PlanWeekDto week;

  @override
  Widget build(BuildContext context) {
    final days = [...week.days]..sort((a, b) => a.dayNo.compareTo(b.dayNo));
    return ListView.separated(
      padding: const EdgeInsets.all(AppSpacing.lg),
      itemCount: days.length,
      separatorBuilder: (_, __) => const SizedBox(height: AppSpacing.md),
      itemBuilder: (_, i) => _DayCard(day: days[i]),
    );
  }
}

class _DayCard extends StatelessWidget {
  const _DayCard({required this.day});
  final PlanDayDto day;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isCardio = day.type == 'cardio';
    final color = isCardio ? AppPalette.warning : theme.colorScheme.primary;
    return Material(
      color: theme.colorScheme.surfaceContainerHigh,
      borderRadius: BorderRadius.circular(AppRadius.lg),
      child: InkWell(
        borderRadius: BorderRadius.circular(AppRadius.lg),
        onTap: () => GoRouter.of(context).push('/plan/day/${day.id}'),
        child: Container(
          padding: const EdgeInsets.all(AppSpacing.lg),
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
                  color: color.withValues(alpha: 0.18),
                  borderRadius: BorderRadius.circular(AppRadius.md),
                ),
                child: Icon(
                  isCardio ? Icons.directions_run : Icons.fitness_center,
                  color: color,
                  size: 22,
                ),
              ),
              const SizedBox(width: AppSpacing.md),
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
                    Text(day.name, style: theme.textTheme.titleMedium),
                    Text(
                      _subtitle(context, day),
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

String _subtitle(BuildContext context, PlanDayDto day) {
  if (day.type == 'cardio') {
    final first = day.exercises.isNotEmpty ? day.exercises.first : null;
    return first?.notes ?? 'Кардио';
  }
  return AppLocalizations.of(context).planExerciseCount(day.exercises.length);
}

class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.error, required this.onRetry});
  final Object error;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final message =
        error is AppFailure ? (error as AppFailure).message : 'Не удалось загрузить';
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.xl),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.cloud_off, color: theme.colorScheme.error, size: 40),
            const SizedBox(height: AppSpacing.md),
            Text(message, textAlign: TextAlign.center),
            const SizedBox(height: AppSpacing.md),
            OutlinedButton(onPressed: onRetry, child: const Text('Повторить')),
          ],
        ),
      ),
    );
  }
}

const _goalLabels = <String, String>{
  'weight_loss': 'Похудение',
  'muscle_gain': 'Набор массы',
  'maintenance': 'Поддержание',
};
const _levelLabels = <String, String>{
  'beginner': 'Новичок',
  'intermediate': 'Средний',
  'advanced': 'Продвинутый',
};
