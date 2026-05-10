import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/theme/app_colors.dart';
import '../../app/theme/app_spacing.dart';
import '../../data/api/analytics_api.dart';
import '../../data/api/failure.dart';
import '../../data/api/inbody_pdf_api.dart';

/// Экран загрузки и подтверждения PDF InBody (spec 013).
///
/// Состояния:
/// - `idle`: пусто, кнопка «Выбрать PDF».
/// - `uploading`: спиннер.
/// - `preview(job)`: показываем распознанные поля для подтверждения.
/// - `error(failure)`: ошибка с возможностью повторить.
/// - `success(measurement)`: создан замер.
class InBodyPdfUploadScreen extends ConsumerStatefulWidget {
  const InBodyPdfUploadScreen({super.key});

  @override
  ConsumerState<InBodyPdfUploadScreen> createState() =>
      _InBodyPdfUploadScreenState();
}

sealed class _ScreenState {
  const _ScreenState();
}

class _Idle extends _ScreenState {
  const _Idle();
}

class _Uploading extends _ScreenState {
  const _Uploading();
}

class _Preview extends _ScreenState {
  const _Preview(this.job);
  final PdfJobDto job;
}

class _ErrorState extends _ScreenState {
  const _ErrorState(this.failure);
  final AppFailure failure;
}

class _Success extends _ScreenState {
  const _Success(this.measurement);
  final CreatedMeasurementDto measurement;
}

class _InBodyPdfUploadScreenState
    extends ConsumerState<InBodyPdfUploadScreen> {
  _ScreenState _state = const _Idle();
  // Локальные правки полей пользователем перед confirm. Если значение совпадает
  // с extracted — не пересылаем (бэкенд сам прочитает из job.extracted).
  final Map<String, TextEditingController> _controllers = {};
  DateTime _measuredAt = DateTime.now();

  @override
  void dispose() {
    for (final c in _controllers.values) {
      c.dispose();
    }
    super.dispose();
  }

  Future<void> _pickAndUpload() async {
    final picked = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf'],
      withData: true, // нужны bytes, не path — это web
    );
    if (picked == null || picked.files.isEmpty) return;
    final file = picked.files.first;
    final bytes = file.bytes;
    if (bytes == null) {
      setState(() {
        _state = const _ErrorState(
          UnexpectedFailure('Не удалось прочитать файл'),
        );
      });
      return;
    }
    setState(() => _state = const _Uploading());
    try {
      final job = await ref
          .read(inBodyPdfApiProvider)
          .upload(bytes: bytes, filename: file.name);
      setState(() {
        _state = _Preview(job);
        _initControllersFromJob(job);
        _measuredAt = DateTime.now();
      });
    } on AppFailure catch (f) {
      setState(() => _state = _ErrorState(f));
    }
  }

  void _initControllersFromJob(PdfJobDto job) {
    for (final c in _controllers.values) {
      c.dispose();
    }
    _controllers.clear();
    for (final entry in job.extracted.entries) {
      _controllers[entry.key] = TextEditingController(
        text: entry.value.toString(),
      );
    }
    // Также подкладываем missing-поля как пустые, чтобы пользователь мог их
    // ввести вручную, не покидая экран.
    for (final missing in job.missingFields) {
      _controllers.putIfAbsent(missing, () => TextEditingController());
    }
  }

  Future<void> _confirm(PdfJobDto job) async {
    // Собираем overrides: что отличается от job.extracted И не пусто.
    final overrides = <String, dynamic>{};
    for (final entry in _controllers.entries) {
      final raw = entry.value.text.trim();
      if (raw.isEmpty) continue;
      final original = job.extracted[entry.key]?.toString();
      if (raw == original) continue;
      // Парсим как число для числовых полей; sex оставляем строкой.
      final num? asNum = num.tryParse(raw.replaceAll(',', '.'));
      overrides[entry.key] = asNum ?? raw;
    }
    setState(() => _state = const _Uploading());
    try {
      final m = await ref.read(inBodyPdfApiProvider).confirm(
            jobId: job.id,
            measuredAt: _measuredAt,
            overrides: overrides,
          );
      // Новый замер влияет на overview, прогресс цели и графики «Тело» —
      // сбрасываем кеши, чтобы соответствующие экраны на следующем showe
      // увидели актуальные данные.
      ref.invalidate(overviewProvider);
      ref.invalidate(goalProgressProvider);
      // inbodySeriesProvider — family; clear() сбрасывает все instance'ы.
      ref.invalidate(inbodySeriesProvider);
      setState(() => _state = _Success(m));
    } on AppFailure catch (f) {
      setState(() => _state = _ErrorState(f));
    }
  }

  void _reset() {
    setState(() {
      _state = const _Idle();
      for (final c in _controllers.values) {
        c.dispose();
      }
      _controllers.clear();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Загрузить InBody PDF'),
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => context.pop(),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(AppSpacing.lg),
          child: switch (_state) {
            _Idle() => _IdleView(onPick: _pickAndUpload),
            _Uploading() => const Center(child: CircularProgressIndicator()),
            _Preview(:final job) => _PreviewView(
                job: job,
                controllers: _controllers,
                measuredAt: _measuredAt,
                onChangeMeasuredAt: (d) => setState(() => _measuredAt = d),
                onConfirm: () => _confirm(job),
                onCancel: _reset,
              ),
            _ErrorState(:final failure) => _ErrorView(
                failure: failure,
                onRetry: _reset,
              ),
            _Success(:final measurement) => _SuccessView(
                measurement: measurement,
                onClose: () => context.pop(),
              ),
          },
        ),
      ),
    );
  }
}

