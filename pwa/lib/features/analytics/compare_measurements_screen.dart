// Экран «Сравнить замеры» (spec 010 §3 Scenario 2, REQ-04).
//
// Две точки входа: можно зайти без параметров (выберем последние два
// замера автоматически) или с `aId/bId` (deep-link с детальной страницы).
//
// Снимаем 2 запроса параллельно:
//   - measurementsListProvider — для двух селекторов;
//   - analyticsApi.inbodyCompare(a, b) — таблица дельт.
//
// Цвет стрелок зависит от цели пользователя:
//   - weight_loss: вес/жир ↓ — success, ↑ — warning;
//   - muscle_gain: вес/мышцы ↑ — success, ↓ — warning;
//   - default (без цели): нейтрально-серая стрелка.
// Для нейтральных метрик (вода, минералы) — нейтральный цвет.

import 'package:flutter/material.dart';
import '../../app/branding/portal_app_bar.dart';
import '../../app/branding/portal_scaffold.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../app/theme/app_colors.dart';
import '../../app/theme/app_spacing.dart';
import '../../data/api/analytics_api.dart';
import '../../data/api/failure.dart';
import '../../data/api/inbody_api.dart';
import '../../data/api/profile_api.dart';

class CompareMeasurementsScreen extends ConsumerStatefulWidget {
  const CompareMeasurementsScreen({super.key});

  @override
  ConsumerState<CompareMeasurementsScreen> createState() =>
      _CompareMeasurementsScreenState();
}

class _CompareMeasurementsScreenState
    extends ConsumerState<CompareMeasurementsScreen> {
  String? _aId;
  String? _bId;

  @override
  Widget build(BuildContext context) {
    final list = ref.watch(measurementsListProvider);
    return PortalScaffold(
      appBar: PortalAppBar(title: const Text('Сравнить замеры')),
      body: SafeArea(
        child: list.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (e, _) => _ErrorView(
            error: e,
            onRetry: () => ref.invalidate(measurementsListProvider),
          ),
          data: (data) {
            if (data.items.length < 2) return const _NotEnoughView();
            // По умолчанию a = предпоследний, b = последний (свежий справа).
            _aId ??= data.items.length >= 2 ? data.items[1].id : null;
            _bId ??= data.items.first.id;
            return _CompareBody(
              items: data.items,
              aId: _aId!,
              bId: _bId!,
              onChangedA: (id) => setState(() => _aId = id),
              onChangedB: (id) => setState(() => _bId = id),
            );
          },
        ),
      ),
    );
  }
}

class _NotEnoughView extends StatelessWidget {
  const _NotEnoughView();

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.xxl),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.compare_arrows,
              size: 56,
              color: theme.colorScheme.onSurfaceVariant,
            ),
            const SizedBox(height: AppSpacing.md),
            Text(
              'Нужно как минимум два замера',
              style: theme.textTheme.titleMedium,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: AppSpacing.sm),
            Text(
              'Загрузите ещё один PDF или введите замер вручную, '
              'чтобы увидеть таблицу дельт.',
              textAlign: TextAlign.center,
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: AppSpacing.lg),
            ElevatedButton.icon(
              icon: const Icon(Icons.upload_file),
              label: const Text('Загрузить InBody PDF'),
              onPressed: () => GoRouter.of(context).push('/inbody/upload-pdf'),
            ),
          ],
        ),
      ),
    );
  }
}

class _CompareBody extends ConsumerWidget {
  const _CompareBody({
    required this.items,
    required this.aId,
    required this.bId,
    required this.onChangedA,
    required this.onChangedB,
  });

