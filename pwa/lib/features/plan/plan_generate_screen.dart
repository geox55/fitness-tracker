// Экран «Сгенерировать план» — spec 006 §8 Screen: Генерация плана.
//
// Состояния:
//   - `_FormState`     — резюме входов из профиля + кнопка «Сгенерировать»;
//   - `_LoadingState`  — спиннер (REQ-01 «до 10 секунд»);
//   - `_SuccessState`  — короткая сводка + переход на /plan;
//   - `_FailureState`  — ошибка с возможностью retry; для preconditions —
//                        CTA «Перейти в профиль».

import 'package:flutter/material.dart';
import '../../app/branding/portal_app_bar.dart';
import '../../app/branding/portal_scaffold.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/l10n/generated/app_localizations.dart';
import '../../app/theme/app_colors.dart';
import '../../app/theme/app_spacing.dart';
import '../../data/api/failure.dart';
import '../../data/api/plans_api.dart';
import '../../data/api/profile_api.dart';

sealed class _GenState {
  const _GenState();
}

class _FormState extends _GenState {
  const _FormState();
}

class _LoadingState extends _GenState {
  const _LoadingState();
}

class _SuccessState extends _GenState {
  const _SuccessState({required this.plan});
  final PlanDto plan;
}

class _FailureState extends _GenState {
  const _FailureState({required this.failure});
  final AppFailure failure;
}

class PlanGenerateScreen extends ConsumerStatefulWidget {
  const PlanGenerateScreen({super.key});

  @override
  ConsumerState<PlanGenerateScreen> createState() =>
      _PlanGenerateScreenState();
}

class _PlanGenerateScreenState extends ConsumerState<PlanGenerateScreen> {
  _GenState _state = const _FormState();

  Future<void> _generate() async {
    setState(() => _state = const _LoadingState());
    try {
      // Без override — берём всё из профиля. Override-режим (изменить
      // частоту/оборудование для what-if) добавим позже отдельным UI.
      final plan = await ref.read(plansApiProvider).generate();
      if (!mounted) return;
      // Инвалидируем activePlanProvider, чтобы /plan показал свежий.
      ref.invalidate(activePlanProvider);
      setState(() => _state = _SuccessState(plan: plan));
    } on AppFailure catch (f) {
      if (!mounted) return;
      setState(() => _state = _FailureState(failure: f));
    }
  }

  @override
  Widget build(BuildContext context) {
    return PortalScaffold(
      appBar: PortalAppBar(
        title: const Text('Сгенерировать план'),
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => context.pop(),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(AppSpacing.lg),
          child: switch (_state) {
            _FormState() => _FormView(onStart: _generate),
            _LoadingState() => const _LoadingView(),
            _SuccessState(:final plan) => _SuccessView(plan: plan),
            _FailureState(:final failure) => _FailureView(
                failure: failure,
                onRetry: _generate,
              ),
          },
        ),
      ),
    );
  }
}

// --- Form: резюме параметров профиля --------------------------------------

class _FormView extends ConsumerWidget {
  const _FormView({required this.onStart});
  final VoidCallback onStart;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final profileAsync = ref.watch(profileProvider);
    return profileAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, _) => Center(
        child: Text(
          e is AppFailure ? e.message : 'Не удалось загрузить профиль',
          textAlign: TextAlign.center,
        ),
      ),
      data: (profile) {
        return ListView(
          children: [
            Text(
              'Что мы учтём',
              style: theme.textTheme.titleMedium,
            ),
            const SizedBox(height: AppSpacing.sm),
            Text(
              'Эти параметры берутся из профиля. Если что-то неверно — '
              'отредактируйте профиль перед генерацией.',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: AppSpacing.lg),
            _SummaryCard(profile: profile),
            const SizedBox(height: AppSpacing.xl),
            ElevatedButton.icon(
              icon: const Icon(Icons.auto_awesome),
              label: const Text('Сгенерировать план'),
              onPressed: _hasRequiredFields(profile) ? onStart : null,
            ),
            if (!_hasRequiredFields(profile)) ...[
              const SizedBox(height: AppSpacing.md),
              _ProfileIncompleteBanner(profile: profile),
            ],
            const SizedBox(height: AppSpacing.md),
            Text(
              'Генерация занимает несколько секунд. Прогрессия нагрузки '
              'выстраивается на 4 недели сразу.',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        );
      },
    );
  }
}

bool _hasRequiredFields(ProfileDto p) =>
    p.goal != null && p.trainingLevel != null && p.trainingFrequency != null;

