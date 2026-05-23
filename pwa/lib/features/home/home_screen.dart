import 'dart:ui';

import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import '../../app/branding/portal_scaffold.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/l10n/generated/app_localizations.dart';
import '../../app/theme/app_colors.dart';
import '../../app/theme/app_spacing.dart';
import '../../app/branding/portal_backdrop.dart';
import '../../data/api/analytics_api.dart';
import '../../data/api/failure.dart';
import '../../data/api/profile_api.dart';
import '../../data/api/workouts_api.dart';
import '../workouts/workout_actions.dart';

Future<void> _startWorkoutFromHome(BuildContext context, WidgetRef ref) async {
  try {
    // Если активная уже есть — переходим к ней.
    final existing = await ref.read(workoutsApiProvider).active();
    if (existing != null) {
      if (!context.mounted) return;
      context.go('/training/active/${existing.id}');
      return;
    }
    final w = await ref.read(workoutsApiProvider).start();
    ref.invalidate(activeWorkoutProvider);
    if (!context.mounted) return;
    context.go('/training/active/${w.id}');
  } on AppFailure catch (f) {
    if (!context.mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(f.message)));
  }
}

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final overview = ref.watch(overviewProvider);

    return PortalScaffold(
      floatingActionButton: Padding(
        padding: const EdgeInsets.only(bottom: 80),
        child: FloatingActionButton(
          onPressed: () => _startWorkoutFromHome(context, ref),
          child: const Icon(Icons.add, size: 28),
        ),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.endFloat,
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: () async => ref.refresh(overviewProvider.future),
          child: overview.when(
            loading: () => const _LoadingSkeleton(),
            error: (err, _) => _ErrorView(
              error: err,
              onRetry: () => ref.invalidate(overviewProvider),
            ),
            data: (data) => _OverviewContent(data: data),
          ),
        ),
      ),
    );
  }
}

// --- Content ---------------------------------------------------------------

class _OverviewContent extends StatelessWidget {
  const _OverviewContent({required this.data});
  final OverviewResponseDto data;

  @override
  Widget build(BuildContext context) {
    final hasAnyData = data.metrics.workoutsThisMonth > 0 ||
        data.recent.isNotEmpty ||
        data.metrics.totalWeightKg > 0;

    return ListView(
      padding: const EdgeInsets.fromLTRB(
        AppSpacing.lg,
        AppSpacing.lg,
        AppSpacing.lg,
        AppSpacing.xxxl * 2 + 100,
      ),
      children: [
        const _Header(),
        const SizedBox(height: AppSpacing.xxl),
        if (!hasAnyData)
          const _EmptyState()
        else ...[
          const _SectionLabel(textKey: 'performance'),
          const SizedBox(height: AppSpacing.md),
          _PerformanceMetrics(metrics: data.metrics),
          const SizedBox(height: AppSpacing.xxl),
          const _TipsSection(),
          if (data.strength != null) ...[
            const _SectionLabel(textKey: 'strength'),
            const SizedBox(height: AppSpacing.md),
            _StrengthCard(strength: data.strength!),
            const SizedBox(height: AppSpacing.xxl),
          ],
          if (data.recent.isNotEmpty) ...[
            const _RecentHeader(),
            const SizedBox(height: AppSpacing.md),
            _RecentList(items: data.recent),
          ],
        ],
      ],
    );
  }
}

// --- Header ----------------------------------------------------------------

class _Header extends ConsumerWidget {
  const _Header();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final l = AppLocalizations.of(context);
    final profileAsync = ref.watch(profileProvider);

    final monthLabel = _currentMonthLabelRu();

