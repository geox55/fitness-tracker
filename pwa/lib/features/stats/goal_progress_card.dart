// Карточка «Прогресс по цели» (spec 010 §3 Sc.3, REQ-05).
//
// Два состояния, switch'аем по типу sealed `GoalProgressDto`:
// - `GoalProgressDataDto` — progress bar + текущее/стартовое/целевое + ETA;
// - `GoalProgressEmptyDto` — CTA «Укажите цель в профиле» с deep-link.
//
// На уровне UI ничего не считаем: процент, метку goal'а и ETA берём из DTO.
// Это сохраняет один источник правды (бэкенд) и упрощает unit-тестирование.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../app/theme/app_colors.dart';
import '../../app/theme/app_spacing.dart';
import '../../data/api/analytics_api.dart';

class GoalProgressCard extends ConsumerWidget {
  const GoalProgressCard({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(goalProgressProvider);
    return async.when(
      loading: () => const _CardShell(child: _LoadingPlaceholder()),
      error: (e, _) => _CardShell(
        child: _Error(onRetry: () => ref.invalidate(goalProgressProvider)),
      ),
      data: (dto) => switch (dto) {
        GoalProgressDataDto() => _CardShell(child: _Progress(data: dto)),
        GoalProgressEmptyDto() => _CardShell(child: _Empty(empty: dto)),
      },
    );
  }
}

// ---------------------------------------------------------------------------
// Положительный сценарий: progress bar + цифры + ETA
// ---------------------------------------------------------------------------

class _Progress extends StatelessWidget {
  const _Progress({required this.data});
  final GoalProgressDataDto data;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final unit = _unitFor(data.goal);
    final goalLabel = _goalLabel(data.goal);

    final percentClamped = data.progressPercent.clamp(0, 100);
    final accent = data.alreadyReached
        ? AppPalette.success
        : theme.colorScheme.primary;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(goalLabel, style: theme.textTheme.titleMedium),
            const Spacer(),
            Text(
              '$percentClamped%',
              style: theme.textTheme.titleMedium?.copyWith(
                color: accent,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
        const SizedBox(height: AppSpacing.md),
        ClipRRect(
          borderRadius: BorderRadius.circular(AppRadius.pill),
          child: LinearProgressIndicator(
            value: percentClamped / 100,
            minHeight: 10,
            backgroundColor: theme.colorScheme.surfaceContainerHighest,
            valueColor: AlwaysStoppedAnimation<Color>(accent),
          ),
        ),
        const SizedBox(height: AppSpacing.md),
        Row(
          children: [
            _ValueColumn(
              label: 'Старт',
              value: _fmtValue(data.startValue, unit),
              subtitle: _fmtDate(data.startedAt),
            ),
            const SizedBox(width: AppSpacing.lg),
            _ValueColumn(
              label: 'Сейчас',
              value: _fmtValue(data.currentValue, unit),
              valueColor: accent,
            ),
            const SizedBox(width: AppSpacing.lg),
            _ValueColumn(
              label: 'Цель',
              value: _fmtValue(data.targetValue, unit),
            ),
          ],
        ),
        if (data.eta != null || data.alreadyReached) ...[
          const SizedBox(height: AppSpacing.md),
          _EtaBlock(data: data),
        ],
      ],
    );
  }
}

class _ValueColumn extends StatelessWidget {
  const _ValueColumn({
    required this.label,
    required this.value,
    this.subtitle,
    this.valueColor,
  });

