// Экран «Тело»: 3 графика InBody-серий с forecast-overlay и CI-band
// (spec 010 §3 Sc.1, REQ-01..03).
//
// Каждая метрика — отдельный inbodySeriesProvider(metric); рендерим три
// карточки с одинаковой структурой:
// - сплошная линия — история (`points`);
// - пунктирная линия — `forecast.points` (overlay), вместе с CI-band'ом
//   (заливка между ci_low и ci_high). Если forecast=null или метрика не
//   forecastable — overlay не рисуется (в spec 010 это нормальный сценарий).
//
// Empty-state — при <2 точках истории показываем CTA вместо графика
// (REQ-01: график осмыслен от 2 точек).

import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import '../../app/branding/portal_app_bar.dart';
import '../../app/branding/portal_scaffold.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../app/branding/portal_backdrop.dart';
import '../../app/theme/app_colors.dart';
import '../../app/theme/app_spacing.dart';
import '../../data/api/analytics_api.dart';

class BodyAnalyticsScreen extends ConsumerWidget {
  const BodyAnalyticsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return PortalScaffold(
      appBar: PortalAppBar(title: const Text('Тело')),
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: () async {
            ref.invalidate(inbodySeriesProvider);
            await Future.wait([
              for (final m in _metrics)
                ref.read(inbodySeriesProvider(m.id).future),
            ]);
          },
          child: ListView(
            padding: const EdgeInsets.fromLTRB(
              AppSpacing.lg,
              AppSpacing.lg,
              AppSpacing.lg,
              AppSpacing.xxxl,
            ),
            children: [
              for (final m in _metrics) ...[
                _MetricSection(metric: m),
                const SizedBox(height: AppSpacing.lg),
              ],
              const _TipsSection(),
              const SizedBox(height: AppSpacing.lg),
            ],
          ),
        ),
      ),
    );
  }
}

class _MetricMeta {
  const _MetricMeta({
    required this.id,
    required this.title,
    required this.unit,
    required this.color,
  });

  final String id;
  final String title;
  final String unit;
  final Color color;
}

const _metrics = <_MetricMeta>[
  _MetricMeta(
    id: 'weight_kg',
    title: 'Вес',
    unit: 'кг',
    color: AppPalette.primary,
  ),
  _MetricMeta(
    id: 'body_fat_percent',
    title: 'Процент жира',
    unit: 'процентов',
    color: AppPalette.warning,
  ),
  _MetricMeta(
    id: 'muscle_mass_kg',
    title: 'Мышечная масса',
    unit: 'кг',
    color: AppPalette.success,
  ),
];

class _MetricSection extends ConsumerWidget {
  const _MetricSection({required this.metric});
  final _MetricMeta metric;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final async = ref.watch(inbodySeriesProvider(metric.id));
    return GlassCard(
      padding: const EdgeInsets.all(AppSpacing.lg),
      tintColor: metric.color,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
            Row(
              children: [
                Container(
                  width: 10,
                  height: 10,
                  decoration: BoxDecoration(
                    color: metric.color,
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: metric.color.withValues(alpha: 0.6),
                        blurRadius: 8,
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: AppSpacing.sm),
                Text(metric.title, style: theme.textTheme.titleMedium),
                const Spacer(),
                async.maybeWhen(
                  data: (dto) => _LatestLabel(dto: dto, unit: metric.unit),
                  orElse: () => const SizedBox.shrink(),
                ),
              ],
            ),
            const SizedBox(height: AppSpacing.md),
            SizedBox(
              height: 200,
              child: async.when(
                loading: () =>
                    const Center(child: CircularProgressIndicator(strokeWidth: 2)),
                error: (e, _) => _ErrorRow(
                  onRetry: () =>
                      ref.invalidate(inbodySeriesProvider(metric.id)),
                ),
                data: (dto) => dto.points.length < 2
                    ? const _EmptyChart()
                    : _LineChartView(dto: dto, color: metric.color),
              ),
            ),
            async.maybeWhen(
              data: (dto) => dto.forecast == null || dto.forecast!.isEmpty
                  ? const SizedBox.shrink()
                  : Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const SizedBox(height: AppSpacing.sm),
                        _ChartLegend(color: metric.color),
                        const SizedBox(height: AppSpacing.xs),
                        _ForecastCaption(
                          last: dto.points.isNotEmpty ? dto.points.last : null,
                          forecastLast: dto.forecast!.last,
                          unit: metric.unit,
                        ),
                      ],
                    ),
              orElse: () => const SizedBox.shrink(),
            ),
        ],
      ),
    );
  }
}

