// Экран экспорта PDF-отчёта (spec 010 §3 Scenario 5, REQ-10..12).
//
// Поток:
//   1. `_FormState`  — пользователь выбирает диапазон и секции,
//      жмёт «Создать PDF» → POST /analytics/export-pdf → 202 + job_id.
//   2. `_PendingState` — поллим GET /analytics/export-pdf/{job_id}
//      каждые 1.2 с, пока `isTerminal`. UI показывает прогресс/спиннер.
//   3. `_ReadyState`  — отдаём кнопку «Скачать»; signed URL TTL 1 час
//      (NFR-03), при истечении просим job ещё раз (бэкенд каждый GET
//      пересоздаёт URL).
//   4. `_FailedState` — текст ошибки + кнопка retry (новый job).
//
// Открываем PDF в новой вкладке через `package:web` — на PWA это
// нативно работает без url_launcher и без extra-permission.

import 'dart:async';

import 'package:flutter/material.dart';
import '../../app/branding/portal_app_bar.dart';
import '../../app/branding/portal_scaffold.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../app/theme/app_colors.dart';
import '../../app/theme/app_spacing.dart';
import '../../data/api/analytics_api.dart';
import '../../data/api/failure.dart';

/// Жёсткий список секций — должен соответствовать `ExportSection` в
/// `src/app/domains/analytics/export_models.py`. Если бэкенд расширит
/// набор — обновить здесь.
const _allSections = <_SectionMeta>[
  _SectionMeta(id: 'profile', title: 'Профиль'),
  _SectionMeta(id: 'inbody', title: 'Графики тела'),
  _SectionMeta(id: 'workouts', title: 'Тренировки'),
  _SectionMeta(id: 'goal', title: 'Прогресс по цели'),
];

class _SectionMeta {
  const _SectionMeta({required this.id, required this.title});
  final String id;
  final String title;
}

enum _RangePreset {
  m1,
  m3,
  m6,
  y1,
  all;

  String get label => switch (this) {
        _RangePreset.m1 => '1 месяц',
        _RangePreset.m3 => '3 месяца',
        _RangePreset.m6 => '6 месяцев',
        _RangePreset.y1 => '1 год',
        _RangePreset.all => 'Вся история',
      };

  /// Возвращает `from` относительно `now`. `null` означает «без нижней
  /// границы» — бэкенд тогда отдаст всю историю.
  DateTime? from(DateTime now) {
    return switch (this) {
      _RangePreset.m1 => DateTime(now.year, now.month - 1, now.day),
      _RangePreset.m3 => DateTime(now.year, now.month - 3, now.day),
      _RangePreset.m6 => DateTime(now.year, now.month - 6, now.day),
      _RangePreset.y1 => DateTime(now.year - 1, now.month, now.day),
      _RangePreset.all => null,
    };
  }
}

sealed class _ExportState {
  const _ExportState();
}

class _FormState extends _ExportState {
  const _FormState();
}

class _PendingState extends _ExportState {
  const _PendingState({required this.jobId, required this.status});
  final String jobId;
  final String status; // pending | running
}

class _ReadyState extends _ExportState {
  const _ReadyState({required this.status});
  final ExportPdfStatusDto status;
}

class _FailedState extends _ExportState {
  const _FailedState({required this.message});
  final String message;
}

class ExportPdfScreen extends ConsumerStatefulWidget {
  const ExportPdfScreen({super.key});

  @override
  ConsumerState<ExportPdfScreen> createState() => _ExportPdfScreenState();
}

class _ExportPdfScreenState extends ConsumerState<ExportPdfScreen> {
  _ExportState _state = const _FormState();
  _RangePreset _range = _RangePreset.m3;
  final Set<String> _selectedSections = {
    for (final s in _allSections) s.id,
  };
  Timer? _pollTimer;

  @override
  void dispose() {
    _pollTimer?.cancel();
    super.dispose();
  }

  Future<void> _start() async {
    if (_selectedSections.isEmpty) return;
    final now = DateTime.now();
    final req = ExportPdfRequestDto(
      from: _range.from(now),
      to: _range == _RangePreset.all ? null : now,
      sections: _selectedSections.toList()..sort(),
    );
    setState(
      () => _state = const _PendingState(jobId: '', status: 'pending'),
    );
    try {
      final accepted = await ref.read(analyticsApiProvider).startExportPdf(req);
      setState(
        () => _state = _PendingState(
          jobId: accepted.jobId,
          status: accepted.status,
        ),
      );
      _schedulePoll(accepted.jobId);
    } on AppFailure catch (f) {
      setState(() => _state = _FailedState(message: f.message));
    }
  }

