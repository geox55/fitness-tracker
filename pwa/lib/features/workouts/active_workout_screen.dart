import 'dart:async';

import 'package:flutter/material.dart';
import '../../app/branding/portal_app_bar.dart';
import '../../app/branding/portal_scaffold.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/theme/app_spacing.dart';
import '../../data/api/analytics_api.dart';
import '../../data/api/catalog_api.dart';
import '../../data/api/failure.dart';
import '../../data/api/workouts_api.dart';
import '../catalog/exercise_picker_screen.dart';

class ActiveWorkoutScreen extends ConsumerStatefulWidget {
  const ActiveWorkoutScreen({required this.workoutId, super.key});
  final String workoutId;

  @override
  ConsumerState<ActiveWorkoutScreen> createState() => _ActiveWorkoutScreenState();
}

class _ActiveWorkoutScreenState extends ConsumerState<ActiveWorkoutScreen> {
  WorkoutDto? _workout;
  // exerciseId → ExerciseSummary (для отображения названия)
  final Map<String, ExerciseSummaryDto> _exerciseCache = {};
  // exerciseId упражнений, у которых сейчас скрыты подходы. Не сохраняется
  // между перезагрузками страницы — это чисто UI-стейт «куда сейчас смотрю».
  final Set<String> _collapsedIds = <String>{};
  Timer? _ticker;
  Duration _elapsed = Duration.zero;
  bool _busy = false;
  String? _formError;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _ticker?.cancel();
    super.dispose();
  }

  Future<void> _load() async {
    try {
      final api = ref.read(workoutsApiProvider);
      final w = await api.get(widget.workoutId);
      // подгружаем словарь упражнений, которые встречаются в логах
      await _ensureExerciseNames(w.logs.map((e) => e.exerciseId).toSet());
      if (!mounted) return;
      // Возвращаемся к незакрытой сессии: оставляем развёрнутым только
      // последнее по порядку упражнение, остальные сворачиваем — обычно
      // нужно дозалогировать именно последнее.
      final initialOrder = _orderOf(w);
      setState(() {
        _workout = w;
        _elapsed = DateTime.now().toUtc().difference(w.performedAt);
        _collapsedIds
          ..clear()
          ..addAll(
            initialOrder.length > 1
                ? initialOrder.sublist(0, initialOrder.length - 1)
                : const <String>[],
          );
      });
      _startTicker();
    } on AppFailure catch (f) {
      if (!mounted) return;
      setState(() => _formError = f.message);
    }
  }

  void _startTicker() {
    _ticker?.cancel();
    _ticker = Timer.periodic(const Duration(seconds: 1), (_) {
      if (!mounted || _workout == null) return;
      setState(() {
        _elapsed = DateTime.now().toUtc().difference(_workout!.performedAt);
      });
    });
  }

  Future<void> _ensureExerciseNames(Set<String> ids) async {
    final missing = ids.where((id) => !_exerciseCache.containsKey(id));
    if (missing.isEmpty) return;
    // Простое решение для маленького каталога: загрузим всё списком и найдём.
    final api = ref.read(catalogApiProvider);
    final all = await api.list(limit: 100);
    for (final e in all.items) {
      _exerciseCache[e.id] = e;
    }
  }

  Future<void> _addExercise() async {
    final picked = await Navigator.of(context).push<ExerciseSummaryDto>(
      MaterialPageRoute(builder: (_) => const ExercisePickerScreen()),
    );
    if (picked == null || _workout == null) return;
    setState(() => _exerciseCache[picked.id] = picked);
    await _logSet(picked.id, weight: 20, reps: 8);
    // Авто-схлопывание: после успешного добавления нового упражнения
    // скрываем подходы у всех остальных. Если _logSet провалился — _workout
    // не успел обновиться, и picked.id просто не появится в order.
    if (!mounted || _workout == null) return;
    setState(() {
      _collapsedIds
        ..clear()
        ..addAll(_orderOf(_workout!).where((id) => id != picked.id));
    });
  }

  void _toggleCollapsed(String exerciseId) {
    setState(() {
      if (!_collapsedIds.remove(exerciseId)) _collapsedIds.add(exerciseId);
    });
  }

  /// Список упражнений в порядке появления в логах. Используется и для рендера,
  /// и для решения, что свернуть после add/load.
  /// spec 016 §7: разбивает плоский список exercise-id'ов на группы.
  /// Упражнения с одинаковым ненулевым supersetGroupId всегда попадают
  /// в ОДНУ группу — даже если между ними в order стоят посторонние
  /// одиночные упражнения. Позиция группы определяется первым её
  /// членом в order; одиночки сохраняют свою позицию.
  static List<List<String>> _groupedOrder(
    List<String> order,
    Map<String, List<ExerciseLogDto>> byExercise,
  ) {
    final groups = <List<String>>[];
    final groupIndexByGid = <String, int>{};
    for (final exId in order) {
      final logs = byExercise[exId];
      final gid = (logs != null && logs.isNotEmpty)
          ? logs.first.supersetGroupId
          : null;
      if (gid == null) {
        groups.add([exId]);
      } else if (groupIndexByGid.containsKey(gid)) {
        groups[groupIndexByGid[gid]!].add(exId);
      } else {
        groupIndexByGid[gid] = groups.length;
        groups.add([exId]);
      }
    }
    return groups;
  }

  /// Порядок упражнений в UI — по самому раннему loggedAt каждого
  /// упражнения. Сервер не гарантирует сортировку logs, поэтому
  /// явно сортируем здесь. Это даёт стабильный порядок: первое
  /// добавленное упражнение остаётся первым в списке, новые
  /// добавляются в конец.
  static List<String> _orderOf(WorkoutDto w) {
    final firstLoggedAt = <String, DateTime>{};
    for (final log in w.logs) {
      final existing = firstLoggedAt[log.exerciseId];
      if (existing == null || log.loggedAt.isBefore(existing)) {
        firstLoggedAt[log.exerciseId] = log.loggedAt;
      }
    }
    final order = firstLoggedAt.keys.toList()
      ..sort((a, b) => firstLoggedAt[a]!.compareTo(firstLoggedAt[b]!));
    return order;
  }

  Future<void> _logSet(
    String exerciseId, {
    required double weight,
    required int reps,
  }) async {
    if (_workout == null) return;
    setState(() {
      _busy = true;
      _formError = null;
    });
    try {
      final api = ref.read(workoutsApiProvider);
      final logs = _workout!.logs.where((l) => l.exerciseId == exerciseId);
      final next = logs.isEmpty
          ? 1
          : logs.map((l) => l.setNumber).reduce((a, b) => a > b ? a : b) + 1;
      await api.logSet(
        widget.workoutId,
        exerciseId: exerciseId,
        setNumber: next,
        reps: reps,
        weightKg: weight,
      );
      final fresh = await api.get(widget.workoutId);
      if (!mounted) return;
      setState(() => _workout = fresh);
    } on AppFailure catch (f) {
      if (!mounted) return;
      setState(() => _formError = f.message);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _deleteLog(String logId) async {
    if (_workout == null) return;
    try {
      final api = ref.read(workoutsApiProvider);
      await api.deleteLog(widget.workoutId, logId);
      final fresh = await api.get(widget.workoutId);
      if (!mounted) return;
      setState(() => _workout = fresh);
    } on AppFailure catch (f) {
      if (!mounted) return;
      setState(() => _formError = f.message);
    }
  }

  Future<void> _editSet(ExerciseLogDto log) async {
    final result = await showDialog<({double weight, int reps})>(
      context: context,
      builder: (_) => _SetEditorDialog(initial: log),
    );
    if (result == null) return;
    // Простой путь: удалить старый и создать новый с тем же set_number.
    try {
      final api = ref.read(workoutsApiProvider);
      await api.deleteLog(widget.workoutId, log.id);
      await api.logSet(
        widget.workoutId,
        exerciseId: log.exerciseId,
        setNumber: log.setNumber,
        reps: result.reps,
        weightKg: result.weight,
      );
      final fresh = await api.get(widget.workoutId);
      if (!mounted) return;
      setState(() => _workout = fresh);
    } on AppFailure catch (f) {
      if (!mounted) return;
      setState(() => _formError = f.message);
    }
  }

  /// spec 016 §UX: рендерит группы упражнений без drop-zones — действие
  /// «Добавить в суперсет» теперь в контекстном меню «⋮» каждого блока
  /// (паттерн Hevy / Strong: самый распространённый workout-tracker UX).
  List<Widget> _buildBlocksWithDropZones({
    required List<String> order,
    required Map<String, List<ExerciseLogDto>> byExercise,
  }) {
    final groups = _groupedOrder(order, byExercise);
    final widgets = <Widget>[];
    for (final group in groups) {
      widgets.add(
        Padding(
          padding: const EdgeInsets.only(bottom: AppSpacing.md),
          child: group.length >= 2
              ? _SupersetBlock(
                  exerciseIds: group,
                  cache: _exerciseCache,
                  byExercise: byExercise,
                  collapsedIds: _collapsedIds,
                  onToggleCollapsed: _toggleCollapsed,
                  onAddSet: (exId) {
                    final last = byExercise[exId]!.last;
                    _logSet(exId, weight: last.weightKg, reps: last.reps);
                  },
                  onDelete: _deleteLog,
                  onEdit: _editSet,
                  onOpenSupersetMenu: (exId) =>
                      _openExerciseMenu(exId, order),
                )
              : _ExerciseBlock(
                  exercise: _exerciseCache[group.first],
                  exerciseId: group.first,
                  logs: byExercise[group.first]!,
                  collapsed: _collapsedIds.contains(group.first),
                  onToggleCollapsed: () => _toggleCollapsed(group.first),
                  onAddSet: () {
                    final last = byExercise[group.first]!.last;
                    _logSet(
                      group.first,
                      weight: last.weightKg,
                      reps: last.reps,
                    );
                  },
                  onDelete: _deleteLog,
                  onEdit: _editSet,
                  onLongPress: () =>
                      _openExerciseMenu(group.first, order),
                ),
        ),
      );
    }
    return widgets;
  }

  /// spec 016 §UX (best-practice Hevy/Strong): контекстное меню «⋮»
  /// упражнения. Содержит «Добавить в суперсет» / «Разъединить».
  Future<void> _openExerciseMenu(String exId, List<String> order) async {
    if (_workout == null) return;
    final logsThis = _workout!.logs.where((l) => l.exerciseId == exId);
    if (logsThis.isEmpty) return;
    final groupId = logsThis.first.supersetGroupId;

    final action = await showModalBottomSheet<String>(
      context: context,
      builder: (ctx) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (groupId != null)
              ListTile(
                leading: const Icon(Icons.link_off),
                title: const Text('Убрать из суперсета'),
                onTap: () => Navigator.of(ctx).pop('ungroup'),
              )
            else
              ListTile(
                leading: const Icon(Icons.link),
                title: const Text('Добавить в суперсет'),
                onTap: () => Navigator.of(ctx).pop('add_to_superset'),
              ),
          ],
        ),
      ),
    );
    if (action == null) return;

    if (action == 'ungroup' && groupId != null) {
      await _ungroupCurrentSuperset(groupId);
    } else if (action == 'add_to_superset') {
      await _showAddToSupersetPicker(exId, order);
    }
  }

  /// Открывает полный picker упражнений из каталога. Выбранное:
  /// - если уже в тренировке → сразу группируем с exId;
  /// - если ещё нет → добавляем default-подходом (как _addExercise),
  ///   затем группируем.
  /// Это покрывает оба сценария: «суперсет с уже добавленным» и
  /// «суперсет с новым упражнением из каталога» в одном flow.
  Future<void> _showAddToSupersetPicker(
    String exId,
    List<String> order,
  ) async {
    final picked = await Navigator.of(context).push<ExerciseSummaryDto>(
      MaterialPageRoute(builder: (_) => const ExercisePickerScreen()),
    );
    if (picked == null) return;

    // Если упражнение ещё не в тренировке — добавим его.
    final alreadyInWorkout = order.contains(picked.id);
    if (!alreadyInWorkout) {
      setState(() => _exerciseCache[picked.id] = picked);
      // _logSet создаст первый подход и обновит _workout — нужно для
      // последующего merge'а, чтобы у обоих упражнений были логи в БД.
      await _logSet(picked.id, weight: 20, reps: 8);
    }
    if (!mounted) return;
    await _mergeGroups([exId, picked.id]);
    if (!mounted) return;
    // spec 016: поддержка трисетов и больше — после успешного merge'а
    // даём пользователю быстрый способ добавить ещё одно упражнение
    // в ту же группу. Тапнул «Ещё» — снова открывается picker.
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          'Добавлено в суперсет: «${picked.displayName}»',
        ),
        action: SnackBarAction(
          label: 'Ещё',
          onPressed: () {
            if (_workout == null) return;
            _showAddToSupersetPicker(exId, _orderOf(_workout!));
          },
        ),
        duration: const Duration(seconds: 6),
      ),
    );
  }

  Future<void> _ungroupCurrentSuperset(String groupId) async {
    try {
      final api = ref.read(workoutsApiProvider);
      await api.ungroupSuperset(workoutId: widget.workoutId, groupId: groupId);
      final fresh = await api.get(widget.workoutId);
      if (!mounted) return;
      setState(() => _workout = fresh);
    } on AppFailure catch (f) {
      if (!mounted) return;
      setState(() => _formError = f.message);
    }
  }

  /// spec 016: слить логи списка упражнений в одну группу. Бэкенд сам
  /// переиспользует существующий group_id, если один уже есть.
  Future<void> _mergeGroups(List<String> exerciseIds) async {
    try {
      final api = ref.read(workoutsApiProvider);
      await api.groupSuperset(
        workoutId: widget.workoutId,
        exerciseIds: exerciseIds,
      );
      final fresh = await api.get(widget.workoutId);
      if (!mounted) return;
      setState(() => _workout = fresh);
    } on AppFailure catch (f) {
      if (!mounted) return;
      setState(() => _formError = f.message);
    }
  }

  Future<void> _finish() async {
    if (_workout == null) return;
    setState(() => _busy = true);
    try {
      final api = ref.read(workoutsApiProvider);
      await api.finish(widget.workoutId);
      // Подтянуть Главную и историю заново.
      ref.invalidate(overviewProvider);
      ref.invalidate(activeWorkoutProvider);
      ref.invalidate(workoutHistoryProvider);
      if (!mounted) return;
      context.go('/training');
    } on AppFailure catch (f) {
      if (!mounted) return;
      setState(() => _formError = f.message);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _cancel() async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Отменить тренировку?'),
        content: const Text(
          'Все зафиксированные подходы будут сохранены, но тренировка не пойдёт в статистику.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Нет'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Да, отменить'),
          ),
        ],
      ),
    );
    if (ok != true || _workout == null) return;
    try {
      await ref.read(workoutsApiProvider).cancel(widget.workoutId);
      ref.invalidate(activeWorkoutProvider);
      ref.invalidate(workoutHistoryProvider);
      if (!mounted) return;
      context.go('/training');
    } on AppFailure catch (f) {
      if (!mounted) return;
      setState(() => _formError = f.message);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final w = _workout;

    if (w == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    // Группировка логов по упражнению с сохранением порядка появления.
    final order = _orderOf(w);
    final byExercise = <String, List<ExerciseLogDto>>{};
    for (final log in w.logs) {
      (byExercise[log.exerciseId] ??= []).add(log);
    }

    return PortalScaffold(
      appBar: PortalAppBar(
        leading: IconButton(
          tooltip: 'К списку тренировок',
          onPressed: () => context.go('/training'),
          icon: const Icon(Icons.arrow_back),
        ),
        actions: [
          IconButton(
            tooltip: 'Отменить тренировку',
            onPressed: _cancel,
            icon: const Icon(Icons.close),
          ),
        ],
        title: Column(
          children: [
            Text(
              'АКТИВНАЯ СЕССИЯ',
              style: theme.textTheme.labelSmall?.copyWith(
                color: theme.colorScheme.primary,
                letterSpacing: 1.6,
              ),
            ),
            Text(
              _formatDuration(_elapsed),
              style: theme.textTheme.headlineMedium?.copyWith(height: 1),
            ),
          ],
        ),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(
            AppSpacing.lg,
            AppSpacing.lg,
            AppSpacing.lg,
            AppSpacing.xxxl * 3,
          ),
          children: [
            // spec 016: упражнения, объединённые в суперсет, рендерим
            // одной общей карточкой; одиночные — обычным блоком.
            // Между группами — drop-zone «– Объединить –»: тап сливает
            // соседние группы в одну (поддерживает трисеты и больше через
            // последовательное объединение).
            ..._buildBlocksWithDropZones(
              order: order,
              byExercise: byExercise,
            ),
            OutlinedButton.icon(
              onPressed: _busy ? null : _addExercise,
              icon: const Icon(Icons.add),
              label: const Text('Добавить упражнение'),
            ),
            if (_formError != null) ...[
              const SizedBox(height: AppSpacing.md),
              Text(
                _formError!,
                style: TextStyle(color: theme.colorScheme.error),
                textAlign: TextAlign.center,
              ),
            ],
            const SizedBox(height: AppSpacing.lg),
            ElevatedButton.icon(
              onPressed: (_busy || w.logs.isEmpty) ? null : _finish,
              icon: const Icon(Icons.check_circle_outline),
              label: const Text('Завершить тренировку'),
            ),
          ],
        ),
      ),
    );
  }

  static String _formatDuration(Duration d) {
    final h = d.inHours.toString().padLeft(2, '0');
    final m = d.inMinutes.remainder(60).toString().padLeft(2, '0');
    final s = d.inSeconds.remainder(60).toString().padLeft(2, '0');
    return '$h:$m:$s';
  }
}

