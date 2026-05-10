import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/theme/app_colors.dart';
import '../../app/theme/app_spacing.dart';
import '../../data/api/analytics_api.dart';
import '../../data/api/failure.dart';
import '../../data/api/workouts_api.dart';
import 'goal_progress_card.dart';

/// Экран статистики: метрики месяца, кривая прогресса по упражнению и
/// полная история тренировок (тренировки из /workouts/history).
class StatsScreen extends ConsumerWidget {
  const StatsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final overview = ref.watch(overviewProvider);
    final history = ref.watch(workoutHistoryProvider);
    return Scaffold(
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: () async {
            ref.invalidate(overviewProvider);
            ref.invalidate(workoutHistoryProvider);
            ref.invalidate(goalProgressProvider);
            await Future.wait([
              ref.read(overviewProvider.future),
              ref.read(workoutHistoryProvider.future),
              ref.read(goalProgressProvider.future),
            ]);
          },
          child: ListView(
            padding: const EdgeInsets.fromLTRB(
              AppSpacing.lg,
              AppSpacing.lg,
              AppSpacing.lg,
              AppSpacing.xxxl * 2,
            ),
            children: [
              const _Header(),
              const SizedBox(height: AppSpacing.xl),
              const _ImportInbodyCard(),
              const SizedBox(height: AppSpacing.xl),
              overview.when(
                loading: () => const _LoadingCard(height: 220),
                error: (e, _) => _ErrorCard(
                  error: e,
                  onRetry: () => ref.invalidate(overviewProvider),
                ),
                data: (data) => _OverviewSection(data: data),
              ),
              const SizedBox(height: AppSpacing.xl),
              const _SectionLabel(text: 'Прогресс по цели'),
              const SizedBox(height: AppSpacing.md),
              const GoalProgressCard(),
              const SizedBox(height: AppSpacing.md),
              const _BodyAnalyticsLinkCard(),
              const SizedBox(height: AppSpacing.xl),
              const _SectionLabel(text: 'История'),
              const SizedBox(height: AppSpacing.md),
              history.when(
                loading: () => const _LoadingCard(height: 320),
                error: (e, _) => _ErrorCard(
                  error: e,
                  onRetry: () => ref.invalidate(workoutHistoryProvider),
                ),
                data: (items) => _HistoryList(items: items),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// --- Header ----------------------------------------------------------------

class _Header extends StatelessWidget {
  const _Header();

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Row(
      children: [
        Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            color: theme.colorScheme.primary.withValues(alpha: 0.18),
            borderRadius: BorderRadius.circular(AppRadius.md),
          ),
          child: Icon(
            Icons.bar_chart,
            color: theme.colorScheme.primary,
            size: 24,
          ),
        ),
        const SizedBox(width: AppSpacing.md),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Статистика', style: theme.textTheme.headlineMedium),
              Text(
                'Прогресс и история',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _SectionLabel extends StatelessWidget {
  const _SectionLabel({required this.text});
  final String text;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Text(
      text.toUpperCase(),
      style: theme.textTheme.labelSmall?.copyWith(
        color: theme.colorScheme.primary,
        letterSpacing: 1.6,
      ),
    );
  }
}

// --- Import InBody PDF card -----------------------------------------------

class _ImportInbodyCard extends StatelessWidget {
  const _ImportInbodyCard();

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Material(
      color: theme.colorScheme.surfaceContainerHigh,
      borderRadius: BorderRadius.circular(AppRadius.lg),
      child: InkWell(
        borderRadius: BorderRadius.circular(AppRadius.lg),
        onTap: () => context.push('/inbody/upload-pdf'),
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
                  Icons.picture_as_pdf_outlined,
                  color: theme.colorScheme.primary,
                  size: 24,
                ),
              ),
              const SizedBox(width: AppSpacing.md),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Загрузить InBody PDF',
                      style: theme.textTheme.titleMedium,
                    ),
                    Text(
                      'Распознаем вес, % жира, мышцы и другие поля',
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

// --- Body analytics link card ---------------------------------------------

/// CTA-карточка → /analytics/body. Полные графики тела (вес/жир/мышцы)
/// с overlay-прогнозом живут на отдельном экране, чтобы не превращать
/// StatsScreen в бесконечный скролл.
class _BodyAnalyticsLinkCard extends StatelessWidget {
  const _BodyAnalyticsLinkCard();

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Material(
      color: theme.colorScheme.surfaceContainerHigh,
      borderRadius: BorderRadius.circular(AppRadius.lg),
      child: InkWell(
        borderRadius: BorderRadius.circular(AppRadius.lg),
        onTap: () => context.push('/analytics/body'),
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
                  Icons.show_chart,
                  color: theme.colorScheme.primary,
                  size: 24,
                ),
              ),
              const SizedBox(width: AppSpacing.md),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Графики тела', style: theme.textTheme.titleMedium),
                    Text(
                      'Вес, % жира, мышцы — с прогнозом и CI',
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

// --- Overview section ------------------------------------------------------

class _OverviewSection extends StatelessWidget {
  const _OverviewSection({required this.data});
  final OverviewResponseDto data;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        _MetricsRow(metrics: data.metrics),
        if (data.strength != null) ...[
          const SizedBox(height: AppSpacing.md),
          _StrengthCard(strength: data.strength!),
        ],
      ],
    );
  }
}

class _MetricsRow extends StatelessWidget {
  const _MetricsRow({required this.metrics});
  final OverviewMetricsDto metrics;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: _MetricCell(
            label: 'Тренировок',
            value: '${metrics.workoutsThisMonth}',
            sublabel: 'за месяц',
          ),
        ),
        const SizedBox(width: AppSpacing.md),
        Expanded(
          child: _MetricCell(
            label: 'Тоннаж',
            value: _thousands(metrics.totalWeightKg),
            sublabel: 'кг',
            delta: metrics.totalWeightDeltaPercent,
          ),
        ),
        const SizedBox(width: AppSpacing.md),
        Expanded(
          child: _MetricCell(
            label: 'Серия',
            value: '${metrics.activeStreakDays}',
            sublabel: 'дн.',
            highlight: metrics.streakIsPersonalBest,
          ),
        ),
      ],
    );
  }
}

class _MetricCell extends StatelessWidget {
  const _MetricCell({
    required this.label,
    required this.value,
    required this.sublabel,
    this.delta,
    this.highlight = false,
  });

  final String label;
  final String value;
  final String sublabel;
  final int? delta;
  final bool highlight;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHigh,
        borderRadius: BorderRadius.circular(AppRadius.lg),
        border: Border.all(
          color: highlight
              ? theme.colorScheme.primary.withValues(alpha: 0.6)
              : theme.colorScheme.outline,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label.toUpperCase(),
            style: theme.textTheme.labelSmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: AppSpacing.sm),
          Text(value, style: theme.textTheme.headlineMedium),
          Text(
            sublabel,
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
          if (delta != null && delta != 0) ...[
            const SizedBox(height: AppSpacing.xs),
            Row(
              children: [
                Icon(
                  delta! > 0 ? Icons.trending_up : Icons.trending_down,
                  color: delta! > 0 ? AppPalette.success : AppPalette.warning,
                  size: 14,
                ),
                const SizedBox(width: 2),
                Flexible(
                  child: Text(
                    '${delta! > 0 ? '+' : ''}$delta%',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: delta! > 0 ? AppPalette.success : AppPalette.warning,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }
}

class _StrengthCard extends StatelessWidget {
  const _StrengthCard({required this.strength});
  final StrengthProgressDto strength;

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
              _Chip(text: strength.exerciseTitle ?? 'Упражнение'),
              const Spacer(),
              Text(
                'Последние 30 дней',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.md),
          Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                '${strength.currentMaxKg}',
                style: theme.textTheme.displayMedium?.copyWith(height: 1),
              ),
              const SizedBox(width: 6),
              Padding(
                padding: const EdgeInsets.only(bottom: 6),
                child: Text(
                  'кг макс.',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.primary,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.lg),
          SizedBox(
            height: 140,
            child: _StrengthLine(points: strength.points),
          ),
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
        text.toUpperCase(),
        style: theme.textTheme.labelSmall?.copyWith(
          color: theme.colorScheme.primary,
          letterSpacing: 1.2,
        ),
      ),
    );
  }
}

class _StrengthLine extends StatelessWidget {
  const _StrengthLine({required this.points});
  final List<StrengthPointDto> points;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    if (points.isEmpty) {
      return Center(
        child: Text(
          'Нет данных',
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
      );
    }
    final spots = points
        .map((p) => FlSpot(p.dayOffset.toDouble(), p.weightKg))
        .toList();
    return LineChart(
      LineChartData(
        gridData: const FlGridData(show: false),
        titlesData: const FlTitlesData(show: false),
        borderData: FlBorderData(show: false),
        lineBarsData: [
          LineChartBarData(
            spots: spots,
            isCurved: true,
            curveSmoothness: 0.32,
            color: theme.colorScheme.primary,
            barWidth: 3,
            isStrokeCapRound: true,
            dotData: FlDotData(
              show: true,
              checkToShowDot: (spot, _) => spot.x == spots.last.x,
              getDotPainter: (spot, _, __, ___) => FlDotCirclePainter(
                radius: 4,
                color: Colors.white,
                strokeColor: theme.colorScheme.primary,
                strokeWidth: 2,
              ),
            ),
            belowBarData: BarAreaData(
              show: true,
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  theme.colorScheme.primary.withValues(alpha: 0.30),
                  theme.colorScheme.primary.withValues(alpha: 0.0),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// --- History ---------------------------------------------------------------

class _HistoryList extends StatelessWidget {
  const _HistoryList({required this.items});
  final List<WorkoutSummaryDto> items;

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty) {
      return _Empty();
    }
    return Column(
      children: [
        for (var i = 0; i < items.length; i++) ...[
          _WorkoutCard(item: items[i]),
          if (i != items.length - 1) const SizedBox(height: AppSpacing.sm),
        ],
      ],
    );
  }
}

class _WorkoutCard extends StatelessWidget {
  const _WorkoutCard({required this.item});
  final WorkoutSummaryDto item;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final tonnage = item.totalTonnage.round();
    final isCompleted = item.status == 'completed' ||
        item.status == 'auto_finished';
    return Container(
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHigh,
        borderRadius: BorderRadius.circular(AppRadius.lg),
        border: Border.all(color: theme.colorScheme.outline),
      ),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: (isCompleted
                      ? theme.colorScheme.primary
                      : theme.colorScheme.onSurfaceVariant)
                  .withValues(alpha: 0.16),
              borderRadius: BorderRadius.circular(AppRadius.sm),
            ),
            child: Icon(
              isCompleted
                  ? Icons.check_circle_outline
                  : Icons.history_toggle_off,
              color: isCompleted
                  ? theme.colorScheme.primary
                  : theme.colorScheme.onSurfaceVariant,
              size: 20,
            ),
          ),
          const SizedBox(width: AppSpacing.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  _formatDate(item.performedAt),
                  style: theme.textTheme.titleMedium,
                ),
                Text(
                  '${item.setsCount} подходов · $tonnage кг',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
              ],
            ),
          ),
          if (item.status == 'cancelled')
            Container(
              padding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.sm,
                vertical: 2,
              ),
              decoration: BoxDecoration(
                color: theme.colorScheme.error.withValues(alpha: 0.14),
                borderRadius: BorderRadius.circular(AppRadius.sm),
              ),
              child: Text(
                'отменена',
                style: theme.textTheme.labelSmall?.copyWith(
                  color: theme.colorScheme.error,
                ),
              ),
            ),
          if (item.status == 'in_progress')
            Container(
              padding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.sm,
                vertical: 2,
              ),
              decoration: BoxDecoration(
                color: theme.colorScheme.primary.withValues(alpha: 0.16),
                borderRadius: BorderRadius.circular(AppRadius.sm),
              ),
              child: Text(
                'идёт',
                style: theme.textTheme.labelSmall?.copyWith(
                  color: theme.colorScheme.primary,
                ),
              ),
            ),
        ],
      ),
    );
  }
}