    return Row(
      children: [
        InkWell(
          onTap: () => context.go('/profile'),
          customBorder: const CircleBorder(),
          child: _HomeAvatar(
            photoUrl: profileAsync.valueOrNull?.photoUrl,
            name: profileAsync.valueOrNull?.name,
          ),
        ),
        const SizedBox(width: AppSpacing.md),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(l.homeTitle, style: theme.textTheme.headlineMedium),
              Text(
                monthLabel,
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

class _HomeAvatar extends StatelessWidget {
  const _HomeAvatar({required this.photoUrl, required this.name});
  final String? photoUrl;
  final String? name;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    const size = 48.0;
    final initial = (name ?? '').trim().isNotEmpty
        ? (name!.trim()[0].toUpperCase())
        : null;

    final container = Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        border: Border.all(color: theme.colorScheme.outline),
        color: theme.colorScheme.surfaceContainerHigh,
      ),
      alignment: Alignment.center,
      child: initial != null
          ? Text(
              initial,
              style: theme.textTheme.titleMedium?.copyWith(
                color: theme.colorScheme.onSurface,
                fontWeight: FontWeight.w600,
              ),
            )
          : Icon(
              Icons.person,
              color: theme.colorScheme.onSurfaceVariant,
              size: 24,
            ),
    );

    if (photoUrl == null) return container;
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        border: Border.all(color: theme.colorScheme.outline),
        color: theme.colorScheme.surfaceContainerHigh,
      ),
      clipBehavior: Clip.antiAlias,
      child: ClipOval(
        child: Image.network(
          photoUrl!,
          width: size,
          height: size,
          fit: BoxFit.cover,
          errorBuilder: (_, __, ___) => container,
        ),
      ),
    );
  }
}

// --- Empty state -----------------------------------------------------------

class _EmptyState extends ConsumerWidget {
  const _EmptyState();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    return _Card(
      padding: const EdgeInsets.all(AppSpacing.xxl),
      child: Column(
        children: [
          Container(
            width: 96,
            height: 96,
            decoration: BoxDecoration(
              color: theme.colorScheme.primary.withValues(alpha: 0.16),
              borderRadius: BorderRadius.circular(AppRadius.xl),
            ),
            child: Icon(
              Icons.fitness_center,
              size: 48,
              color: theme.colorScheme.primary,
            ),
          ),
          const SizedBox(height: AppSpacing.lg),
          Text(
            'Здесь появится ваш прогресс',
            style: theme.textTheme.titleLarge,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: AppSpacing.sm),
          Text(
            'Начни первую тренировку — вернись сюда после, и увидишь метрики, графики силы и историю',
            style: theme.textTheme.bodyMedium?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: AppSpacing.xl),
          ElevatedButton(
            onPressed: () => _startWorkoutFromHome(context, ref),
            child: const Text('Начать тренировку'),
          ),
        ],
      ),
    );
  }
}

// --- Loading / Error -------------------------------------------------------

class _LoadingSkeleton extends StatelessWidget {
  const _LoadingSkeleton();

  @override
  Widget build(BuildContext context) {
    return const Center(child: CircularProgressIndicator());
  }
}

class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.error, required this.onRetry});
  final Object error;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final message = error is AppFailure
        ? (error as AppFailure).message
        : 'Не удалось загрузить данные';
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.xxl),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.cloud_off, size: 48, color: theme.colorScheme.error),
            const SizedBox(height: AppSpacing.md),
            Text(message, textAlign: TextAlign.center),
            const SizedBox(height: AppSpacing.lg),
            OutlinedButton(onPressed: onRetry, child: const Text('Повторить')),
          ],
        ),
      ),
    );
  }
}

// --- Section header --------------------------------------------------------

class _SectionLabel extends StatelessWidget {
  const _SectionLabel({required this.textKey});
  final String textKey;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l = AppLocalizations.of(context);
    final text = switch (textKey) {
      'performance' => l.homeSectionPerformance,
      'strength' => l.homeSectionStrength,
      'recent' => l.homeSectionRecent,
      'tips' => 'Рекомендации',
      _ => textKey,
    };
    // letter-spacing уже зашит в textTheme.labelSmall (0.8) — раньше
    // override 1.6 был «трендом 2022»; в новой системе шире буквы
    // выглядят винтажно.
    return Text(
      text.toUpperCase(),
      style: theme.textTheme.labelSmall?.copyWith(
        color: theme.colorScheme.primary,
      ),
    );
  }
}

// --- Performance metrics ---------------------------------------------------

class _PerformanceMetrics extends StatelessWidget {
  const _PerformanceMetrics({required this.metrics});
  final OverviewMetricsDto metrics;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        _BigMetricCard(value: metrics.workoutsThisMonth),
        const SizedBox(height: AppSpacing.md),
        IntrinsicHeight(
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Expanded(
                child: _TotalWeightCard(
                  totalKg: metrics.totalWeightKg,
                  deltaPercent: metrics.totalWeightDeltaPercent,
                ),
              ),
              const SizedBox(width: AppSpacing.md),
              Expanded(
                child: _StreakCard(
                  streakDays: metrics.activeStreakDays,
                  isPersonalBest: metrics.streakIsPersonalBest,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _BigMetricCard extends StatelessWidget {
  const _BigMetricCard({required this.value});
  final int value;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l = AppLocalizations.of(context);

    return _Card(
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  l.homeMetricWorkoutsThisMonth.toUpperCase(),
                  style: theme.textTheme.labelSmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
                const SizedBox(height: AppSpacing.sm),
                Text(
                  '$value',
                  style: theme.textTheme.displayMedium?.copyWith(height: 1),
                ),
              ],
            ),
          ),
          Container(
            width: 56,
            height: 56,
            decoration: BoxDecoration(
              color: theme.colorScheme.primary.withValues(alpha: 0.18),
              borderRadius: BorderRadius.circular(AppRadius.md),
            ),
            child: Icon(
              Icons.fitness_center,
              color: theme.colorScheme.primary,
              size: 28,
            ),
          ),
        ],
      ),
    );
  }
}