  final String label;
  final String value;
  final String? subtitle;
  final Color? valueColor;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Expanded(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: theme.textTheme.labelSmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            value,
            style: theme.textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.w600,
              color: valueColor,
            ),
          ),
          if (subtitle != null) ...[
            const SizedBox(height: 2),
            Text(
              subtitle!,
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

class _EtaBlock extends StatelessWidget {
  const _EtaBlock({required this.data});
  final GoalProgressDataDto data;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    if (data.alreadyReached) {
      return Row(
        children: [
          const Icon(Icons.check_circle, color: AppPalette.success, size: 18),
          const SizedBox(width: AppSpacing.sm),
          Text(
            'Цель достигнута — пора поставить новую',
            style: theme.textTheme.bodyMedium?.copyWith(
              color: AppPalette.success,
            ),
          ),
        ],
      );
    }
    final eta = data.eta;
    if (eta == null) return const SizedBox.shrink();
    final confidence = data.etaConfidence;
    return Row(
      children: [
        Icon(
          Icons.flag_outlined,
          color: theme.colorScheme.onSurfaceVariant,
          size: 18,
        ),
        const SizedBox(width: AppSpacing.sm),
        Expanded(
          child: Text.rich(
            TextSpan(
              children: [
                TextSpan(
                  text: 'Цель достижима к ${_fmtDate(eta)}',
                  style: theme.textTheme.bodyMedium,
                ),
                if (confidence != null)
                  TextSpan(
                    text: ' · ${_confidenceLabel(confidence)}',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

// ---------------------------------------------------------------------------
// Empty state: CTA в профиль
// ---------------------------------------------------------------------------

class _Empty extends StatelessWidget {
  const _Empty({required this.empty});
  final GoalProgressEmptyDto empty;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final (icon, title, hint) = _emptyContent(empty);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, color: theme.colorScheme.primary),
            const SizedBox(width: AppSpacing.sm),
            Expanded(
              child: Text(title, style: theme.textTheme.titleMedium),
            ),
          ],
        ),
        const SizedBox(height: AppSpacing.sm),
        Text(
          hint,
          style: theme.textTheme.bodyMedium?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        const SizedBox(height: AppSpacing.md),
        // На no_inbody_measurements уводим на /home: оттуда есть быстрый CTA
        // импорта PDF/ручного ввода. Иначе — в профиль для заполнения цели.
        Align(
          alignment: Alignment.centerLeft,
          child: FilledButton.tonal(
            onPressed: () {
              final route = empty.reason == 'no_inbody_measurements'
                  ? '/home'
                  : '/profile';
              GoRouter.of(context).go(route);
            },
            child: Text(
              empty.reason == 'no_inbody_measurements'
                  ? 'Добавить замер'
                  : 'Открыть профиль',
            ),
          ),
        ),
      ],
    );
  }
}

// ---------------------------------------------------------------------------
// Shell + helpers
// ---------------------------------------------------------------------------

class _CardShell extends StatelessWidget {
  const _CardShell({required this.child});
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.zero,
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: child,
      ),
    );
  }
}

class _LoadingPlaceholder extends StatelessWidget {
  const _LoadingPlaceholder();

  @override
  Widget build(BuildContext context) {
    return const SizedBox(
      height: 96,
      child: Center(
        child: CircularProgressIndicator(strokeWidth: 2.5),
      ),
    );
  }
}

class _Error extends StatelessWidget {
  const _Error({required this.onRetry});
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Row(
      children: [
        Icon(Icons.error_outline, color: theme.colorScheme.error),
        const SizedBox(width: AppSpacing.sm),
        Expanded(
          child: Text(
            'Не удалось загрузить прогресс',
            style: theme.textTheme.bodyMedium,
          ),
        ),
        TextButton(onPressed: onRetry, child: const Text('Повторить')),
      ],
    );
  }
}

String _goalLabel(String goal) =>
    switch (goal) {
      'weight_loss' => 'Снижение веса',
      'muscle_gain' => 'Набор мышц',
      _ => 'Прогресс по цели',
    };

String _unitFor(String goal) =>
    goal == 'weight_loss' ? 'кг' : 'кг';

String _fmtValue(double v, String unit) =>
    '${v.toStringAsFixed(v.truncateToDouble() == v ? 0 : 1)} $unit';

String _fmtDate(DateTime d) => DateFormat('d MMM yyyy', 'ru').format(d);

String _confidenceLabel(String c) =>
    switch (c) {
      'high' => 'высокая уверенность',
      'medium' => 'средняя уверенность',
      'low' => 'низкая уверенность',
      _ => '',
    };

(IconData, String, String) _emptyContent(GoalProgressEmptyDto e) {
  return switch (e.reason) {
    'no_goal_in_profile' => (
        Icons.flag_outlined,
        'Поставьте цель',
        'В профиле нет цели — выберите «снижение веса» или «набор мышц», чтобы видеть прогресс и ETA.',
      ),
    'no_target_set' => (
        Icons.adjust,
        'Укажите целевое значение',
        e.missingFields.contains('target_muscle_kg')
            ? 'Сколько мышечной массы вы хотите набрать? Укажите цель в профиле.'
            : 'До какого веса вы хотите дойти? Укажите цель в профиле.',
      ),
    'no_inbody_measurements' => (
        Icons.monitor_weight_outlined,
        'Нужен InBody-замер',
        'Добавьте первый замер — после него появится прогресс и прогноз.',
      ),
    _ => (Icons.help_outline, 'Прогресс недоступен', 'Не хватает данных.'),
  };
}