class _SummaryCard extends StatelessWidget {
  const _SummaryCard({required this.profile});
  final ProfileDto profile;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHigh,
        borderRadius: BorderRadius.circular(AppRadius.lg),
        border: Border.all(color: theme.colorScheme.outline),
      ),
      child: Column(
        children: [
          _SummaryRow(
            label: 'Цель',
            value: _goalLabels[profile.goal] ?? '—',
            missing: profile.goal == null,
          ),
          _Divider(),
          _SummaryRow(
            label: 'Уровень',
            value: _levelLabels[profile.trainingLevel] ?? '—',
            missing: profile.trainingLevel == null,
          ),
          _Divider(),
          _SummaryRow(
            label: 'Тренировок в неделю',
            value: profile.trainingFrequency?.toString() ?? '—',
            missing: profile.trainingFrequency == null,
          ),
          _Divider(),
          _SummaryRow(
            label: 'Стартовый вес',
            value: profile.baselineWeightKg == null
                ? '—'
                : '${profile.baselineWeightKg!.toStringAsFixed(1)} кг',
            missing: false,
          ),
        ],
      ),
    );
  }
}

class _SummaryRow extends StatelessWidget {
  const _SummaryRow({
    required this.label,
    required this.value,
    required this.missing,
  });
  final String label;
  final String value;
  final bool missing;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.lg,
        vertical: AppSpacing.md,
      ),
      child: Row(
        children: [
          Expanded(
            child: Text(
              label,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ),
          Text(
            value,
            style: theme.textTheme.bodyLarge?.copyWith(
              color: missing ? theme.colorScheme.error : null,
            ),
          ),
        ],
      ),
    );
  }
}

class _Divider extends StatelessWidget {
  @override
  Widget build(BuildContext context) => Divider(
        height: 1,
        color: Theme.of(context).colorScheme.outline.withValues(alpha: 0.4),
      );
}

class _ProfileIncompleteBanner extends StatelessWidget {
  const _ProfileIncompleteBanner({required this.profile});
  final ProfileDto profile;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: AppPalette.warning.withValues(alpha: 0.14),
        borderRadius: BorderRadius.circular(AppRadius.md),
        border: Border.all(
          color: AppPalette.warning.withValues(alpha: 0.5),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.warning_amber, color: AppPalette.warning, size: 18),
              const SizedBox(width: AppSpacing.sm),
              Expanded(
                child: Text(
                  'Заполните недостающие поля профиля',
                  style: theme.textTheme.bodyMedium,
                ),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.sm),
          OutlinedButton(
            onPressed: () => GoRouter.of(context).go('/profile'),
            child: const Text('Открыть профиль'),
          ),
        ],
      ),
    );
  }
}

// --- Loading / Success / Failure ------------------------------------------

class _LoadingView extends StatelessWidget {
  const _LoadingView();

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const CircularProgressIndicator(),
          const SizedBox(height: AppSpacing.lg),
          Text(
            'Подбираем упражнения и собираем недели…',
            style: theme.textTheme.bodyMedium,
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}

class _SuccessView extends StatelessWidget {
  const _SuccessView({required this.plan});
  final PlanDto plan;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l = AppLocalizations.of(context);
    final totalExercises = plan.weeks.fold<int>(
      0,
      (acc, w) => acc + w.days.fold<int>(0, (a, d) => a + d.exercises.length),
    );
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.check_circle_outline,
            size: 64,
            color: AppPalette.success,
          ),
          const SizedBox(height: AppSpacing.md),
          Text('План готов', style: theme.textTheme.titleLarge),
          const SizedBox(height: AppSpacing.sm),
          Text(
            '${l.planWeekCount(plan.weeks.length)}, ${l.planExerciseCount(totalExercises)}',
            style: theme.textTheme.bodyMedium,
          ),
          if (plan.warnings.isNotEmpty) ...[
            const SizedBox(height: AppSpacing.lg),
            for (final w in plan.warnings)
              Padding(
                padding: const EdgeInsets.only(bottom: AppSpacing.xs),
                child: Text(
                  '⚠ $w',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: AppPalette.warning,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
          ],
          const SizedBox(height: AppSpacing.xl),
          ElevatedButton(
            onPressed: () {
              final router = GoRouter.of(context);
              if (router.canPop()) {
                router.pop();
              } else {
                router.go('/plan');
              }
            },
            child: const Text('Открыть план'),
          ),
        ],
      ),
    );
  }
}

class _FailureView extends StatelessWidget {
  const _FailureView({required this.failure, required this.onRetry});
  final AppFailure failure;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isPreconditions = failure is ApiFailure &&
        (failure as ApiFailure).code == planPreconditionsCode;
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            isPreconditions ? Icons.assignment_late : Icons.cloud_off,
            size: 56,
            color: theme.colorScheme.error,
          ),
          const SizedBox(height: AppSpacing.md),
          Text(
            failure.message,
            style: theme.textTheme.titleMedium,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: AppSpacing.lg),
          if (isPreconditions)
            ElevatedButton(
              onPressed: () => GoRouter.of(context).go('/profile'),
              child: const Text('Открыть профиль'),
            )
          else
            ElevatedButton(
              onPressed: onRetry,
              child: const Text('Повторить'),
            ),
        ],
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
