import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_slidable/flutter_slidable.dart';
import 'package:go_router/go_router.dart';

import '../../app/theme/app_spacing.dart';
import '../../data/api/failure.dart';
import '../../data/api/workouts_api.dart';

/// Свайп-обёртка с действиями «Изменить» / «Удалить» для карточки тренировки.
/// Используется в трёх местах (Главная, Тренировка, Статистика), поэтому
/// вынесена отдельно.
///
/// `onDeleted` — вызывается ПОСЛЕ успешного DELETE и должен инвалидировать
/// провайдеры, релевантные для экрана-вызывающего (например, на Главной —
/// overview, на статистике — workoutHistory). Edit-экран сам инвалидирует
/// `workoutHistoryProvider`/`activeWorkoutProvider`, поэтому отдельного
/// колбэка для edit не нужно.
class WorkoutActionsSlidable extends ConsumerWidget {
  const WorkoutActionsSlidable({
    super.key,
    required this.workoutId,
    required this.onDeleted,
    required this.borderRadius,
    required this.child,
  });

  final String workoutId;
  final VoidCallback onDeleted;
  final double borderRadius;
  final Widget child;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    return Slidable(
      key: ValueKey('workout-actions-$workoutId'),
      endActionPane: ActionPane(
        motion: const BehindMotion(),
        extentRatio: 0.56,
        children: [
          SlidableAction(
            onPressed: (_) => context.push('/training/edit/$workoutId'),
            backgroundColor: theme.colorScheme.primary,
            foregroundColor: theme.colorScheme.onPrimary,
            icon: Icons.edit_outlined,
            label: 'Изменить',
            borderRadius: BorderRadius.horizontal(
              left: Radius.circular(borderRadius),
            ),
          ),
          SlidableAction(
            onPressed: (_) => _delete(context, ref),
            backgroundColor: theme.colorScheme.error,
            foregroundColor: theme.colorScheme.onError,
            icon: Icons.delete_outline,
            label: 'Удалить',
            borderRadius: BorderRadius.horizontal(
              right: Radius.circular(borderRadius),
            ),
          ),
        ],
      ),
      child: child,
    );
  }

  Future<void> _delete(BuildContext context, WidgetRef ref) async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Удалить тренировку?'),
        content: const Text(
          'Действие нельзя отменить. Все зафиксированные подходы тоже '
          'удалятся.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(false),
            child: const Text('Отмена'),
          ),
          FilledButton.tonal(
            style: FilledButton.styleFrom(
              backgroundColor:
                  Theme.of(ctx).colorScheme.error.withValues(alpha: 0.18),
              foregroundColor: Theme.of(ctx).colorScheme.error,
            ),
            onPressed: () => Navigator.of(ctx).pop(true),
            child: const Text('Удалить'),
          ),
        ],
      ),
    );
    if (ok != true || !context.mounted) return;
    try {
      await ref.read(workoutsApiProvider).delete(workoutId);
      onDeleted();
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Тренировка удалена')),
      );
    } on AppFailure catch (f) {
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(f.message)),
      );
    }
  }
}

/// Реэкспорт SlidableAutoCloseBehavior — список из карточек должен оборачиваться
/// в него, иначе свайпы открываются одновременно. Через этот реэкспорт callers'ы
/// не тянут лишний импорт flutter_slidable.
typedef WorkoutActionsAutoClose = SlidableAutoCloseBehavior;

/// Стандартный отступ под swipe-actions карточек.
const double kWorkoutCardActionsRadius = AppRadius.lg;