  final List<MeasurementDto> items;
  final String aId;
  final String bId;
  final ValueChanged<String> onChangedA;
  final ValueChanged<String> onChangedB;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // analyticsApi.inbodyCompare(a, b) пересчитывается на каждое изменение
    // селекторов (без family-провайдера — экран короткоживущий).
    final compareFuture = ref.watch(
      _compareProvider(_ComparePair(a: aId, b: bId)),
    );
    final profileAsync = ref.watch(profileProvider);
    final goal = profileAsync.maybeWhen(
      data: (p) => p.goal,
      orElse: () => null,
    );
    return ListView(
      padding: const EdgeInsets.all(AppSpacing.lg),
      children: [
        Row(
          children: [
            Expanded(
              child: _MeasurementPicker(
                label: 'Было',
                items: items,
                selectedId: aId,
                onChanged: onChangedA,
              ),
            ),
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: AppSpacing.sm),
              child: Icon(Icons.arrow_forward),
            ),
            Expanded(
              child: _MeasurementPicker(
                label: 'Стало',
                items: items,
                selectedId: bId,
                onChanged: onChangedB,
              ),
            ),
          ],
        ),
        const SizedBox(height: AppSpacing.lg),
        if (aId == bId)
          const _SameMeasurementHint()
        else
          compareFuture.when(
            loading: () => const Padding(
              padding: EdgeInsets.symmetric(vertical: AppSpacing.xxl),
              child: Center(child: CircularProgressIndicator()),
            ),
            error: (e, _) => _ErrorView(
              error: e,
              onRetry: () => ref.invalidate(
                _compareProvider(_ComparePair(a: aId, b: bId)),
              ),
            ),
            data: (compare) => _DeltaTable(compare: compare, goal: goal),
          ),
      ],
    );
  }
}

class _SameMeasurementHint extends StatelessWidget {
  const _SameMeasurementHint();

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.all(AppSpacing.lg),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHigh,
        borderRadius: BorderRadius.circular(AppRadius.lg),
        border: Border.all(color: theme.colorScheme.outline),
      ),
      child: Row(
        children: [
          Icon(Icons.info_outline, color: theme.colorScheme.onSurfaceVariant),
          const SizedBox(width: AppSpacing.sm),
          Expanded(
            child: Text(
              'Выберите два разных замера',
              style: theme.textTheme.bodyMedium,
            ),
          ),
        ],
      ),
    );
  }
}

class _MeasurementPicker extends StatelessWidget {
  const _MeasurementPicker({
    required this.label,
    required this.items,
    required this.selectedId,
    required this.onChanged,
  });

  final String label;
  final List<MeasurementDto> items;
  final String selectedId;
  final ValueChanged<String> onChanged;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label.toUpperCase(),
          style: theme.textTheme.labelSmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
            letterSpacing: 1.2,
          ),
        ),
        const SizedBox(height: AppSpacing.xs),
        DropdownButtonFormField<String>(
          isExpanded: true,
          initialValue: selectedId,
          decoration: const InputDecoration(
            border: OutlineInputBorder(),
            isDense: true,
          ),
          items: items
              .map(
                (m) => DropdownMenuItem(
                  value: m.id,
                  child: Text(_fmtPickerLabel(m), overflow: TextOverflow.ellipsis),
                ),
              )
              .toList(),
          onChanged: (v) {
            if (v != null) onChanged(v);
          },
        ),
      ],
    );
  }
}

class _DeltaTable extends StatelessWidget {
  const _DeltaTable({required this.compare, required this.goal});
  final CompareResponseDto compare;
  final String? goal;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.md,
        vertical: AppSpacing.sm,
      ),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHigh,
        borderRadius: BorderRadius.circular(AppRadius.lg),
        border: Border.all(color: theme.colorScheme.outline),
      ),
      child: Column(
        children: [
          _DeltaHeader(
            a: compare.a.measuredAt,
            b: compare.b.measuredAt,
          ),
          Divider(
            color: theme.colorScheme.outline.withValues(alpha: 0.4),
            height: 1,
          ),
          for (var i = 0; i < compare.deltas.length; i++) ...[
            _DeltaRow(delta: compare.deltas[i], goal: goal),
            if (i != compare.deltas.length - 1)
              Divider(
                color: theme.colorScheme.outline.withValues(alpha: 0.18),
                height: 1,
              ),
          ],
        ],
      ),
    );
  }
}