  void _schedulePoll(String jobId) {
    _pollTimer?.cancel();
    _pollTimer = Timer(const Duration(milliseconds: 1200), () async {
      if (!mounted) return;
      try {
        final status = await ref.read(analyticsApiProvider).getExportPdf(jobId);
        if (!mounted) return;
        if (status.status == 'ready') {
          setState(() => _state = _ReadyState(status: status));
        } else if (status.status == 'failed') {
          setState(
            () => _state = _FailedState(
              message: status.errorMessage ?? 'Не удалось создать отчёт',
            ),
          );
        } else {
          setState(
            () => _state = _PendingState(
              jobId: jobId,
              status: status.status,
            ),
          );
          _schedulePoll(jobId);
        }
      } on AppFailure catch (f) {
        if (!mounted) return;
        setState(() => _state = _FailedState(message: f.message));
      }
    });
  }

  void _reset() {
    _pollTimer?.cancel();
    setState(() => _state = const _FormState());
  }

  Future<void> _refreshUrl(String jobId) async {
    // Signed URL мог истечь (TTL 1 час). Бэкенд каждый GET пересоздаёт
    // его — поэтому просто запрашиваем статус ещё раз.
    try {
      final status = await ref.read(analyticsApiProvider).getExportPdf(jobId);
      if (!mounted) return;
      setState(() => _state = _ReadyState(status: status));
    } on AppFailure catch (f) {
      if (!mounted) return;
      setState(() => _state = _FailedState(message: f.message));
    }
  }

  Future<void> _openUrl(String url) async {
    // Кроссплатформенно: на web — новая вкладка, на Android — внешний браузер.
    await launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication);
  }

  @override
  Widget build(BuildContext context) {
    return PortalScaffold(
      appBar: PortalAppBar(
        title: const Text('Экспорт PDF'),
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => context.pop(),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(AppSpacing.lg),
          child: switch (_state) {
            _FormState() => _FormView(
                range: _range,
                onRangeChanged: (r) => setState(() => _range = r),
                selectedSections: _selectedSections,
                onToggleSection: (id, on) {
                  setState(() {
                    if (on) {
                      _selectedSections.add(id);
                    } else {
                      _selectedSections.remove(id);
                    }
                  });
                },
                onStart: _selectedSections.isEmpty ? null : _start,
              ),
            _PendingState(:final status) => _PendingView(status: status),
            _ReadyState(:final status) => _ReadyView(
                status: status,
                onDownload: () => _openUrl(status.url!),
                onRefresh: () => _refreshUrl(status.jobId),
                onAgain: _reset,
              ),
            _FailedState(:final message) => _FailedView(
                message: message,
                onRetry: _reset,
              ),
          },
        ),
      ),
    );
  }
}

// --- Form -----------------------------------------------------------------

class _FormView extends StatelessWidget {
  const _FormView({
    required this.range,
    required this.onRangeChanged,
    required this.selectedSections,
    required this.onToggleSection,
    required this.onStart,
  });