class _LatestLabel extends StatelessWidget {
  const _LatestLabel({required this.dto, required this.unit});
  final InBodySeriesResponseDto dto;
  final String unit;

  @override
  Widget build(BuildContext context) {
    if (dto.points.isEmpty) return const SizedBox.shrink();
    final last = dto.points.last;
    final theme = Theme.of(context);
    return Text(
      '${_fmtValue(last.value)} $unit',
      style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600),
    );
  }
}

class _ChartLegend extends StatelessWidget {
  const _ChartLegend({required this.color});
  final Color color;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final labelStyle = theme.textTheme.labelSmall?.copyWith(
      color: theme.colorScheme.onSurfaceVariant,
    );
    return Row(
      children: [
        Container(width: 16, height: 2, color: color),
        const SizedBox(width: AppSpacing.xs),
        Text('Ваши замеры', style: labelStyle),
        const SizedBox(width: AppSpacing.md),
        _DashedLine(color: color),
        const SizedBox(width: AppSpacing.xs),
        Text('Прогноз', style: labelStyle),
        const SizedBox(width: AppSpacing.md),
        Container(
          width: 16,
          height: 8,
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.15),
            borderRadius: BorderRadius.circular(2),
          ),
        ),
        const SizedBox(width: AppSpacing.xs),
        Text('Разброс', style: labelStyle),
      ],
    );
  }
}

class _DashedLine extends StatelessWidget {
  const _DashedLine({required this.color});
  final Color color;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 16,
      height: 2,
      child: CustomPaint(painter: _DashPainter(color: color)),
    );
  }
}

class _DashPainter extends CustomPainter {
  const _DashPainter({required this.color});
  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke;
    const dashWidth = 4.0;
    const gap = 2.0;
    var x = 0.0;
    while (x < size.width) {
      canvas.drawLine(
        Offset(x, size.height / 2),
        Offset((x + dashWidth).clamp(0, size.width), size.height / 2),
        paint,
      );
      x += dashWidth + gap;
    }
  }

  @override
  bool shouldRepaint(covariant _DashPainter old) => color != old.color;
}

class _ForecastCaption extends StatelessWidget {
  const _ForecastCaption({
    required this.last,
    required this.forecastLast,
    required this.unit,
  });
  final SeriesPointDto? last;
  final ForecastSeriesPointDto forecastLast;
  final String unit;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final base = last?.value;
    final delta = base == null ? null : forecastLast.value - base;
    final deltaStr = delta == null
        ? ''
        : '${delta >= 0 ? '+' : ''}${_fmtValue(delta)} $unit';
    return Row(
      children: [
        Icon(
          Icons.timeline,
          size: 16,
          color: theme.colorScheme.onSurfaceVariant,
        ),
        const SizedBox(width: AppSpacing.xs),
        Expanded(
          child: Text(
            'Ожидается ${_fmtValue(forecastLast.value)} $unit '
            'к ${_fmtDate(forecastLast.date)} '
            '(±${_fmtValue((forecastLast.ciHigh - forecastLast.ciLow) / 2)})'
            '${deltaStr.isEmpty ? '' : ' · $deltaStr'}',
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
        ),
      ],
    );
  }
}

class _EmptyChart extends StatelessWidget {
  const _EmptyChart();

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.show_chart,
            color: theme.colorScheme.onSurfaceVariant,
            size: 32,
          ),
          const SizedBox(height: AppSpacing.sm),
          Text(
            'Нужно ещё одно измерение,\nчтобы увидеть динамику',
            textAlign: TextAlign.center,
            style: theme.textTheme.bodyMedium?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
          const SizedBox(height: AppSpacing.sm),
          TextButton(
            onPressed: () => GoRouter.of(context).push('/inbody/upload-pdf'),
            child: const Text('Добавить замер'),
          ),
        ],
      ),
    );
  }
}

class _ErrorRow extends StatelessWidget {
  const _ErrorRow({required this.onRetry});
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.error_outline, color: theme.colorScheme.error),
          const SizedBox(width: AppSpacing.sm),
          TextButton(onPressed: onRetry, child: const Text('Повторить')),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// График: история сплошной + forecast пунктир + CI band