class _DeltaHeader extends StatelessWidget {
  const _DeltaHeader({required this.a, required this.b});
  final DateTime a;
  final DateTime b;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final labelStyle = theme.textTheme.labelSmall?.copyWith(
      color: theme.colorScheme.onSurfaceVariant,
      letterSpacing: 1.1,
    );
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: AppSpacing.sm),
      child: Row(
        children: [
          Expanded(flex: 4, child: Text('МЕТРИКА', style: labelStyle)),
          Expanded(
            flex: 3,
            child: Text(
              _fmtDateShort(a),
              style: labelStyle,
              textAlign: TextAlign.right,
            ),
          ),
          Expanded(
            flex: 3,
            child: Text(
              _fmtDateShort(b),
              style: labelStyle,
              textAlign: TextAlign.right,
            ),
          ),
          Expanded(
            flex: 4,
            child: Text(
              'ДЕЛЬТА',
              style: labelStyle,
              textAlign: TextAlign.right,
            ),
          ),
        ],
      ),
    );
  }
}

class _DeltaRow extends StatelessWidget {
  const _DeltaRow({required this.delta, required this.goal});
  final FieldDeltaDto delta;
  final String? goal;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final meta = _fieldMeta[delta.field];
    if (meta == null) return const SizedBox.shrink();
    final color = _deltaColor(theme, delta, goal, meta);
    final arrow = _deltaArrow(delta);
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: AppSpacing.sm),
      child: Row(
        children: [
          Expanded(flex: 4, child: Text(meta.label)),
          Expanded(
            flex: 3,
            child: Text(
              _fmtValue(delta.valueA, meta),
              textAlign: TextAlign.right,
              style: theme.textTheme.bodyMedium,
            ),
          ),
          Expanded(
            flex: 3,
            child: Text(
              _fmtValue(delta.valueB, meta),
              textAlign: TextAlign.right,
              style: theme.textTheme.bodyMedium,
            ),
          ),
          Expanded(
            flex: 4,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                if (arrow != null) Icon(arrow, color: color, size: 16),
                const SizedBox(width: 4),
                Flexible(
                  child: Text(
                    _fmtDelta(delta, meta),
                    style: theme.textTheme.bodyMedium?.copyWith(color: color),
                    textAlign: TextAlign.right,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.error, required this.onRetry});
  final Object error;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final message =
        error is AppFailure ? (error as AppFailure).message : 'Не удалось загрузить';
    return Padding(
      padding: const EdgeInsets.all(AppSpacing.xl),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.cloud_off, color: theme.colorScheme.error, size: 40),
          const SizedBox(height: AppSpacing.sm),
          Text(message, textAlign: TextAlign.center),
          const SizedBox(height: AppSpacing.md),
          OutlinedButton(onPressed: onRetry, child: const Text('Повторить')),
        ],
      ),
    );
  }
}

// --- Domain meta ----------------------------------------------------------

/// Метаданные одной метрики для compare-таблицы. `betterDown=true` —
/// для целей weight_loss «вниз» = хорошо. Если null — метрика
/// «нейтральная», стрелка серая.
class _FieldMeta {
  const _FieldMeta({
    required this.label,
    required this.unit,
    required this.decimals,
    this.weightLossBetterDown,
    this.muscleGainBetterUp,
  });
  final String label;
  final String unit;
  final int decimals;
  final bool? weightLossBetterDown;
  final bool? muscleGainBetterUp;
}

