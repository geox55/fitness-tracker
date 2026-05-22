import 'package:flutter/material.dart';
import '../../app/branding/portal_scaffold.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/theme/app_spacing.dart';
import '../../data/api/catalog_api.dart';
import '../../data/api/failure.dart';
import '../../data/api/workouts_api.dart';

/// Read-only просмотр прошлой тренировки: дата/длительность + сгруппированные
/// по упражнениям подходы. Из главной/тренировки/статистики тапом сюда —
/// «посмотреть, что я делал». Для активной (in_progress) тренировки тап
/// ведёт сразу на active-экран, а сюда заходят только для завершённых.
class WorkoutDetailScreen extends ConsumerStatefulWidget {
  const WorkoutDetailScreen({super.key, required this.workoutId});

  final String workoutId;

  @override
  ConsumerState<WorkoutDetailScreen> createState() =>
      _WorkoutDetailScreenState();
}

class _WorkoutDetailScreenState extends ConsumerState<WorkoutDetailScreen> {
  WorkoutDto? _workout;
  final Map<String, ExerciseSummaryDto> _exerciseCache = {};
  bool _loaded = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final w = await ref.read(workoutsApiProvider).get(widget.workoutId);
      if (!mounted) return;
      // Параллельно подтянем уникальные упражнения — список обычно 4-8 шт.,
      // последовательные запросы тоже сошли бы, но parallel быстрее.
      final uniqueIds = w.logs.map((l) => l.exerciseId).toSet().toList();
      final api = ref.read(catalogApiProvider);
      await Future.wait(uniqueIds.map((id) async {
        try {
          final ex = await api.getById(id);
          _exerciseCache[id] = ex;
        } on AppFailure {
          // Пропускаем: упражнение могло быть удалено — покажем «Упражнение».
        }
      }));
      if (!mounted) return;
      setState(() {
        _workout = w;
        _loaded = true;
      });
    } on AppFailure catch (f) {
      if (!mounted) return;
      setState(() {
        _error = f.message;
        _loaded = true;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return PortalScaffold(
      appBar: AppBar(
        title: const Text('Тренировка'),
        actions: [
          if (_workout != null && _workout!.status != 'in_progress')
            IconButton(
              tooltip: 'Изменить',
              onPressed: () =>
                  context.push('/training/edit/${widget.workoutId}'),
              icon: const Icon(Icons.edit_outlined),
            ),
        ],
      ),
      body: !_loaded
          ? const Center(child: CircularProgressIndicator())
          : _workout == null
              ? Center(
                  child: Text(
                    _error ?? 'Не удалось загрузить тренировку',
                    style: TextStyle(color: theme.colorScheme.error),
                  ),
                )
              : _buildBody(context, _workout!),
    );
  }

  Widget _buildBody(BuildContext context, WorkoutDto w) {
    final theme = Theme.of(context);
    // Группировка логов по упражнению с сохранением порядка появления —
    // первое упражнение должно остаться первым.
    final order = <String>[];
    final byExercise = <String, List<ExerciseLogDto>>{};
    for (final l in w.logs) {
      if (!byExercise.containsKey(l.exerciseId)) {
        order.add(l.exerciseId);
        byExercise[l.exerciseId] = [];
      }
      byExercise[l.exerciseId]!.add(l);
    }
    // Сортируем подходы внутри упражнения по set_number — на бэке порядок
    // не гарантирован.
    for (final list in byExercise.values) {
      list.sort((a, b) => a.setNumber.compareTo(b.setNumber));
    }

    final dur = w.finishedAt?.difference(w.performedAt).inMinutes;

    return SafeArea(
      child: ListView(
        padding: const EdgeInsets.all(AppSpacing.lg),
        children: [
          _Header(
            performedAt: w.performedAt,
            durationMin: dur,
            status: w.status,
            setsCount: w.logs.length,
          ),
          const SizedBox(height: AppSpacing.lg),
          if (w.notes != null && w.notes!.trim().isNotEmpty) ...[
            _SectionLabel(text: 'Заметки'),
            const SizedBox(height: AppSpacing.sm),
            Container(
              padding: const EdgeInsets.all(AppSpacing.md),
              decoration: BoxDecoration(
                color: theme.colorScheme.surfaceContainerHigh,
                borderRadius: BorderRadius.circular(AppRadius.md),
                border: Border.all(color: theme.colorScheme.outline),
              ),
              child: Text(w.notes!),
            ),
            const SizedBox(height: AppSpacing.lg),
          ],
          _SectionLabel(text: 'Упражнения'),
          const SizedBox(height: AppSpacing.sm),
          if (order.isEmpty)
            Container(
              padding: const EdgeInsets.all(AppSpacing.lg),
              alignment: Alignment.center,
              decoration: BoxDecoration(
                color: theme.colorScheme.surfaceContainerHigh,
                borderRadius: BorderRadius.circular(AppRadius.md),
                border: Border.all(color: theme.colorScheme.outline),
              ),
              child: Text(
                'Подходов не было',
                style: TextStyle(color: theme.colorScheme.onSurfaceVariant),
              ),
            )
          else
            for (final exId in order) ...[
              _ExerciseBlock(
                exercise: _exerciseCache[exId],
                logs: byExercise[exId]!,
              ),
              const SizedBox(height: AppSpacing.md),
            ],
        ],
      ),
    );
  }
}

class _Header extends StatelessWidget {
  const _Header({
    required this.performedAt,
    required this.durationMin,
    required this.status,
    required this.setsCount,
  });

  final DateTime performedAt;
  final int? durationMin;
  final String status;
  final int setsCount;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final parts = <String>[
      '$setsCount подходов',
      if (durationMin != null) '$durationMin мин',
    ];
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
          Text(
            _formatDate(performedAt),
            style: theme.textTheme.titleMedium,
          ),
          const SizedBox(height: 2),
          Text(
            parts.join(' · '),
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
          if (status == 'cancelled' || status == 'in_progress') ...[
            const SizedBox(height: AppSpacing.sm),
            Container(
              padding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.sm,
                vertical: 2,
              ),
              decoration: BoxDecoration(
                color: (status == 'cancelled'
                        ? theme.colorScheme.error
                        : theme.colorScheme.primary)
                    .withValues(alpha: 0.16),
                borderRadius: BorderRadius.circular(AppRadius.sm),
              ),
              child: Text(
                status == 'cancelled' ? 'отменена' : 'идёт',
                style: theme.textTheme.labelSmall?.copyWith(
                  color: status == 'cancelled'
                      ? theme.colorScheme.error
                      : theme.colorScheme.primary,
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  static String _formatDate(DateTime utc) {
    final local = utc.toLocal();
    const months = [
      'янв', 'фев', 'мар', 'апр', 'мая', 'июн',
      'июл', 'авг', 'сен', 'окт', 'ноя', 'дек',
    ];
    final hh = local.hour.toString().padLeft(2, '0');
    final mm = local.minute.toString().padLeft(2, '0');
    return '${local.day} ${months[local.month - 1]} ${local.year} · $hh:$mm';
  }
}

class _ExerciseBlock extends StatelessWidget {
  const _ExerciseBlock({required this.exercise, required this.logs});

  final ExerciseSummaryDto? exercise;
  final List<ExerciseLogDto> logs;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final title = exercise?.displayName ?? 'Упражнение';
    return Container(
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHigh,
        borderRadius: BorderRadius.circular(AppRadius.lg),
        border: Border.all(color: theme.colorScheme.outline),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(
              AppSpacing.md,
              AppSpacing.md,
              AppSpacing.md,
              AppSpacing.sm,
            ),
            child: Text(title, style: theme.textTheme.titleMedium),
          ),
          Divider(
            height: 1,
            color: theme.colorScheme.outline.withValues(alpha: 0.4),
          ),
          for (var i = 0; i < logs.length; i++) ...[
            _SetRow(log: logs[i]),
            if (i != logs.length - 1)
              Divider(
                height: 1,
                color: theme.colorScheme.outline.withValues(alpha: 0.2),
              ),
          ],
        ],
      ),
    );
  }
}

class _SetRow extends StatelessWidget {
  const _SetRow({required this.log});
  final ExerciseLogDto log;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final weight = log.weightKg == log.weightKg.roundToDouble()
        ? log.weightKg.toInt().toString()
        : log.weightKg.toStringAsFixed(1);
    return Padding(
      padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.md,
        vertical: AppSpacing.sm,
      ),
      child: Row(
        children: [
          SizedBox(
            width: 28,
            child: Text(
              '#${log.setNumber}',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ),
          const SizedBox(width: AppSpacing.sm),
          Expanded(
            child: Text(
              '${log.reps} × $weight кг',
              style: theme.textTheme.bodyMedium,
            ),
          ),
          if (log.rpe != null)
            Text(
              'Сложность ${log.rpe}',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
        ],
      ),
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
        letterSpacing: 1.2,
      ),
    );
  }
}