// ---------------------------------------------------------------------------

class _LineChartView extends StatelessWidget {
  const _LineChartView({required this.dto, required this.color});
  final InBodySeriesResponseDto dto;
  final Color color;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    // X-ось — миллисекунды эпохи; даёт корректный шаг между неравномерными
    // во времени замерами (без X-в-секундах прогноз сливается с историей).
    final history = dto.points
        .map((p) => FlSpot(
              p.date.millisecondsSinceEpoch.toDouble(),
              p.value,
            ))
        .toList();

    final forecastSpots = (dto.forecast ?? const [])
        .map((p) => FlSpot(
              p.date.millisecondsSinceEpoch.toDouble(),
              p.value,
            ))
        .toList();
    final ciLowSpots = (dto.forecast ?? const [])
        .map((p) => FlSpot(
              p.date.millisecondsSinceEpoch.toDouble(),
              p.ciLow,
            ))
        .toList();
    final ciHighSpots = (dto.forecast ?? const [])
        .map((p) => FlSpot(
              p.date.millisecondsSinceEpoch.toDouble(),
              p.ciHigh,
            ))
        .toList();

    // Чтобы forecast-линия начиналась из последней исторической точки —
    // префиксом добавляем её. Иначе появляется визуальный разрыв.
    if (history.isNotEmpty && forecastSpots.isNotEmpty) {
      forecastSpots.insert(0, history.last);
      ciLowSpots.insert(0, history.last);
      ciHighSpots.insert(0, history.last);
    }

    final allValues = [
      ...history.map((s) => s.y),
      ...ciLowSpots.map((s) => s.y),
      ...ciHighSpots.map((s) => s.y),
    ];
    final minY = allValues.reduce((a, b) => a < b ? a : b);
    final maxY = allValues.reduce((a, b) => a > b ? a : b);
    final pad = (maxY - minY).abs() * 0.15 + 0.5;
    final yBottom = minY - pad;
    final yTop = maxY + pad;
    final visibleRange = yTop - yBottom;
    final yInterval = visibleRange / 2;

    final bars = <LineChartBarData>[
      LineChartBarData(
        spots: history,
        isCurved: true,
        curveSmoothness: 0.25,
        color: color,
        barWidth: 2.5,
        isStrokeCapRound: true,
        dotData: FlDotData(
          show: true,
          getDotPainter: (spot, _, __, ___) => FlDotCirclePainter(
            radius: 3.5,
            color: Colors.white,
            strokeColor: color,
            strokeWidth: 2,
          ),
        ),
      ),
      if (forecastSpots.length >= 2)
        LineChartBarData(
          spots: forecastSpots,
          isCurved: false,
          color: color,
          barWidth: 2,
          dashArray: const [6, 4],
          dotData: const FlDotData(show: false),
        ),
      // Невидимые барс для CI band'а — между low и high.
      // betweenBarsData ниже использует индексы lineBarsData; держим
      // их рядом, иначе fl_chart нарисует band между неподходящими.
      if (ciLowSpots.length >= 2)
        LineChartBarData(
          spots: ciLowSpots,
          color: Colors.transparent,
          barWidth: 0,
          dotData: const FlDotData(show: false),
        ),
      if (ciHighSpots.length >= 2)
        LineChartBarData(
          spots: ciHighSpots,
          color: Colors.transparent,
          barWidth: 0,
          dotData: const FlDotData(show: false),
        ),
    ];

    final betweenBars = <BetweenBarsData>[];
    if (ciLowSpots.length >= 2 && ciHighSpots.length >= 2) {
      // Индексы 2 и 3 — те самые невидимые low/high бары добавленные выше.
      betweenBars.add(
        BetweenBarsData(
          fromIndex: bars.indexWhere((b) => b.spots == ciLowSpots),
          toIndex: bars.indexWhere((b) => b.spots == ciHighSpots),
          color: color.withValues(alpha: 0.15),
        ),
      );
    }