  final _RangePreset range;
  final ValueChanged<_RangePreset> onRangeChanged;
  final Set<String> selectedSections;
  final void Function(String id, bool on) onToggleSection;
  final VoidCallback? onStart;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return ListView(
      children: [
        Text('Диапазон', style: theme.textTheme.titleMedium),
        const SizedBox(height: AppSpacing.sm),
        Wrap(
          spacing: AppSpacing.sm,
          runSpacing: AppSpacing.sm,
          children: [
            for (final r in _RangePreset.values)
              ChoiceChip(
                label: Text(r.label),
                selected: range == r,
                onSelected: (_) => onRangeChanged(r),
              ),
          ],
        ),
        const SizedBox(height: AppSpacing.xl),
        Text('Что включить', style: theme.textTheme.titleMedium),
        const SizedBox(height: AppSpacing.sm),
        Container(
          decoration: BoxDecoration(
            color: theme.colorScheme.surfaceContainerHigh,
            borderRadius: BorderRadius.circular(AppRadius.lg),
            border: Border.all(color: theme.colorScheme.outline),
          ),
          child: Column(
            children: [
              for (var i = 0; i < _allSections.length; i++) ...[
                CheckboxListTile(
                  value: selectedSections.contains(_allSections[i].id),
                  onChanged: (v) =>
                      onToggleSection(_allSections[i].id, v ?? false),
                  title: Text(_allSections[i].title),
                  controlAffinity: ListTileControlAffinity.leading,
                  dense: true,
                ),
                if (i != _allSections.length - 1)
                  Divider(
                    height: 1,
                    color: theme.colorScheme.outline.withValues(alpha: 0.4),
                  ),
              ],
            ],
          ),
        ),
        if (selectedSections.isEmpty) ...[
          const SizedBox(height: AppSpacing.sm),
          Text(
            'Выберите хотя бы одну секцию',
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.error,
            ),
          ),
        ],
        const SizedBox(height: AppSpacing.xl),
        ElevatedButton.icon(
          icon: const Icon(Icons.picture_as_pdf_outlined),
          label: const Text('Создать PDF'),
          onPressed: onStart,
        ),
        const SizedBox(height: AppSpacing.md),
        Text(
          'Файл будет доступен по ссылке в течение часа после готовности.',
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
      ],
    );
  }
}

// --- Pending --------------------------------------------------------------

class _PendingView extends StatelessWidget {
  const _PendingView({required this.status});
  final String status;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final label = switch (status) {
      'pending' => 'Поставлен в очередь',
      'running' => 'Создаём отчёт',
      _ => 'Обрабатываем',
    };
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const CircularProgressIndicator(),
          const SizedBox(height: AppSpacing.lg),
          Text(label, style: theme.textTheme.titleMedium),
          const SizedBox(height: AppSpacing.sm),
          Text(
            'Это занимает обычно несколько секунд.',
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
        ],
      ),
    );
  }
}

// --- Ready ----------------------------------------------------------------

class _ReadyView extends StatelessWidget {
  const _ReadyView({
    required this.status,
    required this.onDownload,
    required this.onRefresh,
    required this.onAgain,
  });
  final ExportPdfStatusDto status;
  final VoidCallback onDownload;
  final VoidCallback onRefresh;
  final VoidCallback onAgain;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final expiresAt = status.expiresAt;
    final expired =
        expiresAt != null && DateTime.now().isAfter(expiresAt);
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
          Text('Отчёт готов', style: theme.textTheme.titleLarge),
          const SizedBox(height: AppSpacing.sm),
          if (status.periodFrom != null && status.periodTo != null)
            Text(
              '${_fmtDate(status.periodFrom!)} — ${_fmtDate(status.periodTo!)}',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            )
          else
            Text(
              'Вся история',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          const SizedBox(height: AppSpacing.xl),
          if (expired)
            // Ссылка истекла — REQ-10/NFR-03; кнопка «Обновить»
            // дёргает GET /export-pdf/{job_id} — он пересоздаст URL.
            Column(
              children: [
                Text(
                  'Ссылка истекла',
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: theme.colorScheme.error,
                  ),
                ),
                const SizedBox(height: AppSpacing.md),
                ElevatedButton.icon(
                  icon: const Icon(Icons.refresh),
                  label: const Text('Обновить ссылку'),
                  onPressed: onRefresh,
                ),
              ],
            )
          else
            ElevatedButton.icon(
              icon: const Icon(Icons.download),
              label: const Text('Скачать'),
              onPressed: onDownload,
            ),
          const SizedBox(height: AppSpacing.md),
          OutlinedButton(
            onPressed: onAgain,
            child: const Text('Создать ещё один'),
          ),
        ],
      ),
    );
  }
}

// --- Failed ---------------------------------------------------------------

class _FailedView extends StatelessWidget {
  const _FailedView({required this.message, required this.onRetry});
  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.error_outline, size: 56, color: theme.colorScheme.error),
          const SizedBox(height: AppSpacing.md),
          Text(
            'Не удалось создать отчёт',
            style: theme.textTheme.titleMedium,
          ),
          const SizedBox(height: AppSpacing.sm),
          Text(message, textAlign: TextAlign.center),
          const SizedBox(height: AppSpacing.lg),
          ElevatedButton(onPressed: onRetry, child: const Text('Повторить')),
        ],
      ),
    );
  }
}

String _fmtDate(DateTime d) => DateFormat('d MMM yyyy', 'ru').format(d);
