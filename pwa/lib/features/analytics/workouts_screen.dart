// Экран «Тренировки» (spec 010 §3 Scenario 4, REQ-07/08).
//
// Два графика по неделям (bucket=week — дефолт по REQ-07):
//   - Тоннаж = SUM(reps * weight_kg) по non-skipped логам;
//   - Количество тренировок = COUNT(DISTINCT workout_id) среди completed/auto_finished.
//
// Селектор диапазона (1m / 3m / 6m / 1y / all) ≠ REQ-02 (тот про InBody),
// но в spec 010 §7 для всех экранов аналитики одинаковый. Бэкенд агрегирует
// SQL'ом — клиент только посылает from/to.

import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../app/theme/app_colors.dart';
import '../../app/theme/app_spacing.dart';
import '../../data/api/analytics_api.dart';
import '../../data/api/failure.dart';

enum _RangePreset {
  m1,
  m3,
  m6,
  y1,
  all;

  String get label => switch (this) {
        _RangePreset.m1 => '1м',
        _RangePreset.m3 => '3м',
        _RangePreset.m6 => '6м',
        _RangePreset.y1 => '1г',
        _RangePreset.all => 'Всё',
      };

  /// Возвращает `from`. `null` → бэкенд отдаст всю историю.
  DateTime? from(DateTime now) {
    return switch (this) {
      _RangePreset.m1 => DateTime(now.year, now.month - 1, now.day),
      _RangePreset.m3 => DateTime(now.year, now.month - 3, now.day),
      _RangePreset.m6 => DateTime(now.year, now.month - 6, now.day),
      _RangePreset.y1 => DateTime(now.year - 1, now.month, now.day),
      _RangePreset.all => null,
    };
  }
}

class WorkoutsAnalyticsScreen extends ConsumerStatefulWidget {
  const WorkoutsAnalyticsScreen({super.key});

  @override
  ConsumerState<WorkoutsAnalyticsScreen> createState() =>
      _WorkoutsAnalyticsScreenState();
}