    return LineChart(
      LineChartData(
        minY: minY - pad,
        maxY: maxY + pad,
        gridData: FlGridData(
          show: true,
          drawVerticalLine: false,
          horizontalInterval: yInterval,
          getDrawingHorizontalLine: (_) => FlLine(
            color: theme.colorScheme.outline.withValues(alpha: 0.18),
            strokeWidth: 1,
          ),
        ),
        titlesData: FlTitlesData(
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 40,
              interval: yInterval,
              getTitlesWidget: (v, meta) {
                final distToEdge = [
                  (v - yBottom).abs(),
                  (v - yTop).abs(),
                ].reduce((a, b) => a < b ? a : b);
                if (distToEdge < yInterval * 0.4) {
                  return const SizedBox.shrink();
                }
                return Padding(
                  padding: const EdgeInsets.only(right: 4),
                  child: Text(
                    v.toStringAsFixed(v.truncateToDouble() == v ? 0 : 1),
                    style: theme.textTheme.labelSmall?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                );
              },
            ),
          ),
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 22,
              interval: _xInterval(history, forecastSpots),
              getTitlesWidget: (v, _) => Padding(
                padding: const EdgeInsets.only(top: 4),
                child: Text(
                  DateFormat('d MMM', 'ru').format(
                    DateTime.fromMillisecondsSinceEpoch(v.toInt()),
                  ),
                  style: theme.textTheme.labelSmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
              ),
            ),
          ),
          topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
        ),
        borderData: FlBorderData(show: false),
        lineBarsData: bars,
        betweenBarsData: betweenBars,
        lineTouchData: LineTouchData(
          touchTooltipData: LineTouchTooltipData(
            getTooltipColor: (_) => theme.colorScheme.surface,
            getTooltipItems: (touched) => touched
                .map((s) => LineTooltipItem(
                      '${_fmtValue(s.y)}\n'
                      '${DateFormat('d MMM yyyy', 'ru').format(DateTime.fromMillisecondsSinceEpoch(s.x.toInt()))}',
                      theme.textTheme.bodySmall ?? const TextStyle(),
                    ))
                .toList(),
          ),
        ),
      ),
    );
  }

  /// Ось X — даём 3-4 деления по умолчанию, чтобы метки не слипались.
  double? _xInterval(List<FlSpot> history, List<FlSpot> forecast) {
    final all = [...history, ...forecast];
    if (all.length < 2) return null;
    final span = all.last.x - all.first.x;
    return span / 3;
  }
}

String _fmtValue(double v) =>
    v.toStringAsFixed(v.truncateToDouble() == v ? 0 : 1);

String _fmtDate(DateTime d) => DateFormat('d MMM yyyy', 'ru').format(d);

// --- Рекомендации на основе ML-прогноза -----------------------------------

class _TipsSection extends ConsumerWidget {
  const _TipsSection();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final async = ref.watch(tipsProvider);
    return async.when(
      loading: () => const SizedBox.shrink(),
      error: (_, __) => const SizedBox.shrink(),
      data: (dto) {
        if (dto.tips.isEmpty) return const SizedBox.shrink();
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.lightbulb_outline,
                    color: theme.colorScheme.primary, size: 20),
                const SizedBox(width: AppSpacing.sm),
                Text(
                  dto.basedOnForecast
                      ? 'Рекомендации на основе прогноза'
                      : 'Рекомендации',
                  style: theme.textTheme.titleMedium,
                ),
              ],
            ),
            const SizedBox(height: AppSpacing.md),
            for (final tip in dto.tips) ...[
              _TipCard(tip: tip),
              const SizedBox(height: AppSpacing.sm),
            ],
          ],
        );
      },
    );
  }
}

class _TipCard extends StatelessWidget {
  const _TipCard({required this.tip});
  final TipDto tip;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final color = switch (tip.severity) {
      'warning' => AppPalette.warning,
      'success' => AppPalette.success,
      _ => theme.colorScheme.primary,
    };
    final icon = switch (tip.icon) {
      'water_drop' => Icons.water_drop,
      'egg' => Icons.egg,
      'science' => Icons.science,
      'monitor_heart' => Icons.monitor_heart,
      'fitness_center' => Icons.fitness_center,
      'trending_up' => Icons.trending_up,
      'trending_down' => Icons.trending_down,
      'directions_run' => Icons.directions_run,
      'warning' => Icons.warning_amber,
      'check_circle' => Icons.check_circle,
      _ => Icons.info_outline,
    };
    return Container(
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(AppRadius.md),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color, size: 22),
          const SizedBox(width: AppSpacing.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(tip.title,
                    style: theme.textTheme.titleSmall?.copyWith(color: color)),
                const SizedBox(height: AppSpacing.xs),
                Text(tip.body, style: theme.textTheme.bodySmall),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