// --- Idle: «выбрать файл» --------------------------------------------------

class _IdleView extends StatelessWidget {
  const _IdleView({required this.onPick});
  final VoidCallback onPick;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 96,
            height: 96,
            decoration: BoxDecoration(
              color: theme.colorScheme.primary.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(AppRadius.xl),
            ),
            child: Icon(
              Icons.picture_as_pdf_outlined,
              size: 48,
              color: theme.colorScheme.primary,
            ),
          ),
          const SizedBox(height: AppSpacing.lg),
          Text(
            'Загрузите PDF InBody-отчёта',
            style: theme.textTheme.titleLarge,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: AppSpacing.sm),
          Text(
            'Поддерживаются модели 270/570/770/970. Размер файла до 10 MB.',
            style: theme.textTheme.bodyMedium?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: AppSpacing.xl),
          ElevatedButton.icon(
            icon: const Icon(Icons.upload_file),
            label: const Text('Выбрать PDF'),
            onPressed: onPick,
          ),
        ],
      ),
    );
  }
}

// --- Preview: распознанные поля --------------------------------------------

class _PreviewView extends StatelessWidget {
  const _PreviewView({
    required this.job,
    required this.controllers,
    required this.measuredAt,
    required this.onChangeMeasuredAt,
    required this.onConfirm,
    required this.onCancel,
  });

  final PdfJobDto job;
  final Map<String, TextEditingController> controllers;
  final DateTime measuredAt;
  final ValueChanged<DateTime> onChangeMeasuredAt;
  final VoidCallback onConfirm;
  final VoidCallback onCancel;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    if (!job.status.isConfirmable) {
      return _NotConfirmableView(job: job, onCancel: onCancel);
    }