class _ExerciseBlock extends StatelessWidget {
  const _ExerciseBlock({
    required this.exercise,
    required this.exerciseId,
    required this.logs,
    required this.collapsed,
    required this.onToggleCollapsed,
    required this.onAddSet,
    required this.onDelete,
    required this.onEdit,
    required this.onLongPress,
    this.embedded = false,
  });

  final ExerciseSummaryDto? exercise;
  final String exerciseId;
  final List<ExerciseLogDto> logs;
  final bool collapsed;
  final VoidCallback onToggleCollapsed;
  final VoidCallback onAddSet;
  final void Function(String logId) onDelete;
  final void Function(ExerciseLogDto log) onEdit;
  // spec 016: long-press на блоке — открывает меню «Объединить со
  // следующим / разъединить» (используется как secondary вход; primary —
  // drop-zone между блоками, см. _SupersetDropZone).
  final VoidCallback onLongPress;
  // spec 016: true когда блок встроен в общий _SupersetBlock —
  // тогда свою рамку и бейдж не рисуем, чтобы не было «карточка в карточке».
  final bool embedded;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final title = exercise?.displayName ?? 'Упражнение';
    final subtitle = exercise == null
        ? ''
        : exercise!.equipment.isEmpty
            ? muscleRu(exercise!.primaryMuscleGroup).toUpperCase()
            : '${muscleRu(exercise!.primaryMuscleGroup).toUpperCase()} · ${equipmentRu(exercise!.equipment.first).toUpperCase()}';
    // spec 016: блок в составе суперсета — обводка blue, бейдж сверху.
    // Если embedded=true (блок внутри _SupersetBlock) — без своей рамки
    // и бейджа, рисуем только контент.
    final inSuperset = logs.isNotEmpty && logs.first.supersetGroupId != null;
    final borderColor = inSuperset
        ? theme.colorScheme.primary.withValues(alpha: 0.55)
        : theme.colorScheme.outline;
    final inner = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
          if (inSuperset && !embedded)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.md,
                vertical: 4,
              ),
              color: theme.colorScheme.primary.withValues(alpha: 0.12),
              child: Row(
                children: [
                  Icon(Icons.link, size: 14, color: theme.colorScheme.primary),
                  const SizedBox(width: 6),
                  Text(
                    'СУПЕРСЕТ',
                    style: theme.textTheme.labelSmall?.copyWith(
                      color: theme.colorScheme.primary,
                      letterSpacing: 1.4,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ),
          // Хедер кликабельный целиком — это удобнее, чем целиться в шеврон.
          InkWell(
            onTap: onToggleCollapsed,
            onLongPress: onLongPress,
            child: Padding(
              padding: const EdgeInsets.all(AppSpacing.md),
              child: Row(
                children: [
                  Container(
                    width: 44,
                    height: 44,
                    decoration: BoxDecoration(
                      color: theme.colorScheme.primary.withValues(alpha: 0.16),
                      borderRadius: BorderRadius.circular(AppRadius.md),
                    ),
                    child: Icon(Icons.fitness_center,
                        color: theme.colorScheme.primary, size: 22),
                  ),
                  const SizedBox(width: AppSpacing.md),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(title, style: theme.textTheme.titleMedium),
                        if (subtitle.isNotEmpty)
                          Text(
                            subtitle,
                            style: theme.textTheme.labelSmall?.copyWith(
                              color: theme.colorScheme.onSurfaceVariant,
                              letterSpacing: 1.2,
                            ),
                          ),
                      ],
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: AppSpacing.sm,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: theme.colorScheme.primary.withValues(alpha: 0.16),
                      borderRadius: BorderRadius.circular(AppRadius.sm),
                    ),
                    child: Text(
                      '${logs.length} подх.',
                      style: theme.textTheme.labelSmall?.copyWith(
                        color: theme.colorScheme.primary,
                      ),
                    ),
                  ),
                  const SizedBox(width: AppSpacing.xs),
                  // spec 016 §UX (Hevy/Strong-стиль): контекстное меню «⋮»
                  // с действиями «Добавить в суперсет» / «Убрать из».
                  // На embedded-блоке (внутри SupersetBlock) меню тоже
                  // доступно — позволяет убрать конкретное упражнение.
                  IconButton(
                    tooltip: 'Меню упражнения',
                    icon: Icon(
                      Icons.more_vert,
                      size: 20,
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                    visualDensity: VisualDensity.compact,
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(
                      minWidth: 32,
                      minHeight: 32,
                    ),
                    onPressed: onLongPress,
                  ),
                  // Шеврон поворачивается на 180° при разворачивании —
                  // получаем «free» индикацию состояния, без лишних иконок.
                  AnimatedRotation(
                    turns: collapsed ? 0 : 0.5,
                    duration: const Duration(milliseconds: 180),
                    child: Icon(
                      Icons.expand_more,
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ],
              ),
            ),
          ),
          // Тело сворачиваемого блока. AnimatedSize даёт плавный коллапс
          // высоты; ClipRect — чтобы внутренние Row'ы не моргали поверх границы
          // во время анимации.
          AnimatedSize(
            duration: const Duration(milliseconds: 180),
            curve: Curves.easeInOut,
            alignment: Alignment.topCenter,
            child: collapsed
                ? const SizedBox(width: double.infinity)
                : Padding(
                    padding: const EdgeInsets.fromLTRB(
                      AppSpacing.md,
                      0,
                      AppSpacing.md,
                      AppSpacing.md,
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        for (var i = 0; i < logs.length; i++)
                          _SetRow(log: logs[i], displayIndex: i + 1, onDelete: onDelete, onEdit: onEdit),
                        const SizedBox(height: AppSpacing.sm),
                        Align(
                          alignment: Alignment.centerLeft,
                          child: TextButton.icon(
                            onPressed: onAddSet,
                            icon: const Icon(Icons.add, size: 18),
                            label: const Text('Добавить подход'),
                          ),
                        ),
                      ],
                    ),
                  ),
          ),
        ],
      );

    if (embedded) {
      return inner;
    }
    return Container(
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHigh,
        borderRadius: BorderRadius.circular(AppRadius.lg),
        border: Border.all(
          color: borderColor,
          width: inSuperset ? 1.5 : 1.0,
        ),
      ),
      clipBehavior: Clip.antiAlias,
      child: inner,
    );
  }
}