class _TotalWeightCard extends StatelessWidget {
  const _TotalWeightCard({required this.totalKg, required this.deltaPercent});
  final int totalKg;
  final int deltaPercent;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l = AppLocalizations.of(context);
    final isPositive = deltaPercent >= 0;
    final deltaText = isPositive ? '+$deltaPercent' : '$deltaPercent';

    return _Card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            l.homeMetricTotalWeight.toUpperCase(),
            style: theme.textTheme.labelSmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
          const SizedBox(height: AppSpacing.sm),
          Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                _formatThousands(totalKg),
                style: theme.textTheme.headlineMedium,
              ),
              const SizedBox(width: 4),
              Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Text(
                  l.homeMetricTotalWeightUnit,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.xs),
          if (deltaPercent != 0)
            Row(
              children: [
                Icon(
                  isPositive ? Icons.trending_up : Icons.trending_down,
                  color: AppPalette.success,
                  size: 16,
                ),
                const SizedBox(width: 4),
                Expanded(
                  child: Text(
                    l.homeMetricVsLastMonth(deltaText),
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: AppPalette.success,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
        ],
      ),
    );
  }
}

class _StreakCard extends StatelessWidget {
  const _StreakCard({required this.streakDays, required this.isPersonalBest});
  final int streakDays;
  final bool isPersonalBest;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l = AppLocalizations.of(context);

    return _Card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            l.homeMetricActiveStreak.toUpperCase(),
            style: theme.textTheme.labelSmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
          const SizedBox(height: AppSpacing.sm),
          Text(
            l.homeMetricActiveStreakDays(streakDays),
            style: theme.textTheme.headlineMedium,
          ),
          const SizedBox(height: AppSpacing.xs),
          if (isPersonalBest)
            Row(
              children: [
                Icon(
                  Icons.local_fire_department,
                  color: theme.colorScheme.primary,
                  size: 16,
                ),
                const SizedBox(width: 4),
                Expanded(
                  child: Text(
                    l.homeMetricPersonalBest,
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.primary,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
        ],
      ),
    );
  }
}

// --- Strength chart --------------------------------------------------------

class _StrengthCard extends StatelessWidget {
  const _StrengthCard({required this.strength});
  final StrengthProgressDto strength;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l = AppLocalizations.of(context);

    return _Card(
      padding: const EdgeInsets.fromLTRB(
        AppSpacing.lg,
        AppSpacing.lg,
        AppSpacing.lg,
        AppSpacing.md,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Flexible(
                child: _ExerciseChip(
                  title: strength.exerciseTitle ?? l.homeStrengthExercise,
                ),
              ),
              const SizedBox(width: AppSpacing.md),
              Text(
                l.homeStrengthLast30Days,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            'Упражнение, в котором было больше всего подходов',
            style: theme.textTheme.labelSmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
          const SizedBox(height: AppSpacing.md),
          Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                '${strength.currentMaxKg}',
                style: theme.textTheme.displayLarge?.copyWith(height: 1),
              ),
              const SizedBox(width: 8),
              Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Text(
                  l.homeStrengthUnit,
                  style: theme.textTheme.titleMedium?.copyWith(
                    color: theme.colorScheme.primary,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.lg),
          SizedBox(
            height: 140,
            child: _StrengthLineChart(points: strength.points),
          ),
        ],
      ),
    );
  }
}

class _ExerciseChip extends StatelessWidget {
  const _ExerciseChip({required this.title});
  final String title;

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
        title.toUpperCase(),
        style: theme.textTheme.labelSmall?.copyWith(
          color: theme.colorScheme.primary,
        ),
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
      ),
    );
  }
}

