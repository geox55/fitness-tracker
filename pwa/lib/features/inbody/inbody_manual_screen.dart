import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../app/branding/portal_app_bar.dart';
import '../../app/branding/portal_scaffold.dart';
import '../../app/theme/app_colors.dart';
import '../../app/theme/app_spacing.dart';
import '../../data/api/failure.dart';
import '../../data/api/inbody_api.dart';

class InBodyManualScreen extends ConsumerStatefulWidget {
  const InBodyManualScreen({super.key});

  @override
  ConsumerState<InBodyManualScreen> createState() => _InBodyManualScreenState();
}

class _InBodyManualScreenState extends ConsumerState<InBodyManualScreen> {
  final _formKey = GlobalKey<FormState>();
  final _weightCtrl = TextEditingController();
  final _fatCtrl = TextEditingController();
  final _muscleCtrl = TextEditingController();
  DateTime _measuredAt = DateTime.now();
  bool _busy = false;
  String? _formError;
  bool _done = false;

  @override
  void dispose() {
    _weightCtrl.dispose();
    _fatCtrl.dispose();
    _muscleCtrl.dispose();
    super.dispose();
  }

  Future<void> _pickDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _measuredAt,
      firstDate: DateTime(2020),
      lastDate: DateTime.now(),
      locale: const Locale('ru'),
    );
    if (picked != null) {
      setState(() => _measuredAt = picked);
    }
  }

  Future<void> _submit() async {
    if (_busy) return;
    final form = _formKey.currentState;
    if (form == null || !form.validate()) return;
    setState(() {
      _busy = true;
      _formError = null;
    });
    try {
      final muscle = _muscleCtrl.text.trim();
      await ref.read(inBodyApiProvider).create(
            measuredAt: _measuredAt,
            weightKg: double.parse(_weightCtrl.text.trim()),
            bodyFatPercent: double.parse(_fatCtrl.text.trim()),
            muscleMassKg: muscle.isEmpty ? null : double.parse(muscle),
          );
      ref.invalidate(measurementsListProvider);
      if (!mounted) return;
      setState(() => _done = true);
    } on AppFailure catch (f) {
      if (!mounted) return;
      setState(() => _formError = f.message);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return PortalScaffold(
      appBar: PortalAppBar(title: const Text('Ввод замера вручную')),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(AppSpacing.lg),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 480),
              child: _done ? _buildSuccess(theme) : _buildForm(theme),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildSuccess(ThemeData theme) {
    return Column(
      children: [
        Icon(Icons.check_circle_outline, size: 64, color: AppPalette.success),
        const SizedBox(height: AppSpacing.lg),
        Text('Замер сохранён', style: theme.textTheme.titleLarge),
        const SizedBox(height: AppSpacing.sm),
        Text(
          'Данные появятся в графиках и аналитике.',
          style: theme.textTheme.bodyMedium?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: AppSpacing.xl),
        FilledButton(
          onPressed: () {
            final router = GoRouter.of(context);
            if (router.canPop()) {
              router.pop();
            } else {
              router.go('/home');
            }
          },
          child: const Text('Готово'),
        ),
      ],
    );
  }

  Widget _buildForm(ThemeData theme) {
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text('Дата замера', style: theme.textTheme.titleSmall),
          const SizedBox(height: AppSpacing.sm),
          InkWell(
            onTap: _pickDate,
            borderRadius: BorderRadius.circular(AppRadius.md),
            child: InputDecorator(
              decoration: const InputDecoration(
                prefixIcon: Icon(Icons.calendar_today),
              ),
              child: Text(
                DateFormat('d MMMM yyyy', 'ru').format(_measuredAt),
              ),
            ),
          ),
          const SizedBox(height: AppSpacing.lg),
          _NumField(
            controller: _weightCtrl,
            label: 'Вес (кг)',
            hint: '75.0',
            required: true,
          ),
          const SizedBox(height: AppSpacing.lg),
          _NumField(
            controller: _fatCtrl,
            label: '% жира',
            hint: '18.5',
            required: true,
          ),
          const SizedBox(height: AppSpacing.lg),
          _NumField(
            controller: _muscleCtrl,
            label: 'Мышечная масса (кг)',
            hint: '32.0',
            required: false,
          ),
          if (_formError != null) ...[
            const SizedBox(height: AppSpacing.md),
            Container(
              padding: const EdgeInsets.all(AppSpacing.md),
              decoration: BoxDecoration(
                color: theme.colorScheme.error.withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(AppRadius.md),
                border: Border.all(
                  color: theme.colorScheme.error.withValues(alpha: 0.4),
                ),
              ),
              child: Text(
                _formError!,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.error,
                ),
              ),
            ),
          ],
          const SizedBox(height: AppSpacing.xl),
          FilledButton(
            onPressed: _busy ? null : _submit,
            child: _busy
                ? const SizedBox(
                    width: 22,
                    height: 22,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Colors.white,
                    ),
                  )
                : const Text('Сохранить замер'),
          ),
        ],
      ),
    );
  }
}

class _NumField extends StatelessWidget {
  const _NumField({
    required this.controller,
    required this.label,
    required this.hint,
    required this.required,
  });

  final TextEditingController controller;
  final String label;
  final String hint;
  final bool required;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: theme.textTheme.titleSmall),
        const SizedBox(height: AppSpacing.sm),
        TextFormField(
          controller: controller,
          decoration: InputDecoration(hintText: hint),
          keyboardType: const TextInputType.numberWithOptions(decimal: true),
          validator: (v) {
            final t = v?.trim() ?? '';
            if (t.isEmpty) return required ? 'Обязательное поле' : null;
            final n = double.tryParse(t);
            if (n == null || n <= 0) return 'Введите положительное число';
            return null;
          },
        ),
      ],
    );
  }
}