    return ListView(
      children: [
        _StatusBadge(status: job.status, template: job.template),
        const SizedBox(height: AppSpacing.lg),
        Text(
          'Распознанные поля',
          style: theme.textTheme.titleMedium,
        ),
        const SizedBox(height: AppSpacing.sm),
        Text(
          'Проверьте значения и поправьте, если что-то не так. Пустые поля в созданном замере останутся незаполненными.',
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        const SizedBox(height: AppSpacing.lg),
        _MeasuredAtPicker(
          value: measuredAt,
          onChanged: onChangeMeasuredAt,
        ),
        const SizedBox(height: AppSpacing.lg),
        for (final f in _orderedFields)
          if (controllers.containsKey(f))
            Padding(
              padding: const EdgeInsets.only(bottom: AppSpacing.md),
              child: _FieldRow(
                fieldKey: f,
                controller: controllers[f]!,
                isMissing: job.missingFields.contains(f),
                confidence: job.confidence[f] as String?,
              ),
            ),
        const SizedBox(height: AppSpacing.xl),
        Row(
          children: [
            Expanded(
              child: OutlinedButton(
                onPressed: onCancel,
                child: const Text('Отменить'),
              ),
            ),
            const SizedBox(width: AppSpacing.md),
            Expanded(
              child: ElevatedButton.icon(
                icon: const Icon(Icons.check),
                label: const Text('Сохранить'),
                onPressed: onConfirm,
              ),
            ),
          ],
        ),
      ],
    );
  }
}

const _orderedFields = [
  'weight_kg',
  'height_cm',
  'body_fat_percent',
  'muscle_mass_kg',
  'fat_free_mass_kg',
  'body_water_percent',
  'protein_kg',
  'minerals_kg',
  'visceral_fat_level',
  'bmr_kcal',
  'bmi',
  'sex',
];

const _fieldLabels = {
  'weight_kg': 'Вес, кг',
  'height_cm': 'Рост, см',
  'body_fat_percent': 'Жир, %',
  'muscle_mass_kg': 'Мышечная масса, кг',
  'fat_free_mass_kg': 'Сухая масса, кг',
  'body_water_percent': 'Вода, %',
  'protein_kg': 'Белок, кг',
  'minerals_kg': 'Минералы, кг',
  'visceral_fat_level': 'Висцеральный жир',
  'bmr_kcal': 'BMR, ккал',
  'bmi': 'BMI',
  'sex': 'Пол (male/female)',
};

class _FieldRow extends StatelessWidget {
  const _FieldRow({
    required this.fieldKey,
    required this.controller,
    required this.isMissing,
    required this.confidence,
  });

  final String fieldKey;
  final TextEditingController controller;
  final bool isMissing;
  final String? confidence;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final label = _fieldLabels[fieldKey] ?? fieldKey;
    return TextField(
      controller: controller,
      keyboardType: fieldKey == 'sex'
          ? TextInputType.text
          : const TextInputType.numberWithOptions(decimal: true),
      decoration: InputDecoration(
        labelText: label,
        suffixIcon: isMissing
            ? Tooltip(
                message: 'Не распознано — введите вручную, если знаете',
                child: Icon(
                  Icons.error_outline,
                  color: theme.colorScheme.error,
                ),
              )
            : (confidence != null
                ? _ConfidenceBadge(confidence: confidence!)
                : null),
        border: const OutlineInputBorder(),
      ),
    );
  }
}

class _ConfidenceBadge extends StatelessWidget {
  const _ConfidenceBadge({required this.confidence});
  final String confidence;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final color = switch (confidence) {
      'high' => AppPalette.success,
      'medium' => theme.colorScheme.primary,
      _ => theme.colorScheme.onSurfaceVariant,
    };
    return Padding(
      padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.md,
        vertical: AppSpacing.xs,
      ),
      child: Container(
        padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.sm,
          vertical: 2,
        ),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.15),
          borderRadius: BorderRadius.circular(AppRadius.pill),
        ),
        child: Text(
          confidence,
          style: theme.textTheme.labelSmall?.copyWith(color: color),
        ),
      ),
    );
  }
}

class _StatusBadge extends StatelessWidget {
  const _StatusBadge({required this.status, required this.template});
  final PdfJobStatus status;
  final String? template;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final (text, color) = switch (status) {
      PdfJobStatus.ready => ('Распознано', AppPalette.success),
      PdfJobStatus.partial => ('Частично распознано', AppPalette.warning),
      PdfJobStatus.failed => ('Не распознано', theme.colorScheme.error),
      PdfJobStatus.notInbody =>
        ('Это не похоже на InBody-отчёт', theme.colorScheme.error),
      PdfJobStatus.encrypted =>
        ('Файл защищён паролем', theme.colorScheme.error),
      PdfJobStatus.scannedUnsupported =>
        ('Сканированный PDF не поддерживается', theme.colorScheme.error),
      _ => ('Обработка', theme.colorScheme.primary),
    };
    return Container(
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(AppRadius.md),
        border: Border.all(color: color.withValues(alpha: 0.4)),
      ),
      child: Row(
        children: [
          Icon(Icons.description_outlined, color: color),
          const SizedBox(width: AppSpacing.sm),
          Expanded(
            child: Text(
              template != null ? '$text · $template' : text,
              style: theme.textTheme.bodyMedium?.copyWith(color: color),
            ),
          ),
        ],
      ),
    );
  }
}