class _StrengthLineChart extends StatelessWidget {
  const _StrengthLineChart({required this.points});
  final List<StrengthPointDto> points;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
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
              checkToShowDot: (spot, _) =>
                  spots.isNotEmpty && spot.x == spots.last.x,
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

// --- Recent activity -------------------------------------------------------

class _RecentHeader extends StatelessWidget {
  const _RecentHeader();

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l = AppLocalizations.of(context);
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          l.homeSectionRecent.toUpperCase(),
          style: theme.textTheme.labelSmall?.copyWith(
            color: theme.colorScheme.primary,
          ),
        ),
        TextButton(
          onPressed: () => context.go('/stats'),
          style: TextButton.styleFrom(
            padding: EdgeInsets.zero,
            minimumSize: Size.zero,
            tapTargetSize: MaterialTapTargetSize.shrinkWrap,
          ),
          child: Text(l.homeRecentViewAll),
        ),
      ],
    );
  }
}

class _RecentList extends StatelessWidget {
  const _RecentList({required this.items});
  final List<RecentWorkoutDto> items;

  @override
  Widget build(BuildContext context) {
    return WorkoutActionsAutoClose(
      child: Column(
        children: [
          for (var i = 0; i < items.length; i++) ...[
            _ActivityCard(item: items[i]),
            if (i != items.length - 1) const SizedBox(height: AppSpacing.md),
          ],
        ],
      ),
    );
  }
}

class _ActivityCard extends ConsumerWidget {
  const _ActivityCard({required this.item});
  final RecentWorkoutDto item;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final l = AppLocalizations.of(context);

    return WorkoutActionsSlidable(
      workoutId: item.id,
      onDeleted: () {
        ref.invalidate(overviewProvider);
        ref.invalidate(workoutHistoryProvider);
        ref.invalidate(activeWorkoutProvider);
      },
      borderRadius: AppRadius.xl,
      child: Material(
        color: theme.colorScheme.surfaceContainerHigh,
        borderRadius: BorderRadius.circular(AppRadius.xl),
        child: InkWell(
          onTap: () => context.push('/training/view/${item.id}'),
          borderRadius: BorderRadius.circular(AppRadius.xl),
          child: Container(
            padding: const EdgeInsets.symmetric(
              horizontal: AppSpacing.lg,
              vertical: AppSpacing.md,
            ),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(AppRadius.xl),
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
                  _iconForKind(item.kind),
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
                      item.dayLabel,
                      style: theme.textTheme.labelSmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(item.title, style: theme.textTheme.titleMedium),
                    const SizedBox(height: 2),
                    Text(
                      l.homeActivitySetsRepsAt(
                          item.sets, item.reps, item.weightKg),
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
                size: 20,
              ),
            ],
          ),
        ),
      ),
      ),
    );
  }
}

IconData _iconForKind(String kind) => switch (kind) {
      'full_body' => Icons.calendar_today_outlined,
      'push' => Icons.bolt_outlined,
      'legs' => Icons.fitness_center_outlined,
      'pull' => Icons.arrow_downward,
      'cardio' => Icons.directions_run,
      _ => Icons.fitness_center_outlined,
    };

// --- Generic card ----------------------------------------------------------

class _Card extends StatelessWidget {
  const _Card({
    required this.child,
    this.padding = const EdgeInsets.all(AppSpacing.lg),
  });

  final Widget child;
  final EdgeInsets padding;

  @override
  Widget build(BuildContext context) {
    // Все карточки на главной теперь — liquid-glass поверх PortalBackdrop.
    return GlassCard(padding: padding, child: child);
  }
}

// --- Helpers ---------------------------------------------------------------

String _formatThousands(int value) {
  final s = value.toString();
  final buf = StringBuffer();
  for (var i = 0; i < s.length; i++) {
    final reverseIndex = s.length - i;
    if (i != 0 && reverseIndex % 3 == 0) buf.write(',');
    buf.write(s[i]);
  }
  return buf.toString();
}

String _currentMonthLabelRu() {
  const months = [
    'Январь',
    'Февраль',
    'Март',
    'Апрель',
    'Май',
    'Июнь',
    'Июль',
    'Август',
    'Сентябрь',
    'Октябрь',
    'Ноябрь',
    'Декабрь',
  ];
  final now = DateTime.now();
  return '${months[now.month - 1]} ${now.year}';
}


// --- Рекомендации на основе ML-прогноза -----------------------------------

IconData _tipIcon(String name) => switch (name) {
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
  _ => Icons.lightbulb_outline,
};