class _Empty extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.all(AppSpacing.xxl),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHigh,
        borderRadius: BorderRadius.circular(AppRadius.lg),
        border: Border.all(color: theme.colorScheme.outline),
      ),
      child: Column(
        children: [
          Icon(
            Icons.fitness_center_outlined,
            size: 40,
            color: theme.colorScheme.onSurfaceVariant,
          ),
          const SizedBox(height: AppSpacing.md),
          Text(
            'Нет завершённых тренировок',
            style: theme.textTheme.titleMedium,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: AppSpacing.xs),
          Text(
            'История появится после первой тренировки',
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}

// --- Generic --------------------------------------------------------------

class _LoadingCard extends StatelessWidget {
  const _LoadingCard({required this.height});
  final double height;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: height,
      child: const Center(child: CircularProgressIndicator()),
    );
  }
}

class _ErrorCard extends StatelessWidget {
  const _ErrorCard({required this.error, required this.onRetry});
  final Object error;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final message = error is AppFailure
        ? (error as AppFailure).message
        : 'Не удалось загрузить';
    return Container(
      padding: const EdgeInsets.all(AppSpacing.lg),
      decoration: BoxDecoration(
        color: theme.colorScheme.error.withValues(alpha: 0.10),
        borderRadius: BorderRadius.circular(AppRadius.lg),
        border: Border.all(
          color: theme.colorScheme.error.withValues(alpha: 0.4),
        ),
      ),
      child: Column(
        children: [
          Icon(Icons.cloud_off, color: theme.colorScheme.error, size: 32),
          const SizedBox(height: AppSpacing.sm),
          Text(message, textAlign: TextAlign.center),
          const SizedBox(height: AppSpacing.md),
          OutlinedButton(onPressed: onRetry, child: const Text('Повторить')),
        ],
      ),
    );
  }
}

// --- Helpers --------------------------------------------------------------

String _thousands(int value) {
  final s = value.toString();
  final buf = StringBuffer();
  for (var i = 0; i < s.length; i++) {
    final reverseIndex = s.length - i;
    if (i != 0 && reverseIndex % 3 == 0) buf.write(',');
    buf.write(s[i]);
  }
  return buf.toString();
}

String _formatDate(DateTime d) {
  const months = [
    'янв', 'фев', 'мар', 'апр', 'мая', 'июн',
    'июл', 'авг', 'сен', 'окт', 'ноя', 'дек',
  ];
  return '${d.day} ${months[d.month - 1]} ${d.year}';
}