/// spec 016: одна общая карточка для двух (и более) упражнений в суперсете.
/// Внутри — _ExerciseBlock'и с embedded=true (без своих рамок), разделённые
/// тонкой линией. Сверху — общий бейдж 🔗 СУПЕРСЕТ.
class _SupersetBlock extends StatelessWidget {
  const _SupersetBlock({
    required this.exerciseIds,
    required this.cache,
    required this.byExercise,
    required this.collapsedIds,
    required this.onToggleCollapsed,
    required this.onAddSet,
    required this.onDelete,
    required this.onEdit,
    required this.onOpenSupersetMenu,
  });

  final List<String> exerciseIds;
  final Map<String, ExerciseSummaryDto> cache;
  final Map<String, List<ExerciseLogDto>> byExercise;
  final Set<String> collapsedIds;
  final void Function(String exId) onToggleCollapsed;
  final void Function(String exId) onAddSet;
  final void Function(String logId) onDelete;
  final void Function(ExerciseLogDto log) onEdit;
  final void Function(String exId) onOpenSupersetMenu;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHigh,
        borderRadius: BorderRadius.circular(AppRadius.lg),
        border: Border.all(
          color: theme.colorScheme.primary.withValues(alpha: 0.55),
          width: 1.5,
        ),
      ),
      clipBehavior: Clip.antiAlias,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(
              horizontal: AppSpacing.md,
              vertical: 6,
            ),
            color: theme.colorScheme.primary.withValues(alpha: 0.12),
            child: Row(
              children: [
                Icon(Icons.link, size: 14, color: theme.colorScheme.primary),
                const SizedBox(width: 6),
                Text(
                  'СУПЕРСЕТ',
                  style: theme.textTheme.labelSmall?.copyWith(
                    color: theme.colorScheme.primary,
                    letterSpacing: 1.4,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const Spacer(),
                IconButton(
                  tooltip: 'Разъединить',
                  icon: Icon(
                    Icons.link_off,
                    size: 18,
                    color: theme.colorScheme.primary,
                  ),
                  visualDensity: VisualDensity.compact,
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints(),
                  onPressed: () => onOpenSupersetMenu(exerciseIds.first),
                ),
              ],
            ),
          ),
          for (var i = 0; i < exerciseIds.length; i++) ...[
            if (i > 0)
              Divider(
                height: 1,
                thickness: 1,
                color: theme.colorScheme.primary.withValues(alpha: 0.25),
              ),
            _ExerciseBlock(
              exercise: cache[exerciseIds[i]],
              exerciseId: exerciseIds[i],
              logs: byExercise[exerciseIds[i]]!,
              collapsed: collapsedIds.contains(exerciseIds[i]),
              onToggleCollapsed: () => onToggleCollapsed(exerciseIds[i]),
              onAddSet: () => onAddSet(exerciseIds[i]),
              onDelete: onDelete,
              onEdit: onEdit,
              onLongPress: () => onOpenSupersetMenu(exerciseIds[i]),
              embedded: true,
            ),
          ],
        ],
      ),
    );
  }
}

