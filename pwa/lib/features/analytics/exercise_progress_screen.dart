// Экран «Прогресс по упражнению» (spec 010 §3 Scenario 4, REQ-09).
//
// Селект-with-search упражнения (через каталог) → по неделям рисуем:
//   - лучший рабочий вес (best_weight_kg) — основная линия;
//   - график динамики лучшего рабочего веса по неделям.
//
// CTA на /analytics/exercise открывается без пред-выбора упражнения;
// если пользователь так и не выбрал — empty state с инструкцией.

import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../app/theme/app_colors.dart';
import '../../app/theme/app_spacing.dart';
import '../../data/api/analytics_api.dart';
import '../../data/api/catalog_api.dart';
import '../../data/api/failure.dart';
import '../catalog/exercise_picker_screen.dart' show muscleRu;

class ExerciseProgressScreen extends ConsumerStatefulWidget {
  const ExerciseProgressScreen({super.key});

  @override
  ConsumerState<ExerciseProgressScreen> createState() =>
      _ExerciseProgressScreenState();
}

class _ExerciseProgressScreenState
    extends ConsumerState<ExerciseProgressScreen> {
  ExerciseSummaryDto? _selected;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Прогресс по упражнению')),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(AppSpacing.lg),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _ExercisePickerField(
                selected: _selected,
                onChanged: (e) => setState(() => _selected = e),
              ),
              const SizedBox(height: AppSpacing.lg),
              Expanded(
                child: _selected == null
                    ? _TrainedExercisesList(
                        onSelect: (e) => setState(() => _selected = e),
                      )
                    : _ProgressView(exercise: _selected!),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// --- Picker ----------------------------------------------------------------

class _ExercisePickerField extends ConsumerWidget {
  const _ExercisePickerField({
    required this.selected,
    required this.onChanged,
  });
  final ExerciseSummaryDto? selected;
  final ValueChanged<ExerciseSummaryDto> onChanged;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    return InkWell(
      onTap: () async {
        final picked = await showModalBottomSheet<ExerciseSummaryDto>(
          context: context,
          isScrollControlled: true,
          builder: (_) => const _ExercisePickerSheet(),
        );
        if (picked != null) onChanged(picked);
      },
      borderRadius: BorderRadius.circular(AppRadius.md),
      child: InputDecorator(
        decoration: InputDecoration(
          labelText: 'Упражнение',
          suffixIcon: const Icon(Icons.search),
          border: const OutlineInputBorder(),
          filled: true,
          fillColor: theme.colorScheme.surfaceContainerHigh,
        ),
        child: Text(
          selected?.displayName ?? 'Выберите упражнение',
          style: theme.textTheme.bodyLarge?.copyWith(
            color: selected == null
                ? theme.colorScheme.onSurfaceVariant
                : null,
          ),
        ),
      ),
    );
  }
}

class _ExercisePickerSheet extends ConsumerStatefulWidget {
  const _ExercisePickerSheet();

  @override
  ConsumerState<_ExercisePickerSheet> createState() =>
      _ExercisePickerSheetState();
}

