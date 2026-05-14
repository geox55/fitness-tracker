import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../app/theme/app_spacing.dart';
import '../../data/api/catalog_api.dart';
import '../../data/api/failure.dart';
import 'exercise_picker_screen.dart' show muscleRu, equipmentRu;

/// Экран создания/редактирования пользовательского упражнения. Если
/// `initial == null` — create-режим (POST /exercises). Иначе — edit-режим
/// (PATCH /exercises/{id}).
///
/// Поля минимальные: название (RU + EN), основная группа мышц, регион тела,
/// оборудование (chip-multi-select). instructions/calories пока не редактируем —
/// модель их поддерживает, добавим, когда будет конкретный сценарий.
class ExerciseEditScreen extends ConsumerStatefulWidget {
  const ExerciseEditScreen({this.initial, super.key});

  final ExerciseSummaryDto? initial;

  @override
  ConsumerState<ExerciseEditScreen> createState() => _ExerciseEditScreenState();
}

class _ExerciseEditScreenState extends ConsumerState<ExerciseEditScreen> {
  late final TextEditingController _nameRuCtrl;
  late final TextEditingController _nameEnCtrl;
  String? _muscleGroup;
  String? _bodyRegion;
  final Set<String> _equipment = <String>{};
  bool _busy = false;
  String? _error;

  static const _muscleOptions = <String>[
    'chest',
    'back',
    'quads',
    'shoulders',
    'biceps',
    'triceps',
    'lats',
    'abs',
    'cardio',
  ];
  static const _bodyRegionOptions = <(String, String)>[
    ('upper', 'Верх тела'),
    ('lower', 'Низ тела'),
    ('core', 'Кор'),
    ('full', 'Всё тело'),
  ];
  static const _equipmentOptions = <String>[
    'barbell',
    'dumbbell',
    'bench',
    'cable',
    'pullup_bar',
    'bodyweight',
    'treadmill',
  ];

  bool get _isEdit => widget.initial != null;

  @override
  void initState() {
    super.initState();
    final i = widget.initial;
    _nameRuCtrl = TextEditingController(text: i?.nameRu ?? '');
    _nameEnCtrl = TextEditingController(text: i?.name ?? '');
    _muscleGroup = i?.primaryMuscleGroup;
    _bodyRegion = i?.bodyRegion;
    _equipment.addAll(i?.equipment ?? const <String>[]);
  }

  @override
  void dispose() {
    _nameRuCtrl.dispose();
    _nameEnCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: Text(_isEdit ? 'Редактировать' : 'Новое упражнение'),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(AppSpacing.lg),
          children: [
            TextField(
              controller: _nameRuCtrl,
              decoration: const InputDecoration(
                labelText: 'Название (по-русски)',
                hintText: 'Например: Жим штанги лёжа узким хватом',
              ),
              textCapitalization: TextCapitalization.sentences,
            ),
            const SizedBox(height: AppSpacing.md),
            TextField(
              controller: _nameEnCtrl,
              decoration: const InputDecoration(
                labelText: 'Название (English, optional)',
                hintText: 'Close-Grip Bench Press',
              ),
            ),
            const SizedBox(height: AppSpacing.lg),
            _SectionLabel(text: 'Группа мышц'),
            const SizedBox(height: AppSpacing.sm),
            Wrap(
              spacing: AppSpacing.sm,
              runSpacing: AppSpacing.sm,
              children: [
                for (final m in _muscleOptions)
                  ChoiceChip(
                    label: Text(muscleRu(m)),
                    selected: _muscleGroup == m,
                    onSelected: (_) => setState(() => _muscleGroup = m),
                  ),
              ],
            ),
            const SizedBox(height: AppSpacing.lg),
            _SectionLabel(text: 'Регион тела'),
            const SizedBox(height: AppSpacing.sm),
            Wrap(
              spacing: AppSpacing.sm,
              runSpacing: AppSpacing.sm,
              children: [
                for (final (key, label) in _bodyRegionOptions)
                  ChoiceChip(
                    label: Text(label),
                    selected: _bodyRegion == key,
                    onSelected: (_) => setState(() => _bodyRegion = key),
                  ),
              ],
            ),
            const SizedBox(height: AppSpacing.lg),
            _SectionLabel(text: 'Оборудование'),
            const SizedBox(height: AppSpacing.sm),
            Wrap(
              spacing: AppSpacing.sm,
              runSpacing: AppSpacing.sm,
              children: [
                for (final e in _equipmentOptions)
                  FilterChip(
                    label: Text(equipmentRu(e)),
                    selected: _equipment.contains(e),
                    onSelected: (sel) => setState(() {
                      if (sel) {
                        _equipment.add(e);
                      } else {
                        _equipment.remove(e);
                      }
                    }),
                  ),
              ],
            ),
            if (_error != null) ...[
              const SizedBox(height: AppSpacing.lg),
              Text(
                _error!,
                style: TextStyle(color: theme.colorScheme.error),
              ),
            ],
            const SizedBox(height: AppSpacing.xxl),
            ElevatedButton.icon(
              onPressed: _busy ? null : _submit,
              icon: const Icon(Icons.check),
              label: Text(_isEdit ? 'Сохранить' : 'Создать'),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _submit() async {
    final nameRu = _nameRuCtrl.text.trim();
    final nameEn = _nameEnCtrl.text.trim();
    // Хотя бы одно из имён должно быть; primary_muscle_group/body_region на
    // бэке обязательные.
    if (nameRu.isEmpty && nameEn.isEmpty) {
      setState(() => _error = 'Укажите название упражнения');
      return;
    }
    if (_muscleGroup == null) {
      setState(() => _error = 'Выберите основную группу мышц');
      return;
    }
    if (_bodyRegion == null) {
      setState(() => _error = 'Выберите регион тела');
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });

    // EN-имя у бэка required (`exercise_name`); если пользователь не ввёл —
    // используем RU. Так пользовательский кейс «знаю только русское»
    // не упирается в валидацию.
    final effectiveEn = nameEn.isNotEmpty ? nameEn : nameRu;
    final effectiveRu = nameRu.isNotEmpty ? nameRu : null;

    final fields = ExerciseEditFields(
      name: effectiveEn,
      nameRu: effectiveRu,
      primaryMuscleGroup: _muscleGroup,
      bodyRegion: _bodyRegion,
      equipment: _equipment.toList(),
    );
    try {
      final api = ref.read(catalogApiProvider);
      final result = _isEdit
          ? await api.updateOwned(widget.initial!.id, fields)
          : await api.createOwned(fields);
      if (!mounted) return;
      Navigator.of(context).pop(result);
    } on AppFailure catch (f) {
      if (!mounted) return;
      setState(() => _error = f.message);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
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