class _SetRow extends StatelessWidget {
  const _SetRow({
    required this.log,
    required this.displayIndex,
    required this.onDelete,
    required this.onEdit,
  });

  final ExerciseLogDto log;
  final int displayIndex;
  final void Function(String logId) onDelete;
  final void Function(ExerciseLogDto log) onEdit;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return InkWell(
      onTap: () => onEdit(log),
      borderRadius: BorderRadius.circular(AppRadius.md),
      child: Padding(
        padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.sm,
          vertical: AppSpacing.sm,
        ),
        child: Row(
          children: [
            SizedBox(
              width: 24,
              child: Text(
                '$displayIndex',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ),
            const SizedBox(width: AppSpacing.sm),
            Expanded(
              child: Text(
                '${_kg(log.weightKg)} кг × ${log.reps}',
                style: theme.textTheme.titleMedium,
              ),
            ),
            IconButton(
              tooltip: 'Удалить подход',
              onPressed: () => onDelete(log.id),
              icon: Icon(
                Icons.delete_outline,
                color: theme.colorScheme.onSurfaceVariant,
                size: 20,
              ),
            ),
          ],
        ),
      ),
    );
  }

  static String _kg(double v) {
    if (v == v.roundToDouble()) return v.toStringAsFixed(0);
    return v.toStringAsFixed(1);
  }
}