const _fieldMeta = <String, _FieldMeta>{
  'weight_kg': _FieldMeta(
    label: 'Вес',
    unit: 'кг',
    decimals: 1,
    weightLossBetterDown: true,
    muscleGainBetterUp: true,
  ),
  'body_fat_percent': _FieldMeta(
    label: 'Жир',
    unit: '%',
    decimals: 1,
    weightLossBetterDown: true,
    muscleGainBetterUp: false,
  ),
  'muscle_mass_kg': _FieldMeta(
    label: 'Мышечная масса',
    unit: 'кг',
    decimals: 1,
    weightLossBetterDown: false,
    muscleGainBetterUp: true,
  ),
  'body_water_percent': _FieldMeta(label: 'Вода', unit: '%', decimals: 1),
  'protein_kg': _FieldMeta(label: 'Белок', unit: 'кг', decimals: 1),
  'minerals_kg': _FieldMeta(label: 'Минералы', unit: 'кг', decimals: 2),
  'visceral_fat_level': _FieldMeta(
    label: 'Висцеральный жир',
    unit: '',
    decimals: 0,
    weightLossBetterDown: true,
    muscleGainBetterUp: false,
  ),
  'bmr_kcal': _FieldMeta(label: 'BMR', unit: 'ккал', decimals: 0),
  'fat_free_mass_kg': _FieldMeta(
    label: 'Сухая масса',
    unit: 'кг',
    decimals: 1,
    weightLossBetterDown: false,
    muscleGainBetterUp: true,
  ),
  'bmi': _FieldMeta(label: 'BMI', unit: '', decimals: 1),
};

IconData? _deltaArrow(FieldDeltaDto d) {
  final v = d.deltaAbsolute;
  if (v == null || v == 0) return null;
  return v > 0 ? Icons.arrow_upward : Icons.arrow_downward;
}

Color _deltaColor(
  ThemeData theme,
  FieldDeltaDto d,
  String? goal,
  _FieldMeta meta,
) {
  final v = d.deltaAbsolute;
  if (v == null || v == 0) return theme.colorScheme.onSurfaceVariant;
  final goesDown = v < 0;
  final betterDown = switch (goal) {
    'weight_loss' => meta.weightLossBetterDown,
    'muscle_gain' => meta.muscleGainBetterUp == null
        ? null
        : !meta.muscleGainBetterUp!,
    _ => null,
  };
  if (betterDown == null) return theme.colorScheme.onSurfaceVariant;
  final improved = (betterDown && goesDown) || (!betterDown && !goesDown);
  return improved ? AppPalette.success : AppPalette.warning;
}

String _fmtValue(double? v, _FieldMeta meta) {
  if (v == null) return '—';
  final s = v.toStringAsFixed(meta.decimals);
  return meta.unit.isEmpty ? s : '$s ${meta.unit}';
}

String _fmtDelta(FieldDeltaDto d, _FieldMeta meta) {
  final abs = d.deltaAbsolute;
  final pct = d.deltaPercent;
  if (abs == null) return '—';
  final sign = abs > 0 ? '+' : '';
  final absStr = '$sign${abs.toStringAsFixed(meta.decimals)}';
  if (pct == null) return absStr;
  final pctSign = pct > 0 ? '+' : '';
  return '$absStr ${meta.unit} · $pctSign${pct.toStringAsFixed(1)}%';
}

String _fmtDateShort(DateTime d) => DateFormat('d MMM', 'ru').format(d);

String _fmtPickerLabel(MeasurementDto m) {
  final date = DateFormat('d MMM yyyy', 'ru').format(m.measuredAt);
  return '$date · ${m.weightKg.toStringAsFixed(1)} кг';
}

// --- Cache compare result by (a, b) pair ----------------------------------

class _ComparePair {
  const _ComparePair({required this.a, required this.b});
  final String a;
  final String b;

  @override
  bool operator ==(Object other) =>
      other is _ComparePair && other.a == a && other.b == b;
  @override
  int get hashCode => Object.hash(a, b);
}

final _compareProvider = FutureProvider.autoDispose
    .family<CompareResponseDto, _ComparePair>(
  (ref, pair) =>
      ref.watch(analyticsApiProvider).inbodyCompare(aId: pair.a, bId: pair.b),
);