class _ExercisePickerSheetState extends ConsumerState<_ExercisePickerSheet> {
  final _controller = TextEditingController();
  String _query = '';

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<ExerciseListResult> _fetch() {
    return ref.read(catalogApiProvider).list(
          query: _query.length >= 2 ? _query : null,
          limit: 40,
        );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final mediaInsets = MediaQuery.of(context).viewInsets;
    return Padding(
      padding: EdgeInsets.only(bottom: mediaInsets.bottom),
      child: FractionallySizedBox(
        heightFactor: 0.75,
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.all(AppSpacing.lg),
              child: TextField(
                controller: _controller,
                autofocus: true,
                decoration: const InputDecoration(
                  prefixIcon: Icon(Icons.search),
                  labelText: 'Поиск упражнения',
                  border: OutlineInputBorder(),
                ),
                onChanged: (v) => setState(() => _query = v),
              ),
            ),
            Expanded(
              child: FutureBuilder<ExerciseListResult>(
                future: _fetch(),
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.waiting) {
                    return const Center(child: CircularProgressIndicator());
                  }
                  if (snapshot.hasError) {
                    final msg = snapshot.error is AppFailure
                        ? (snapshot.error as AppFailure).message
                        : 'Не удалось загрузить каталог';
                    return Center(
                      child: Padding(
                        padding: const EdgeInsets.all(AppSpacing.lg),
                        child: Text(msg, textAlign: TextAlign.center),
                      ),
                    );
                  }
                  final data = snapshot.data;
                  if (data == null || data.items.isEmpty) {
                    return Center(
                      child: Padding(
                        padding: const EdgeInsets.all(AppSpacing.lg),
                        child: Text(
                          'Ничего не найдено',
                          style: theme.textTheme.bodyMedium?.copyWith(
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                        ),
                      ),
                    );
                  }
                  return ListView.separated(
                    itemCount: data.items.length,
                    separatorBuilder: (_, __) => Divider(
                      height: 1,
                      color: theme.colorScheme.outline.withValues(alpha: 0.18),
                    ),
                    itemBuilder: (_, i) {
                      final e = data.items[i];
                      return ListTile(
                        title: Text(e.displayName),
                        subtitle: Text(
                          muscleRu(e.primaryMuscleGroup),
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                        ),
                        onTap: () => Navigator.of(context).pop(e),
                      );
                    },
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// --- Progress view --------------------------------------------------------

class _ProgressView extends ConsumerWidget {
  const _ProgressView({required this.exercise});
  final ExerciseSummaryDto exercise;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(exerciseProgressProvider(exercise.id));
    return async.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, _) => _ErrorCard(
        error: e,
        onRetry: () => ref.invalidate(exerciseProgressProvider(exercise.id)),
      ),
      data: (data) {
        if (data.weeks.isEmpty) {
          return _EmptyView(exerciseTitle: data.exerciseTitle ?? exercise.displayName);
        }
        return _ProgressChartCard(data: data);
      },
    );
  }
}

class _ProgressChartCard extends StatelessWidget {
  const _ProgressChartCard({required this.data});
  final ExerciseProgressResponseDto data;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final last = data.weeks.last;
    return ListView(
      children: [
        Container(
          padding: const EdgeInsets.all(AppSpacing.lg),
          decoration: BoxDecoration(
            color: theme.colorScheme.surfaceContainerHigh,
            borderRadius: BorderRadius.circular(AppRadius.lg),
            border: Border.all(color: theme.colorScheme.outline),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _MetricLabel(
                label: 'Лучший вес',
                value: '${last.bestWeightKg.toStringAsFixed(1)} кг',
                color: AppPalette.primary,
              ),
              const SizedBox(height: AppSpacing.lg),
              SizedBox(
                height: 240,
                child: _LineChart(weeks: data.weeks),
              ),
            ],
          ),
        ),
        const SizedBox(height: AppSpacing.lg),
        Container(
          padding: const EdgeInsets.all(AppSpacing.lg),
          decoration: BoxDecoration(
            color: theme.colorScheme.surfaceContainerHigh,
            borderRadius: BorderRadius.circular(AppRadius.lg),
            border: Border.all(color: theme.colorScheme.outline),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('История по неделям', style: theme.textTheme.titleMedium),
              const SizedBox(height: AppSpacing.sm),
              for (final w in data.weeks.reversed) ...[
                _WeekRow(week: w),
                Divider(
                  height: 1,
                  color: theme.colorScheme.outline.withValues(alpha: 0.18),
                ),
              ],
            ],
          ),
        ),
      ],
    );
  }
}

class _MetricLabel extends StatelessWidget {
  const _MetricLabel({
    required this.label,
    required this.value,
    required this.color,
  });
  final String label;
  final String value;
  final Color color;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Container(
              width: 10,
              height: 10,
              decoration: BoxDecoration(color: color, shape: BoxShape.circle),
            ),
            const SizedBox(width: AppSpacing.sm),
            Text(
              label,
              style: theme.textTheme.labelSmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
                letterSpacing: 1.1,
              ),
            ),
          ],
        ),
        const SizedBox(height: AppSpacing.xs),
        Text(value, style: theme.textTheme.headlineSmall),
      ],
    );
  }
}

