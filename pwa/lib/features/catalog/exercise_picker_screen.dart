import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../app/theme/app_spacing.dart';
import '../../data/api/catalog_api.dart';
import '../../data/api/failure.dart';

/// Экран выбора упражнения. Открывается из активной тренировки.
/// Возвращает [ExerciseSummaryDto] через `Navigator.pop(context, ex)`.
class ExercisePickerScreen extends ConsumerStatefulWidget {
  const ExercisePickerScreen({super.key});

  @override
  ConsumerState<ExercisePickerScreen> createState() => _ExercisePickerScreenState();
}

class _ExercisePickerScreenState extends ConsumerState<ExercisePickerScreen> {
  final _searchCtrl = TextEditingController();
  String? _muscleGroup; // null = "Все"

  static const _groups = <(String label, String? value)>[
    ('Все', null),
    ('Грудь', 'chest'),
    ('Спина', 'back'),
    ('Ноги', 'quads'),
    ('Плечи', 'shoulders'),
    ('Бицепс', 'biceps'),
    ('Трицепс', 'triceps'),
    ('Кор', 'abs'),
    ('Кардио', 'cardio'),
  ];

  @override
  void dispose() {
    _searchCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Выбрать упражнение'),
        leading: IconButton(
          onPressed: () => Navigator.of(context).pop(),
          icon: const Icon(Icons.arrow_back),
        ),
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(
              AppSpacing.lg,
              AppSpacing.sm,
              AppSpacing.lg,
              AppSpacing.sm,
            ),
            child: TextField(
              controller: _searchCtrl,
              onChanged: (_) => setState(() {}),
              decoration: const InputDecoration(
                hintText: 'Поиск упражнений…',
                prefixIcon: Icon(Icons.search),
              ),
            ),
          ),
          SizedBox(
            height: 44,
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: AppSpacing.lg),
              itemCount: _groups.length,
              separatorBuilder: (_, __) => const SizedBox(width: AppSpacing.sm),
              itemBuilder: (context, i) {
                final (label, value) = _groups[i];
                final selected = _muscleGroup == value;
                return ChoiceChip(
                  label: Text(label),
                  selected: selected,
                  onSelected: (_) => setState(() => _muscleGroup = value),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(AppRadius.pill),
                    side: BorderSide(color: theme.colorScheme.outline),
                  ),
                  labelStyle: theme.textTheme.bodyMedium?.copyWith(
                    color: selected
                        ? theme.colorScheme.onPrimary
                        : theme.colorScheme.onSurface,
                  ),
                  selectedColor: theme.colorScheme.primary,
                  backgroundColor: theme.colorScheme.surfaceContainerHigh,
                );
              },
            ),
          ),
          const SizedBox(height: AppSpacing.sm),
          Expanded(
            child: _ExerciseList(
              query: _searchCtrl.text.trim(),
              muscleGroup: _muscleGroup,
            ),
          ),
        ],
      ),
    );
  }
}

class _ExerciseList extends ConsumerWidget {
  const _ExerciseList({required this.query, required this.muscleGroup});

  final String query;
  final String? muscleGroup;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final api = ref.watch(catalogApiProvider);
    final future = api.list(
      query: query.length >= 2 ? query : null,
      muscleGroup: muscleGroup,
      limit: 50,
    );
    return FutureBuilder<ExerciseListResult>(
      future: future,
      builder: (context, snap) {
        if (snap.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }
        if (snap.hasError) {
          final err = snap.error;
          final msg = err is AppFailure ? err.message : 'Ошибка загрузки';
          return Center(child: Text(msg));
        }
        final items = snap.data!.items;
        if (items.isEmpty) {
          return const Center(child: Text('Ничего не нашлось'));
        }
        return ListView.separated(
          padding: const EdgeInsets.fromLTRB(
            AppSpacing.lg,
            AppSpacing.sm,
            AppSpacing.lg,
            AppSpacing.xxl,
          ),
          itemCount: items.length,
          separatorBuilder: (_, __) => const SizedBox(height: AppSpacing.sm),
          itemBuilder: (context, i) => _ExerciseTile(item: items[i]),
        );
      },
    );
  }
}

class _ExerciseTile extends StatelessWidget {
  const _ExerciseTile({required this.item});
  final ExerciseSummaryDto item;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final equipmentLabel =
        item.equipment.isEmpty ? '' : ' · ${_equipmentRu(item.equipment.first)}';
    return Material(
      color: theme.colorScheme.surfaceContainerHigh,
      borderRadius: BorderRadius.circular(AppRadius.lg),
      child: InkWell(
        onTap: () => Navigator.of(context).pop(item),
        borderRadius: BorderRadius.circular(AppRadius.lg),
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
                child: Icon(
                  Icons.fitness_center,
                  color: theme.colorScheme.primary,
                  size: 22,
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
                      '${_muscleRu(item.primaryMuscleGroup)}$equipmentLabel',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ],
                ),
              ),
              Icon(Icons.chevron_right, color: theme.colorScheme.onSurfaceVariant),
            ],
          ),
        ),
      ),
    );
  }
}

String _muscleRu(String key) => switch (key) {
      'chest' => 'Грудь',
      'back' => 'Спина',
      'quads' => 'Ноги',
      'shoulders' => 'Плечи',
      'biceps' => 'Бицепс',
      'triceps' => 'Трицепс',
      'lats' => 'Широчайшие',
      'abs' => 'Кор',
      'cardio' => 'Кардио',
      _ => key,
    };

String _equipmentRu(String key) => switch (key) {
      'barbell' => 'штанга',
      'dumbbell' => 'гантели',
      'bench' => 'скамья',
      'cable' => 'блок',
      'pullup_bar' => 'турник',
      'bodyweight' => 'без оборудования',
      'treadmill' => 'дорожка',
      _ => key,
    };