class _TipsSection extends ConsumerWidget {
  const _TipsSection();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(tipsProvider);
    return async.when(
      loading: () => const SizedBox.shrink(),
      error: (_, __) => const SizedBox.shrink(),
      data: (dto) {
        if (dto.tips.isEmpty) return const SizedBox.shrink();
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _BodyStatusCard(tips: dto.tips, basedOnForecast: dto.basedOnForecast),
            const SizedBox(height: AppSpacing.lg),
          ],
        );
      },
    );
  }
}

class _BodyStatusCard extends StatelessWidget {
  const _BodyStatusCard({required this.tips, required this.basedOnForecast});
  final List<TipDto> tips;
  final bool basedOnForecast;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final warnings = tips.where((t) => t.severity == 'warning').length;
    final infos = tips.where((t) => t.severity == 'info').length;
    final issues = warnings + infos;
    final total = tips.length;
    final successOnly = issues == 0 && total > 0;

    final Color statusColor;
    final String statusLabel;
    final String statusDetail;
    final double score;

    if (successOnly) {
      statusColor = AppPalette.success;
      statusLabel = 'Всё в порядке';
      statusDetail = 'Показатели в норме — так держать!';
      score = 1.0;
    } else if (warnings == 0 && infos <= 2) {
      statusColor = AppPalette.success;
      statusLabel = 'В целом неплохо';
      statusDetail = _buildSummary(tips);
      score = 0.75;
    } else if (warnings <= 2) {
      statusColor = AppPalette.warning;
      statusLabel = 'Обратите внимание';
      statusDetail = _buildSummary(tips);
      score = 0.5;
    } else {
      statusColor = const Color(0xFFEF6C00);
      statusLabel = 'Стоит поработать';
      statusDetail = _buildSummary(tips);
      score = 0.3;
    }

    return GestureDetector(
      onTap: () => context.push('/analytics/body'),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(
              color: statusColor.withValues(alpha: 0.25),
              blurRadius: 28,
              spreadRadius: -6,
              offset: const Offset(0, 8),
            ),
          ],
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(20),
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 24, sigmaY: 24),
            child: Container(
              padding: const EdgeInsets.all(AppSpacing.xl),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(20),
                color: theme.colorScheme.surfaceContainerHigh
                    .withValues(alpha: 0.55),
                border: Border.all(
                  color: statusColor.withValues(alpha: 0.3),
                ),
              ),
              child: Row(
                children: [
                  SizedBox(
                    width: 72,
                    height: 72,
                    child: Stack(
                      alignment: Alignment.center,
                      children: [
                        SizedBox(
                          width: 72,
                          height: 72,
                          child: CircularProgressIndicator(
                            value: score,
                            strokeWidth: 5,
                            backgroundColor:
                                statusColor.withValues(alpha: 0.15),
                            valueColor:
                                AlwaysStoppedAnimation<Color>(statusColor),
                            strokeCap: StrokeCap.round,
                          ),
                        ),
                        Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(
                              '$total',
                              style:
                                  theme.textTheme.headlineSmall?.copyWith(
                                color: statusColor,
                                fontWeight: FontWeight.w700,
                                height: 1,
                              ),
                            ),
                            Text(
                              _tipWord(total),
                              style:
                                  theme.textTheme.labelSmall?.copyWith(
                                color: statusColor.withValues(alpha: 0.8),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: AppSpacing.lg),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          statusLabel,
                          style: theme.textTheme.titleMedium?.copyWith(
                            color: statusColor,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        const SizedBox(height: AppSpacing.xs),
                        Text(
                          statusDetail,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: theme.colorScheme.onSurface
                                .withValues(alpha: 0.7),
                            height: 1.4,
                          ),
                        ),
                        const SizedBox(height: AppSpacing.sm),
                        Text(
                          'Посмотреть все советы →',
                          style: theme.textTheme.labelMedium?.copyWith(
                            color: statusColor,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  String _buildSummary(List<TipDto> tips) {
    final issues = tips
        .where((t) => t.severity == 'warning' || t.severity == 'info')
        .toList();
    if (issues.isEmpty) return 'Показатели в норме';
    return issues.map((t) => t.title).take(2).join(' · ');
  }

  String _tipWord(int n) {
    if (n % 10 == 1 && n % 100 != 11) return 'совет';
    if (n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 10 || n % 100 >= 20)) {
      return 'совета';
    }
    return 'советов';
  }
}