class _LineChart extends StatelessWidget {
  const _LineChart({required this.weeks});
  final List<ExerciseProgressWeekDto> weeks;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final bestSpots = weeks
        .map(
          (w) => FlSpot(
            w.weekStart.millisecondsSinceEpoch.toDouble(),
            w.bestWeightKg,
          ),
        )
        .toList();
    final allValues = bestSpots.map((s) => s.y).toList();
    final minY = allValues.reduce((a, b) => a < b ? a : b);
    final maxY = allValues.reduce((a, b) => a > b ? a : b);
    final pad = (maxY - minY).abs() * 0.15 + 0.5;
    return LineChart(
      LineChartData(
        minY: minY - pad,
        maxY: maxY + pad,
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
                  v.toStringAsFixed(0),
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
              reservedSize: 22,
              interval: bestSpots.length >= 2
                  ? (bestSpots.last.x - bestSpots.first.x) / 3
                  : null,
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
          rightTitles:
              const AxisTitles(sideTitles: SideTitles(showTitles: false)),
        ),
        borderData: FlBorderData(show: false),
        lineBarsData: [
          LineChartBarData(
            spots: bestSpots,
            isCurved: true,
            curveSmoothness: 0.25,
            color: AppPalette.primary,
            barWidth: 2.5,
            isStrokeCapRound: true,
            dotData: FlDotData(
              show: true,
              getDotPainter: (spot, _, __, ___) => FlDotCirclePainter(
                radius: 3.5,
                color: Colors.white,
                strokeColor: AppPalette.primary,
                strokeWidth: 2,
              ),
            ),
          ),
        ],
        lineTouchData: LineTouchData(
          touchTooltipData: LineTouchTooltipData(
            getTooltipColor: (_) => theme.colorScheme.surface,
            getTooltipItems: (touched) => touched
                .map(
                  (s) => LineTooltipItem(
                    '${s.y.toStringAsFixed(1)} кг\n'
                    '${DateFormat('d MMM yyyy', 'ru').format(DateTime.fromMillisecondsSinceEpoch(s.x.toInt()))}',
                    theme.textTheme.bodySmall ?? const TextStyle(),
                  ),
                )
                .toList(),
          ),
        ),
      ),
    );
  }
}

