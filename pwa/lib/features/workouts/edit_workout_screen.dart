import 'package:flutter/material.dart';
import '../../app/branding/portal_app_bar.dart';
import '../../app/branding/portal_scaffold.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/theme/app_spacing.dart';
import '../../data/api/failure.dart';
import '../../data/api/workouts_api.dart';

/// Экран редактирования тренировки — открывается свайпом из истории.
/// Меняет только notes / performed_at / finished_at; статус и origin тут не
/// трогаем (для статуса есть finish/cancel).
class EditWorkoutScreen extends ConsumerStatefulWidget {
  const EditWorkoutScreen({super.key, required this.workoutId});

  final String workoutId;

  @override
  ConsumerState<EditWorkoutScreen> createState() => _EditWorkoutScreenState();
}

class _EditWorkoutScreenState extends ConsumerState<EditWorkoutScreen> {
  final _notesCtrl = TextEditingController();
  DateTime? _performedAt;
  DateTime? _finishedAt;
  bool _loaded = false;
  bool _saving = false;
  String? _error;
  WorkoutDto? _original;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _notesCtrl.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    try {
      final w = await ref.read(workoutsApiProvider).get(widget.workoutId);
      if (!mounted) return;
      setState(() {
        _original = w;
        _notesCtrl.text = w.notes ?? '';
        _performedAt = w.performedAt.toLocal();
        _finishedAt = w.finishedAt?.toLocal();
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

  Future<DateTime?> _pickDateTime(BuildContext context, DateTime initial) async {
    final date = await showDatePicker(
      context: context,
      initialDate: initial,
      firstDate: DateTime(2020),
      lastDate: DateTime.now().add(const Duration(days: 1)),
    );
    if (date == null || !context.mounted) return null;
    final time = await showTimePicker(
      context: context,
      initialTime: TimeOfDay.fromDateTime(initial),
    );
    if (time == null) return null;
    return DateTime(date.year, date.month, date.day, time.hour, time.minute);
  }

  Future<void> _save() async {
    if (_saving || _original == null) return;
    // Минимальная клиентская валидация — на бэке такая же проверка.
    if (_finishedAt != null &&
        _performedAt != null &&
        _finishedAt!.isBefore(_performedAt!)) {
      setState(() => _error = 'Окончание не может быть раньше начала');
      return;
    }
    setState(() {
      _saving = true;
      _error = null;
    });
    try {
      final notes = _notesCtrl.text.trim();
      final original = _original!;
      await ref.read(workoutsApiProvider).patch(
            widget.workoutId,
            notes: notes.isEmpty ? null : notes,
            clearNotes: notes.isEmpty && (original.notes?.isNotEmpty ?? false),
            performedAt: _performedAt != original.performedAt.toLocal()
                ? _performedAt
                : null,
            finishedAt:
                _finishedAt != null && _finishedAt != original.finishedAt?.toLocal()
                    ? _finishedAt
                    : null,
          );
      // Освежаем оба провайдера: активная тренировка и история — оба могут
      // содержать обновлённую запись.
      ref.invalidate(activeWorkoutProvider);
      ref.invalidate(workoutHistoryProvider);
      if (!mounted) return;
      context.pop();
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Тренировка обновлена')),
      );
    } on AppFailure catch (f) {
      if (!mounted) return;
      setState(() => _error = f.message);
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return PortalScaffold(
      appBar: PortalAppBar(
        title: const Text('Редактировать'),
        actions: [
          if (_loaded && _original != null)
            TextButton(
              onPressed: _saving ? null : _save,
              child: _saving
                  ? const SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Text('Сохранить'),
            ),
        ],
      ),
      body: !_loaded
          ? const Center(child: CircularProgressIndicator())
          : _original == null
              ? Center(
                  child: Text(
                    _error ?? 'Не удалось загрузить тренировку',
                    style: TextStyle(color: theme.colorScheme.error),
                  ),
                )
              : SafeArea(
                  child: ListView(
                    padding: const EdgeInsets.all(AppSpacing.lg),
                    children: [
                      Text('Начало', style: theme.textTheme.titleSmall),
                      const SizedBox(height: AppSpacing.sm),
                      _DateTimeTile(
                        value: _performedAt,
                        onTap: () async {
                          final v = await _pickDateTime(
                              context, _performedAt ?? DateTime.now());
                          if (v != null) setState(() => _performedAt = v);
                        },
                      ),
                      const SizedBox(height: AppSpacing.lg),
                      Row(
                        children: [
                          Expanded(
                            child: Text('Окончание',
                                style: theme.textTheme.titleSmall),
                          ),
                          if (_finishedAt != null &&
                              _original!.status == 'in_progress')
                            TextButton.icon(
                              onPressed: () =>
                                  setState(() => _finishedAt = null),
                              icon: const Icon(Icons.clear, size: 16),
                              label: const Text('Сбросить'),
                            ),
                        ],
                      ),
                      const SizedBox(height: AppSpacing.sm),
                      _DateTimeTile(
                        value: _finishedAt,
                        placeholder: 'Не задано',
                        onTap: () async {
                          final v = await _pickDateTime(
                            context,
                            _finishedAt ?? _performedAt ?? DateTime.now(),
                          );
                          if (v != null) setState(() => _finishedAt = v);
                        },
                      ),
                      const SizedBox(height: AppSpacing.lg),
                      Text('Заметки', style: theme.textTheme.titleSmall),
                      const SizedBox(height: AppSpacing.sm),
                      TextField(
                        controller: _notesCtrl,
                        maxLines: 4,
                        maxLength: 500,
                        decoration: const InputDecoration(
                          hintText: 'Самочувствие, отметки по технике…',
                        ),
                      ),
                      if (_error != null) ...[
                        const SizedBox(height: AppSpacing.md),
                        Text(
                          _error!,
                          style: TextStyle(color: theme.colorScheme.error),
                        ),
                      ],
                    ],
                  ),
                ),
    );
  }
}

class _DateTimeTile extends StatelessWidget {
  const _DateTimeTile({
    required this.value,
    required this.onTap,
    this.placeholder,
  });

  final DateTime? value;
  final VoidCallback onTap;
  final String? placeholder;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(AppRadius.md),
      child: Container(
        padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.lg,
          vertical: AppSpacing.md,
        ),
        decoration: BoxDecoration(
          color: theme.colorScheme.surfaceContainerHigh,
          borderRadius: BorderRadius.circular(AppRadius.md),
          border: Border.all(color: theme.colorScheme.outline),
        ),
        child: Row(
          children: [
            Icon(Icons.event, color: theme.colorScheme.onSurfaceVariant),
            const SizedBox(width: AppSpacing.md),
            Expanded(
              child: Text(
                value == null ? (placeholder ?? '—') : _format(value!),
                style: theme.textTheme.bodyLarge?.copyWith(
                  color: value == null
                      ? theme.colorScheme.onSurfaceVariant
                      : null,
                ),
              ),
            ),
            Icon(Icons.chevron_right, color: theme.colorScheme.onSurfaceVariant),
          ],
        ),
      ),
    );
  }

  static String _format(DateTime local) {
    const months = [
      'янв', 'фев', 'мар', 'апр', 'мая', 'июн',
      'июл', 'авг', 'сен', 'окт', 'ноя', 'дек',
    ];
    final hh = local.hour.toString().padLeft(2, '0');
    final mm = local.minute.toString().padLeft(2, '0');
    return '${local.day} ${months[local.month - 1]} ${local.year} · $hh:$mm';
  }
}