class _MeasuredAtPicker extends StatelessWidget {
  const _MeasuredAtPicker({required this.value, required this.onChanged});
  final DateTime value;
  final ValueChanged<DateTime> onChanged;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return InkWell(
      onTap: () async {
        final picked = await showDatePicker(
          context: context,
          initialDate: value,
          firstDate: DateTime(2010),
          lastDate: DateTime.now(),
        );
        if (picked != null) onChanged(picked);
      },
      child: InputDecorator(
        decoration: const InputDecoration(
          labelText: 'Дата измерения',
          border: OutlineInputBorder(),
        ),
        child: Text(
          '${value.day.toString().padLeft(2, '0')}.'
          '${value.month.toString().padLeft(2, '0')}.${value.year}',
          style: theme.textTheme.bodyLarge,
        ),
      ),
    );
  }
}

// --- not_inbody / encrypted / scanned_unsupported / failed ----------------

class _NotConfirmableView extends StatelessWidget {
  const _NotConfirmableView({required this.job, required this.onCancel});
  final PdfJobDto job;
  final VoidCallback onCancel;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final message = switch (job.status) {
      PdfJobStatus.notInbody =>
        'Это не похоже на InBody-отчёт. Загрузите PDF, выданный InBody-аппаратом.',
      PdfJobStatus.encrypted =>
        'Файл защищён паролем. Снимите защиту в просмотрщике PDF и попробуйте снова.',
      PdfJobStatus.scannedUnsupported =>
        'Сканированный PDF без текстового слоя не поддерживается. Введите данные вручную.',
      PdfJobStatus.failed =>
        'Не удалось распознать содержимое. Введите данные вручную.',
      _ => 'Обработка не завершена',
    };
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.error_outline, size: 64, color: theme.colorScheme.error),
          const SizedBox(height: AppSpacing.md),
          Text(
            message,
            style: theme.textTheme.bodyLarge,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: AppSpacing.lg),
          OutlinedButton(
            onPressed: onCancel,
            child: const Text('Выбрать другой файл'),
          ),
        ],
      ),
    );
  }
}

// --- Error / Success ------------------------------------------------------

class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.failure, required this.onRetry});
  final AppFailure failure;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.cloud_off, size: 56, color: theme.colorScheme.error),
          const SizedBox(height: AppSpacing.md),
          Text(failure.message, textAlign: TextAlign.center),
          const SizedBox(height: AppSpacing.lg),
          OutlinedButton(onPressed: onRetry, child: const Text('Повторить')),
        ],
      ),
    );
  }
}

class _SuccessView extends StatelessWidget {
  const _SuccessView({required this.measurement, required this.onClose});
  final CreatedMeasurementDto measurement;
  final VoidCallback onClose;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.check_circle_outline,
            size: 64,
            color: AppPalette.success,
          ),
          const SizedBox(height: AppSpacing.md),
          Text('Замер сохранён', style: theme.textTheme.titleLarge),
          const SizedBox(height: AppSpacing.sm),
          Text(
            'Вес ${measurement.weightKg.toStringAsFixed(1)} кг · '
            'Жир ${measurement.bodyFatPercent.toStringAsFixed(1)} %',
            style: theme.textTheme.bodyLarge,
          ),
          const SizedBox(height: AppSpacing.lg),
          ElevatedButton(onPressed: onClose, child: const Text('Готово')),
        ],
      ),
    );
  }
}