class _WeekRow extends StatelessWidget {
  const _WeekRow({required this.week});
  final ExerciseProgressWeekDto week;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: AppSpacing.sm),
      child: Row(
        children: [
          Expanded(
            flex: 3,
            child: Text(
              'Неделя ${DateFormat('d MMM', 'ru').format(week.weekStart)}',
              style: theme.textTheme.bodyMedium,
            ),
          ),
          Expanded(
            flex: 4,
            child: Text(
              '${week.bestWeightKg.toStringAsFixed(1)} кг',
              textAlign: TextAlign.right,
              style: theme.textTheme.bodyMedium,
            ),
          ),
          Expanded(
            flex: 1,
            child: Text(
              '${week.sets}×',
              textAlign: TextAlign.right,
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _EmptyView extends StatelessWidget {
  const _EmptyView({required this.exerciseTitle});
  final String exerciseTitle;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.fitness_center_outlined,
            size: 56,
            color: theme.colorScheme.onSurfaceVariant,
          ),
          const SizedBox(height: AppSpacing.md),
          Text(
            'Нет завершённых подходов\nпо «$exerciseTitle»',
            style: theme.textTheme.titleMedium,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: AppSpacing.sm),
          Text(
            'Сделайте хотя бы один подход — и здесь появится кривая прогресса.',
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

/// Стартовый список: упражнения, по которым у пользователя есть логи.
/// Тап → выбор того же DTO, что отдаёт каталоговый picker — поэтому
/// для совместимости конвертируем TrainedExerciseDto → ExerciseSummaryDto.
class _TrainedExercisesList extends ConsumerWidget {
  const _TrainedExercisesList({required this.onSelect});
  final ValueChanged<ExerciseSummaryDto> onSelect;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(trainedExercisesProvider);
    final theme = Theme.of(context);
    return async.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, _) => _ErrorCard(
        error: e,
        onRetry: () => ref.invalidate(trainedExercisesProvider),
      ),
      data: (items) {
        if (items.isEmpty) {
          return Center(
            child: Padding(
              padding: const EdgeInsets.all(AppSpacing.lg),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    Icons.fitness_center_outlined,
                    size: 56,
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                  const SizedBox(height: AppSpacing.md),
                  Text(
                    'Пока нет тренированных упражнений',
                    style: theme.textTheme.titleMedium,
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: AppSpacing.sm),
                  Text(
                    'Сделайте подход — упражнение появится в этом списке.\nИли воспользуйтесь поиском выше.',
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
        return Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Padding(
              padding: const EdgeInsets.only(bottom: AppSpacing.sm),
              child: Text(
                'ВЫ УЖЕ ДЕЛАЛИ',
                style: theme.textTheme.labelSmall?.copyWith(
                  color: theme.colorScheme.primary,
                  letterSpacing: 1.2,
                ),
              ),
            ),
            Expanded(
              child: ListView.separated(
                itemCount: items.length,
                separatorBuilder: (_, __) => const SizedBox(
                  height: AppSpacing.sm,
                ),
                itemBuilder: (_, i) {
                  final it = items[i];
                  return _TrainedExerciseTile(
                    item: it,
                    onTap: () => onSelect(_toSummary(it)),
                  );
                },
              ),
            ),
          ],
        );
      },
    );
  }

  ExerciseSummaryDto _toSummary(TrainedExerciseDto e) => ExerciseSummaryDto(
        id: e.id,
        exerciseId: e.id,
        name: e.exerciseName,
        nameRu: e.exerciseNameRu,
        primaryMuscleGroup: e.primaryMuscleGroup,
        equipment: e.equipment,
        bodyRegion: '',
        isFavorite: false,
        isMine: false,
      );
}

class _TrainedExerciseTile extends StatelessWidget {
  const _TrainedExerciseTile({required this.item, required this.onTap});
  final TrainedExerciseDto item;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Material(
      color: theme.colorScheme.surfaceContainerHigh,
      borderRadius: BorderRadius.circular(AppRadius.lg),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(AppRadius.lg),
        child: Container(
          padding: const EdgeInsets.all(AppSpacing.md),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(AppRadius.lg),
            border: Border.all(color: theme.colorScheme.outline),
          ),
          child: Row(
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: theme.colorScheme.primary.withValues(alpha: 0.16),
                  borderRadius: BorderRadius.circular(AppRadius.md),
                ),
                child: Icon(
                  Icons.fitness_center,
                  color: theme.colorScheme.primary,
                  size: 20,
                ),
              ),
              const SizedBox(width: AppSpacing.md),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(item.displayName, style: theme.textTheme.titleMedium),
                    const SizedBox(height: 2),
                    Text(
                      '${muscleRu(item.primaryMuscleGroup)} · '
                      '${item.setsCount} подходов',
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
    return Center(
      child: Container(
        padding: const EdgeInsets.all(AppSpacing.lg),
        decoration: BoxDecoration(
          color: theme.colorScheme.error.withValues(alpha: 0.10),
          borderRadius: BorderRadius.circular(AppRadius.lg),
          border: Border.all(
            color: theme.colorScheme.error.withValues(alpha: 0.4),
          ),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.cloud_off, color: theme.colorScheme.error, size: 32),
            const SizedBox(height: AppSpacing.sm),
            Text(message, textAlign: TextAlign.center),
            const SizedBox(height: AppSpacing.md),
            OutlinedButton(onPressed: onRetry, child: const Text('Повторить')),
          ],
        ),
      ),
    );
  }
}