class _WorkoutsAnalyticsScreenState
    extends ConsumerState<WorkoutsAnalyticsScreen> {
  _RangePreset _range = _RangePreset.m3;

  @override
  Widget build(BuildContext context) {
    final now = DateTime.now();
    final args = WorkoutsAnalyticsArgs(
      bucket: 'week',
      from: _range.from(now),
      to: _range == _RangePreset.all ? null : now,
    );
    final async = ref.watch(workoutsAnalyticsFamily(args));
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(title: const Text('Тренировки')),
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: () async {
            ref.invalidate(workoutsAnalyticsFamily(args));
            await ref.read(workoutsAnalyticsFamily(args).future);
          },
          child: ListView(
            padding: const EdgeInsets.fromLTRB(
              AppSpacing.lg,
              AppSpacing.lg,
              AppSpacing.lg,
              AppSpacing.xxxl,
            ),
            children: [
              Wrap(
                spacing: AppSpacing.sm,
                runSpacing: AppSpacing.sm,
                children: [
                  for (final r in _RangePreset.values)
                    ChoiceChip(
                      label: Text(r.label),
                      selected: _range == r,
                      onSelected: (_) => setState(() => _range = r),
                    ),
                ],
              ),
              const SizedBox(height: AppSpacing.xl),
              async.when(
                loading: () => const _LoadingCard(height: 280),
                error: (e, _) => _ErrorCard(
                  error: e,
                  onRetry: () =>
                      ref.invalidate(workoutsAnalyticsFamily(args)),
                ),
                data: (data) => _ChartsBlock(data: data),
              ),
              const SizedBox(height: AppSpacing.xl),
              // CTA на детальный экран по упражнению (REQ-09) — единственная
              // точка входа сейчас, поэтому ставим её сюда же.
              Material(
                color: theme.colorScheme.surfaceContainerHigh,
                borderRadius: BorderRadius.circular(AppRadius.lg),
                child: InkWell(
                  borderRadius: BorderRadius.circular(AppRadius.lg),
                  onTap: () =>
                      GoRouter.of(context).push('/analytics/exercise'),
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
                            color: theme.colorScheme.primary
                                .withValues(alpha: 0.16),
                            borderRadius: BorderRadius.circular(AppRadius.md),
                          ),
                          child: Icon(
                            Icons.trending_up,
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
                                'Прогресс по упражнению',
                                style: theme.textTheme.titleMedium,
                              ),
                              Text(
                                'Лучший вес и 1RM по неделям',
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
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ChartsBlock extends StatelessWidget {
  const _ChartsBlock({required this.data});
  final WorkoutsAnalyticsResponseDto data;

  @override
  Widget build(BuildContext context) {
    if (data.items.isEmpty) {
      return const _EmptyState();
    }
    return Column(
      children: [
        _ChartCard(
          title: 'Тоннаж по неделям',
          unit: 'кг',
          color: AppPalette.primary,
          values: data.items
              .map((b) => _BarValue(date: b.periodStart, value: b.tonnageKg))
              .toList(),
        ),
        const SizedBox(height: AppSpacing.lg),
        _ChartCard(
          title: 'Количество тренировок по неделям',
          unit: '',
          color: AppPalette.success,
          values: data.items
              .map(
                (b) => _BarValue(
                  date: b.periodStart,
                  value: b.workoutsCount.toDouble(),
                ),
              )
              .toList(),
          isInteger: true,
        ),
      ],
    );
  }
}

class _BarValue {
  const _BarValue({required this.date, required this.value});
  final DateTime date;
  final double value;
}

class _ChartCard extends StatelessWidget {
  const _ChartCard({
    required this.title,
    required this.unit,
    required this.color,
    required this.values,
    this.isInteger = false,
  });
  final String title;
  final String unit;
  final Color color;
  final List<_BarValue> values;
  final bool isInteger;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final total = values.fold<double>(0, (acc, v) => acc + v.value);
    final totalStr = isInteger
        ? total.toStringAsFixed(0)
        : NumberFormat('#,###', 'ru').format(total.round());
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
              Container(
                width: 10,
                height: 10,
                decoration: BoxDecoration(
                  color: color,
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: AppSpacing.sm),
              Expanded(
                child: Text(title, style: theme.textTheme.titleMedium),
              ),
              Text(
                unit.isEmpty ? totalStr : '$totalStr $unit',
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.md),
          SizedBox(
            height: 200,
            child: _BarsChart(
              values: values,
              color: color,
              unit: unit,
              isInteger: isInteger,
            ),
          ),
        ],
      ),
    );
  }
}

class _BarsChart extends StatelessWidget {
  const _BarsChart({
    required this.values,
    required this.color,
    required this.unit,
    required this.isInteger,
  });
  final List<_BarValue> values;
  final Color color;
  final String unit;
  final bool isInteger;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final maxValue =
        values.map((v) => v.value).fold<double>(0, (a, b) => a > b ? a : b);
    final maxY = maxValue == 0 ? 1.0 : maxValue * 1.18;
    // Подписи редкие: каждый N-й, чтобы не накладывались.
    final stride = (values.length / 6).ceil().clamp(1, 9999);
    return BarChart(
      BarChartData(
        alignment: BarChartAlignment.spaceAround,
        maxY: maxY,
        barGroups: [
          for (var i = 0; i < values.length; i++)
            BarChartGroupData(
              x: i,
              barRods: [
                BarChartRodData(
                  toY: values[i].value,
                  color: color,
                  width: 14,
                  borderRadius: const BorderRadius.vertical(
                    top: Radius.circular(4),
                  ),
                ),
              ],
            ),
        ],
        gridData: FlGridData(
          show: true,
          drawVerticalLine: false,
          getDrawingHorizontalLine: (_) => FlLine(
            color: theme.colorScheme.outline.withValues(alpha: 0.18),
            strokeWidth: 1,
          ),
        ),
        titlesData: FlTitlesData(
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 36,
              getTitlesWidget: (v, _) => Padding(
                padding: const EdgeInsets.only(right: 4),
                child: Text(
                  isInteger
                      ? v.toStringAsFixed(0)
                      : _shortNumber(v),
                  style: theme.textTheme.labelSmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
              ),
            ),
          ),
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 24,
              getTitlesWidget: (x, _) {
                final i = x.toInt();
                if (i < 0 || i >= values.length) return const SizedBox.shrink();
                if (i % stride != 0) return const SizedBox.shrink();
                return Padding(
                  padding: const EdgeInsets.only(top: 4),
                  child: Text(
                    DateFormat('d MMM', 'ru').format(values[i].date),
                    style: theme.textTheme.labelSmall?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                );
              },
            ),
          ),
          topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          rightTitles:
              const AxisTitles(sideTitles: SideTitles(showTitles: false)),
        ),
        borderData: FlBorderData(show: false),
        barTouchData: BarTouchData(
          touchTooltipData: BarTouchTooltipData(
            getTooltipColor: (_) => theme.colorScheme.surface,
            getTooltipItem: (group, _, rod, __) {
              final v = values[group.x];
              final val = isInteger
                  ? rod.toY.toStringAsFixed(0)
                  : NumberFormat('#,###', 'ru').format(rod.toY.round());
              return BarTooltipItem(
                '$val${unit.isEmpty ? '' : ' $unit'}\n'
                '${DateFormat('d MMM yyyy', 'ru').format(v.date)}',
                theme.textTheme.bodySmall ?? const TextStyle(),
              );
            },
          ),
        ),
      ),
    );
  }
}

class _EmptyState extends StatelessWidget {
  const _EmptyState();

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
            'Нет завершённых тренировок в выбранном диапазоне',
            style: theme.textTheme.titleMedium,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: AppSpacing.xs),
          Text(
            'Попробуйте расширить диапазон или добавить тренировку.',
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
    final message =
        error is AppFailure ? (error as AppFailure).message : 'Не удалось загрузить';
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

/// 1234 → «1.2k», 1234567 → «1.2M». Для оси Y тоннажа — миллионы кг могут
/// набраться у активных пользователей за год.
String _shortNumber(double v) {
  if (v.abs() >= 1e6) return '${(v / 1e6).toStringAsFixed(1)}M';
  if (v.abs() >= 1e3) return '${(v / 1e3).toStringAsFixed(1)}k';
  return v.toStringAsFixed(0);
}