class _SetEditorDialog extends StatefulWidget {
  const _SetEditorDialog({required this.initial});
  final ExerciseLogDto initial;

  @override
  State<_SetEditorDialog> createState() => _SetEditorDialogState();
}

class _SetEditorDialogState extends State<_SetEditorDialog> {
  late final TextEditingController _weightCtrl;
  late final TextEditingController _repsCtrl;

  @override
  void initState() {
    super.initState();
    _weightCtrl = TextEditingController(
      text: widget.initial.weightKg.toString(),
    );
    _repsCtrl = TextEditingController(text: widget.initial.reps.toString());
  }

  @override
  void dispose() {
    _weightCtrl.dispose();
    _repsCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text('Подход ${widget.initial.setNumber}'),
      content: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _weightCtrl,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'Вес, кг'),
            ),
          ),
          const SizedBox(width: AppSpacing.md),
          Expanded(
            child: TextField(
              controller: _repsCtrl,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'Повторы'),
            ),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Отмена'),
        ),
        ElevatedButton(
          onPressed: () {
            final w = double.tryParse(_weightCtrl.text.replaceAll(',', '.'));
            final r = int.tryParse(_repsCtrl.text);
            if (w == null || r == null || r < 1) return;
            Navigator.pop(context, (weight: w, reps: r));
          },
          child: const Text('Сохранить'),
        ),
      ],
    );
  }
}
