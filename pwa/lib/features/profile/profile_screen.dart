// Файл — UI-обвязка над bottom-sheet'ами. Сначала ждём пользовательский выбор
// (await _showXxxSheet), затем сразу делаем PATCH и показываем SnackBar — это
// нормальный flow, экран не размонтируется между ожиданием и patch'ом.
// Точечные mounted-проверки ничего не добавили бы кроме шума.
// ignore_for_file: use_build_context_synchronously

import 'package:flutter/material.dart';
import '../../app/branding/portal_scaffold.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';

import '../../app/theme/app_spacing.dart';
import '../../data/api/analytics_api.dart';
import '../../data/api/failure.dart';
import '../../data/api/profile_api.dart';
import '../auth/auth_state.dart';
import '../catalog/exercise_picker_screen.dart' show equipmentRu;

/// Экран «Мой профиль».
///
/// Поля редактируются inline через bottom-sheet с одним полем за раз — так не
/// нужно показывать огромную форму и вводить «черновое состояние»: каждый
/// PATCH летит сразу, ошибки видны точечно.
class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(profileProvider);
    return PortalScaffold(
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: () async => ref.refresh(profileProvider.future),
          child: async.when(
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (err, _) => _ErrorView(
              error: err,
              onRetry: () => ref.invalidate(profileProvider),
            ),
            data: (data) => _ProfileContent(profile: data),
          ),
        ),
      ),
    );
  }
}

// --- Content ---------------------------------------------------------------

class _ProfileContent extends ConsumerWidget {
  const _ProfileContent({required this.profile});
  final ProfileDto profile;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ListView(
      padding: const EdgeInsets.fromLTRB(
        AppSpacing.lg,
        AppSpacing.lg,
        AppSpacing.lg,
        AppSpacing.xxxl * 2,
      ),
      children: [
        _Header(profile: profile),
        const SizedBox(height: AppSpacing.xxl),
        _SectionLabel(text: 'Основное'),
        const SizedBox(height: AppSpacing.md),
        _FieldCard(
          label: 'Имя',
          value: profile.name,
          placeholder: 'Введите имя',
          icon: Icons.person_outline,
          onTap: () => _editName(context, ref, profile),
        ),
        const SizedBox(height: AppSpacing.sm),
        _FieldCard(
          label: 'Пол',
          value: _formatSex(profile.sex),
          placeholder: 'Выберите пол',
          icon: Icons.wc_outlined,
          onTap: () => _editSex(context, ref, profile),
        ),
        const SizedBox(height: AppSpacing.sm),
        _FieldCard(
          label: 'Дата рождения',
          value:
              profile.birthDate == null ? null : _formatDate(profile.birthDate!),
          placeholder: 'Укажите дату рождения',
          icon: Icons.cake_outlined,
          onTap: () => _editBirthDate(context, ref, profile),
        ),
        const SizedBox(height: AppSpacing.lg),
        _SectionLabel(text: 'Параметры тела'),
        const SizedBox(height: AppSpacing.md),
        Row(
          children: [
            Expanded(
              child: _CompactMetric(
                label: 'Рост',
                value: profile.heightCm == null
                    ? null
                    : '${profile.heightCm!.toStringAsFixed(0)} см',
                placeholder: 'Не указан',
                icon: Icons.straighten,
                onTap: () => _editHeight(context, ref, profile),
              ),
            ),
            const SizedBox(width: AppSpacing.md),
            Expanded(
              child: _CompactMetric(
                label: 'Вес',
                value: profile.baselineWeightKg == null
                    ? null
                    : '${profile.baselineWeightKg!.toStringAsFixed(1)} кг',
                placeholder: 'Не указан',
                icon: Icons.monitor_weight_outlined,
                onTap: () => _editWeight(context, ref, profile),
              ),
            ),
          ],
        ),
        const SizedBox(height: AppSpacing.sm),
        _BmrCard(bmrKcal: profile.bmrKcal),
        const SizedBox(height: AppSpacing.lg),
        _SectionLabel(text: 'Цели тренировок'),
        const SizedBox(height: AppSpacing.md),
        _FieldCard(
          label: 'Цель',
          value: _formatGoal(profile.goal),
          placeholder: 'Выберите цель',
          icon: Icons.flag_outlined,
          onTap: () => _editGoal(context, ref, profile),
        ),
        const SizedBox(height: AppSpacing.sm),
        _FieldCard(
          label: 'Уровень подготовки',
          value: _formatLevel(profile.trainingLevel),
          placeholder: 'Выберите уровень',
          icon: Icons.trending_up,
          onTap: () => _editLevel(context, ref, profile),
        ),
        const SizedBox(height: AppSpacing.sm),
        _FieldCard(
          label: 'Частота',
          value: profile.trainingFrequency == null
              ? null
              : '${profile.trainingFrequency} раз/нед',
          placeholder: 'Сколько раз в неделю',
          icon: Icons.calendar_month,
          onTap: () => _editFrequency(context, ref, profile),
        ),
        const SizedBox(height: AppSpacing.sm),
        // Spec 004 REQ-09: ограничивает пул упражнений в AI-генераторе.
        // value=null → «Типовой зал» (бэк подставит DEFAULT_EQUIPMENT_AVAILABLE);
        // [] → «Только своё тело»; иначе короткое перечисление.
        _FieldCard(
          label: 'Оборудование',
          value: _formatEquipment(profile.equipmentAvailable),
          placeholder: 'Типовой зал',
          icon: Icons.fitness_center,
          onTap: () => _editEquipment(context, ref, profile),
        ),
        const SizedBox(height: AppSpacing.lg),
        // REQ-06 spec 010: целевые значения для прогресс-бара. Показываем
        // только то поле, которое релевантно выбранной цели — это снижает
        // шум в UI; иначе пользователь видит две одинаковые строки и
        // не понимает, какую заполнять.
        if (profile.goal == 'weight_loss' || profile.goal == 'muscle_gain') ...[
          _SectionLabel(text: 'Целевое значение'),
          const SizedBox(height: AppSpacing.md),
          if (profile.goal == 'weight_loss')
            _FieldCard(
              label: 'Целевой вес',
              value: profile.targetWeightKg == null
                  ? null
                  : '${profile.targetWeightKg!.toStringAsFixed(1)} кг',
              placeholder: 'До какого веса хотите дойти',
              icon: Icons.flag,
              onTap: () => _editTargetWeight(context, ref, profile),
            )
          else
            _FieldCard(
              label: 'Целевая мышечная масса',
              value: profile.targetMuscleKg == null
                  ? null
                  : '${profile.targetMuscleKg!.toStringAsFixed(1)} кг',
              placeholder: 'Сколько мышц набрать',
              icon: Icons.fitness_center,
              onTap: () => _editTargetMuscle(context, ref, profile),
            ),
          const SizedBox(height: AppSpacing.sm),
          _FieldCard(
            label: 'Старт работы над целью',
            value: profile.goalStartedAt == null
                ? null
                : _formatDate(profile.goalStartedAt!),
            placeholder: 'Дата старта',
            icon: Icons.event_outlined,
            onTap: () => _editGoalStartedAt(context, ref, profile),
          ),
        ],
        const SizedBox(height: AppSpacing.xxl),
        _LogoutButton(),
      ],
    );
  }
}

// --- Header (avatar + name + email) ---------------------------------------

class _Header extends ConsumerWidget {
  const _Header({required this.profile});
  final ProfileDto profile;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
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
          _Avatar(profile: profile),
          const SizedBox(width: AppSpacing.lg),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  profile.name ?? 'Заполните профиль',
                  style: theme.textTheme.titleLarge?.copyWith(
                    fontStyle: profile.name == null
                        ? FontStyle.italic
                        : FontStyle.normal,
                    color: profile.name == null
                        ? theme.colorScheme.onSurfaceVariant
                        : null,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 2),
                Text(
                  profile.email,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: AppSpacing.sm),
                Row(
                  children: [
                    OutlinedButton.icon(
                      onPressed: () => _pickAndUpload(context, ref),
                      icon: const Icon(Icons.photo_camera_outlined, size: 16),
                      label: const Text('Фото'),
                      style: OutlinedButton.styleFrom(
                        // Не используем Size.fromHeight — он даёт width=∞,
                        // и Row в Column ломается на BoxConstraints forces
                        // infinite width. Указываем width=0, height=36.
                        minimumSize: const Size(0, 36),
                        padding: const EdgeInsets.symmetric(
                          horizontal: AppSpacing.md,
                        ),
                      ),
                    ),
                    if (profile.photoUrl != null) ...[
                      const SizedBox(width: AppSpacing.sm),
                      IconButton(
                        tooltip: 'Удалить фото',
                        icon: const Icon(Icons.delete_outline, size: 20),
                        onPressed: () => _deletePhoto(context, ref),
                      ),
                    ],
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _Avatar extends StatelessWidget {
  const _Avatar({required this.profile});
  final ProfileDto profile;

  // 72 → 112 px: на хедере профиля старый размер выглядел жидко.
  // 112 — близко к большим материал-аватарам и не ломает соседние строки.
  static const double _size = 112;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final url = profile.photoUrl;
    final border = Border.all(color: theme.colorScheme.primary, width: 2);

    if (url != null) {
      // На Flutter web `DecorationImage(NetworkImage(url))` рисует через
      // canvas и требует CORS-заголовки на signed-URL — MinIO в dev их не
      // отдаёт, и аватарка получалась пустой. `Image.network`
      // использует `<img>`-элемент, CORS для display не нужен.
      //
      // Container + shape:circle + clipBehavior:antiAlias на web рендерит
      // нечёткие края — квадратные углы Image выглядывают из круга. ClipOval
      // на дочернем элементе режет ровно по эллипсу, а border остаётся за
      // ним и рисуется поверх.
      return Container(
        width: _size,
        height: _size,
        decoration: BoxDecoration(shape: BoxShape.circle, border: border),
        child: ClipOval(
          child: Image.network(
            url,
            width: _size,
            height: _size,
            fit: BoxFit.cover,
            errorBuilder: (_, __, ___) => _initials(theme),
          ),
        ),
      );
    }
    return Container(
      width: _size,
      height: _size,
      alignment: Alignment.center,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        border: border,
        color: theme.colorScheme.primary.withValues(alpha: 0.18),
      ),
      // Без clipBehavior дочерний _initials своим color-фоном вылезал в
      // углы bounding-box'а — placeholder выглядел квадратным. Clip.antiAlias
      // принудительно режет содержимое по форме (circle), как и в ветке с фото.
      clipBehavior: Clip.antiAlias,
      child: _initials(theme),
    );
  }

  Widget _initials(ThemeData theme) {
    final initial = (profile.name?.isNotEmpty ?? false)
        ? profile.name!.substring(0, 1).toUpperCase()
        : '?';
    // Намеренно без собственного color/Container — фон даёт внешний
    // контейнер (заливка через decoration). Раньше дублирующий color на
    // alignment.center-Container'е растягивался во всю площадь и в no-clip
    // ветке вылезал из круга. Теперь это просто центрирующий wrapper.
    return Center(
      child: Text(
        initial,
        style: theme.textTheme.displaySmall?.copyWith(
          color: theme.colorScheme.primary,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}

// --- Building blocks -------------------------------------------------------

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
        letterSpacing: 1.6,
      ),
    );
  }
}

class _FieldCard extends StatelessWidget {
  const _FieldCard({
    required this.label,
    required this.value,
    required this.placeholder,
    required this.icon,
    required this.onTap,
  });

  final String label;
  final String? value;
  final String placeholder;
  final IconData icon;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Material(
      color: theme.colorScheme.surfaceContainerHigh,
      borderRadius: BorderRadius.circular(AppRadius.lg),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(AppRadius.lg),
        child: Container(
          padding: const EdgeInsets.symmetric(
            horizontal: AppSpacing.lg,
            vertical: AppSpacing.md,
          ),
          decoration: BoxDecoration(
            border: Border.all(color: theme.colorScheme.outline),
            borderRadius: BorderRadius.circular(AppRadius.lg),
          ),
          child: Row(
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: theme.colorScheme.primary.withValues(alpha: 0.16),
                  borderRadius: BorderRadius.circular(AppRadius.sm),
                ),
                child: Icon(icon, color: theme.colorScheme.primary, size: 20),
              ),
              const SizedBox(width: AppSpacing.md),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      label,
                      style: theme.textTheme.labelSmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                        letterSpacing: 1.2,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      value ?? placeholder,
                      style: theme.textTheme.titleMedium?.copyWith(
                        color: value == null
                            ? theme.colorScheme.onSurfaceVariant
                                .withValues(alpha: 0.7)
                            : null,
                        fontStyle:
                            value == null ? FontStyle.italic : FontStyle.normal,
                      ),
                    ),
                  ],
                ),
              ),
              Icon(
                Icons.chevron_right,
                color: theme.colorScheme.onSurfaceVariant,
                size: 20,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _CompactMetric extends StatelessWidget {
  const _CompactMetric({
    required this.label,
    required this.value,
    required this.placeholder,
    required this.icon,
    required this.onTap,
  });

  final String label;
  final String? value;
  final String placeholder;
  final IconData icon;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Material(
      color: theme.colorScheme.surfaceContainerHigh,
      borderRadius: BorderRadius.circular(AppRadius.lg),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(AppRadius.lg),
        child: Container(
          padding: const EdgeInsets.all(AppSpacing.lg),
          decoration: BoxDecoration(
            border: Border.all(color: theme.colorScheme.outline),
            borderRadius: BorderRadius.circular(AppRadius.lg),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    icon,
                    color: theme.colorScheme.primary,
                    size: 18,
                  ),
                  const SizedBox(width: AppSpacing.xs),
                  Text(
                    label.toUpperCase(),
                    style: theme.textTheme.labelSmall?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                      letterSpacing: 1.2,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: AppSpacing.sm),
              Text(
                value ?? placeholder,
                style: value == null
                    ? theme.textTheme.titleMedium?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant
                            .withValues(alpha: 0.7),
                        fontStyle: FontStyle.italic,
                      )
                    : theme.textTheme.headlineMedium,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _BmrCard extends StatelessWidget {
  const _BmrCard({required this.bmrKcal});
  final int? bmrKcal;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.all(AppSpacing.lg),
      decoration: BoxDecoration(
        color: theme.colorScheme.primary.withValues(alpha: 0.10),
        borderRadius: BorderRadius.circular(AppRadius.lg),
        border: Border.all(
          color: theme.colorScheme.primary.withValues(alpha: 0.4),
        ),
      ),
      child: Row(
        children: [
          Icon(
            Icons.local_fire_department,
            color: theme.colorScheme.primary,
            size: 24,
          ),
          const SizedBox(width: AppSpacing.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'БАЗОВЫЙ ОБМЕН (BMR)',
                  style: theme.textTheme.labelSmall?.copyWith(
                    color: theme.colorScheme.primary,
                    letterSpacing: 1.2,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  bmrKcal == null
                      ? 'Заполните рост, вес, возраст и пол'
                      : '$bmrKcal ккал/сутки',
                  style: theme.textTheme.titleMedium,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _LogoutButton extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return OutlinedButton.icon(
      onPressed: () async {
        await ref.read(authSessionProvider.notifier).logout();
        if (!context.mounted) return;
        context.go('/login');
      },
      icon: const Icon(Icons.logout),
      label: const Text('Выйти'),
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
    final message = error is AppFailure
        ? (error as AppFailure).message
        : 'Не удалось загрузить профиль';
    return ListView(
      padding: const EdgeInsets.all(AppSpacing.xxl),
      children: [
        const SizedBox(height: 80),
        Icon(Icons.cloud_off, size: 48, color: theme.colorScheme.error),
        const SizedBox(height: AppSpacing.md),
        Text(message, textAlign: TextAlign.center),
        const SizedBox(height: AppSpacing.lg),
        OutlinedButton(onPressed: onRetry, child: const Text('Повторить')),
      ],
    );
  }
}

// --- Edit handlers (bottom sheets / dialogs) ------------------------------

Future<void> _patch(
  BuildContext context,
  WidgetRef ref,
  Future<ProfileDto> Function(ProfileApi) action,
) async {
  try {
    final api = ref.read(profileApiProvider);
    await action(api);
    ref.invalidate(profileProvider);
  } on AppFailure catch (f) {
    if (!context.mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(f.message)),
    );
  }
}

Future<void> _editName(
  BuildContext context,
  WidgetRef ref,
  ProfileDto profile,
) async {
  final result = await _showTextSheet(
    context,
    title: 'Имя',
    initial: profile.name ?? '',
    hint: 'Как к вам обращаться',
    validator: (v) => v.trim().isEmpty ? 'Введите имя' : null,
  );
  if (result == null) return;
  await _patch(context, ref, (api) => api.patch(name: result));
}

Future<void> _editSex(
  BuildContext context,
  WidgetRef ref,
  ProfileDto profile,
) async {
  final result = await _showChoiceSheet(
    context,
    title: 'Пол',
    options: const [
      ('male', 'Мужской'),
      ('female', 'Женский'),
    ],
    selected: profile.sex,
  );
  if (result == null) return;
  await _patch(context, ref, (api) => api.patch(sex: result));
}

Future<void> _editBirthDate(
  BuildContext context,
  WidgetRef ref,
  ProfileDto profile,
) async {
  final now = DateTime.now();
  final picked = await showDatePicker(
    context: context,
    firstDate: DateTime(now.year - 100),
    lastDate: DateTime(now.year - 14, now.month, now.day),
    initialDate:
        profile.birthDate ?? DateTime(now.year - 25, now.month, now.day),
  );
  if (picked == null) return;
  await _patch(context, ref, (api) => api.patch(birthDate: picked));
}

Future<void> _editHeight(
  BuildContext context,
  WidgetRef ref,
  ProfileDto profile,
) async {
  final result = await _showNumberSheet(
    context,
    title: 'Рост, см',
    initial: profile.heightCm?.toStringAsFixed(0) ?? '',
    hint: '175',
    validator: (n) {
      if (n == null) return 'Введите число';
      if (n < 100 || n > 250) return 'От 100 до 250';
      return null;
    },
  );
  if (result == null) return;
  await _patch(context, ref, (api) => api.patch(heightCm: result));
}

Future<void> _editWeight(
  BuildContext context,
  WidgetRef ref,
  ProfileDto profile,
) async {
  final result = await _showNumberSheet(
    context,
    title: 'Вес, кг',
    initial: profile.baselineWeightKg?.toStringAsFixed(1) ?? '',
    hint: '70',
    validator: (n) {
      if (n == null) return 'Введите число';
      if (n < 30 || n > 300) return 'От 30 до 300';
      return null;
    },
  );
  if (result == null) return;
  await _patch(context, ref, (api) => api.patch(baselineWeightKg: result));
}

Future<void> _editGoal(
  BuildContext context,
  WidgetRef ref,
  ProfileDto profile,
) async {
  final result = await _showChoiceSheet(
    context,
    title: 'Цель',
    options: const [
      ('weight_loss', 'Похудение'),
      ('muscle_gain', 'Набор массы'),
      ('maintenance', 'Поддержание'),
    ],
    selected: profile.goal,
  );
  if (result == null) return;

  // Если goal сменился (а не остался прежним) или ставится впервые —
  // автоматически проставляем goal_started_at = сегодня. Бэкенд сам этого
  // не делает: он не может различить «PATCH без изменения goal» и «новый
  // goal с тем же значением». Пользователь сможет переопределить дату
  // вручную через _editGoalStartedAt.
  final shouldResetStart =
      result != 'maintenance' && profile.goal != result;
  await _patch(
    context,
    ref,
    (api) => api.patch(
      goal: result,
      goalStartedAt: shouldResetStart ? DateTime.now() : null,
    ),
  );
  // Прогресс-карточка завязана на goal+target_*; пересчитываем сразу.
  ref.invalidate(goalProgressProvider);
}

Future<void> _editTargetWeight(
  BuildContext context,
  WidgetRef ref,
  ProfileDto profile,
) async {
  final result = await _showNumberSheet(
    context,
    title: 'Целевой вес, кг',
    initial: profile.targetWeightKg?.toStringAsFixed(1) ?? '',
    hint: profile.baselineWeightKg == null
        ? '70'
        : (profile.baselineWeightKg! - 5).toStringAsFixed(0),
    validator: (n) {
      if (n == null) return 'Введите число';
      if (n < 30 || n > 300) return 'От 30 до 300';
      return null;
    },
  );
  if (result == null) return;
  await _patch(context, ref, (api) => api.patch(targetWeightKg: result));
  ref.invalidate(goalProgressProvider);
}

Future<void> _editTargetMuscle(
  BuildContext context,
  WidgetRef ref,
  ProfileDto profile,
) async {
  final result = await _showNumberSheet(
    context,
    title: 'Целевая мышечная масса, кг',
    initial: profile.targetMuscleKg?.toStringAsFixed(1) ?? '',
    hint: '35',
    validator: (n) {
      if (n == null) return 'Введите число';
      if (n < 5 || n > 120) return 'От 5 до 120';
      return null;
    },
  );
  if (result == null) return;
  await _patch(context, ref, (api) => api.patch(targetMuscleKg: result));
  ref.invalidate(goalProgressProvider);
}

Future<void> _editGoalStartedAt(
  BuildContext context,
  WidgetRef ref,
  ProfileDto profile,
) async {
  final now = DateTime.now();
  final picked = await showDatePicker(
    context: context,
    firstDate: DateTime(now.year - 5),
    lastDate: now,
    initialDate: profile.goalStartedAt ?? now,
  );
  if (picked == null) return;
  await _patch(context, ref, (api) => api.patch(goalStartedAt: picked));
  ref.invalidate(goalProgressProvider);
}

Future<void> _editLevel(
  BuildContext context,
  WidgetRef ref,
  ProfileDto profile,
) async {
  final result = await _showChoiceSheet(
    context,
    title: 'Уровень подготовки',
    options: const [
      ('beginner', 'Новичок'),
      ('intermediate', 'Средний'),
      ('advanced', 'Продвинутый'),
    ],
    selected: profile.trainingLevel,
  );
  if (result == null) return;
  await _patch(context, ref, (api) => api.patch(trainingLevel: result));
}

Future<void> _editFrequency(
  BuildContext context,
  WidgetRef ref,
  ProfileDto profile,
) async {
  final result = await _showChoiceSheet(
    context,
    title: 'Частота тренировок (раз/неделя)',
    options: const [
      ('2', '2 раза'),
      ('3', '3 раза'),
      ('4', '4 раза'),
      ('5', '5 раз'),
      ('6', '6 раз'),
    ],
    selected: profile.trainingFrequency?.toString(),
  );
  if (result == null) return;
  await _patch(
    context,
    ref,
    (api) => api.patch(trainingFrequency: int.parse(result)),
  );
}

// Полный enum из spec 004 §6 — порядок зафиксирован, чтобы UI и backend
// показывали одинаковую последовательность.
const _equipmentOptions = <String>[
  'barbell',
  'dumbbell',
  'kettlebell',
  'machine',
  'cable',
  'bodyweight',
  'bench',
  'pullup_bar',
  'dip_bars',
  'resistance_band',
  'medicine_ball',
  'treadmill',
  'stationary_bike',
  'rowing_machine',
  'other',
];

Future<void> _editEquipment(
  BuildContext context,
  WidgetRef ref,
  ProfileDto profile,
) async {
  final result = await _showEquipmentSheet(
    context,
    initial: profile.equipmentAvailable,
  );
  if (result == null) return;
  await _patch(context, ref, (api) => api.patch(equipmentAvailable: result));
}

Future<void> _pickAndUpload(BuildContext context, WidgetRef ref) async {
  try {
    final picker = ImagePicker();
    final picked = await picker.pickImage(
      source: ImageSource.gallery,
      maxWidth: 2048,
      maxHeight: 2048,
      imageQuality: 90,
    );
    if (picked == null) return;
    final bytes = await picked.readAsBytes();
    final ext = picked.name.split('.').last.toLowerCase();
    final ct = ext == 'png' ? 'image/png' : 'image/jpeg';
    final api = ref.read(profileApiProvider);
    await api.uploadPhoto(
      bytes: bytes,
      filename: picked.name,
      contentType: ct,
    );
    ref.invalidate(profileProvider);
  } on AppFailure catch (f) {
    if (!context.mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(f.message)),
    );
  }
}

Future<void> _deletePhoto(BuildContext context, WidgetRef ref) async {
  try {
    await ref.read(profileApiProvider).deletePhoto();
    ref.invalidate(profileProvider);
  } on AppFailure catch (f) {
    if (!context.mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(f.message)),
    );
  }
}

// --- Sheet helpers ---------------------------------------------------------

Future<String?> _showTextSheet(
  BuildContext context, {
  required String title,
  required String initial,
  required String hint,
  String? Function(String value)? validator,
}) async {
  final ctrl = TextEditingController(text: initial);
  String? error;
  return showModalBottomSheet<String>(
    context: context,
    isScrollControlled: true,
    builder: (ctx) {
      return StatefulBuilder(
        builder: (ctx, setState) {
          return Padding(
            padding: EdgeInsets.fromLTRB(
              AppSpacing.lg,
              AppSpacing.lg,
              AppSpacing.lg,
              MediaQuery.of(ctx).viewInsets.bottom + AppSpacing.lg,
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  title,
                  style: Theme.of(ctx).textTheme.titleLarge,
                ),
                const SizedBox(height: AppSpacing.lg),
                TextField(
                  controller: ctrl,
                  autofocus: true,
                  decoration: InputDecoration(
                    hintText: hint,
                    errorText: error,
                  ),
                ),
                const SizedBox(height: AppSpacing.lg),
                ElevatedButton(
                  onPressed: () {
                    final v = ctrl.text;
                    final err = validator?.call(v);
                    if (err != null) {
                      setState(() => error = err);
                      return;
                    }
                    Navigator.of(ctx).pop(v.trim());
                  },
                  child: const Text('Сохранить'),
                ),
              ],
            ),
          );
        },
      );
    },
  );
}

Future<double?> _showNumberSheet(
  BuildContext context, {
  required String title,
  required String initial,
  required String hint,
  String? Function(double? value)? validator,
}) async {
  final ctrl = TextEditingController(text: initial);
  String? error;
  return showModalBottomSheet<double>(
    context: context,
    isScrollControlled: true,
    builder: (ctx) {
      return StatefulBuilder(
        builder: (ctx, setState) {
          return Padding(
            padding: EdgeInsets.fromLTRB(
              AppSpacing.lg,
              AppSpacing.lg,
              AppSpacing.lg,
              MediaQuery.of(ctx).viewInsets.bottom + AppSpacing.lg,
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(title, style: Theme.of(ctx).textTheme.titleLarge),
                const SizedBox(height: AppSpacing.lg),
                TextField(
                  controller: ctrl,
                  autofocus: true,
                  keyboardType:
                      const TextInputType.numberWithOptions(decimal: true),
                  decoration: InputDecoration(
                    hintText: hint,
                    errorText: error,
                  ),
                ),
                const SizedBox(height: AppSpacing.lg),
                ElevatedButton(
                  onPressed: () {
                    final v = double.tryParse(
                      ctrl.text.replaceAll(',', '.'),
                    );
                    final err = validator?.call(v);
                    if (err != null) {
                      setState(() => error = err);
                      return;
                    }
                    Navigator.of(ctx).pop(v);
                  },
                  child: const Text('Сохранить'),
                ),
              ],
            ),
          );
        },
      );
    },
  );
}

Future<List<String>?> _showEquipmentSheet(
  BuildContext context, {
  required List<String>? initial,
}) async {
  // Стартовое состояние: если null (не настраивал) — пустой набор, чтобы
  // пользователь явно выбрал, что у него есть. Если [] — тоже пустой.
  final selected = <String>{...?initial};
  return showModalBottomSheet<List<String>>(
    context: context,
    isScrollControlled: true,
    builder: (ctx) {
      return SafeArea(
        child: DraggableScrollableSheet(
          initialChildSize: 0.7,
          minChildSize: 0.5,
          maxChildSize: 0.95,
          expand: false,
          builder: (ctx, scrollController) {
            return StatefulBuilder(
              builder: (ctx, setState) {
                final theme = Theme.of(ctx);
                return Padding(
                  padding: const EdgeInsets.fromLTRB(
                    AppSpacing.lg,
                    AppSpacing.lg,
                    AppSpacing.lg,
                    AppSpacing.md,
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text(
                        'Доступное оборудование',
                        style: theme.textTheme.titleLarge,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Отметьте, что у вас есть под рукой — генератор '
                        'плана будет подбирать упражнения только из этого '
                        'списка. Если оставить пустым, план рассчитается под '
                        'типовой коммерческий зал.',
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                      const SizedBox(height: AppSpacing.md),
                      Expanded(
                        child: SingleChildScrollView(
                          controller: scrollController,
                          child: Wrap(
                            spacing: AppSpacing.sm,
                            runSpacing: AppSpacing.sm,
                            children: [
                              for (final e in _equipmentOptions)
                                FilterChip(
                                  label: Text(equipmentRu(e)),
                                  selected: selected.contains(e),
                                  onSelected: (v) => setState(() {
                                    if (v) {
                                      selected.add(e);
                                    } else {
                                      selected.remove(e);
                                    }
                                  }),
                                ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: AppSpacing.md),
                      Row(
                        children: [
                          Expanded(
                            child: OutlinedButton(
                              onPressed: () => setState(selected.clear),
                              child: const Text('Очистить'),
                            ),
                          ),
                          const SizedBox(width: AppSpacing.md),
                          Expanded(
                            child: ElevatedButton(
                              onPressed: () => Navigator.of(ctx).pop(
                                selected.toList()..sort(),
                              ),
                              child: const Text('Сохранить'),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                );
              },
            );
          },
        ),
      );
    },
  );
}

Future<String?> _showChoiceSheet(
  BuildContext context, {
  required String title,
  required List<(String, String)> options,
  required String? selected,
}) async {
  return showModalBottomSheet<String>(
    context: context,
    builder: (ctx) {
      final theme = Theme.of(ctx);
      return SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(AppSpacing.lg),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(title, style: theme.textTheme.titleLarge),
              const SizedBox(height: AppSpacing.md),
              for (final (key, label) in options)
                ListTile(
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(AppRadius.md),
                  ),
                  title: Text(label),
                  trailing: key == selected
                      ? Icon(
                          Icons.check_circle,
                          color: theme.colorScheme.primary,
                        )
                      : null,
                  onTap: () => Navigator.of(ctx).pop(key),
                ),
            ],
          ),
        ),
      );
    },
  );
}

// --- Formatting -----------------------------------------------------------

String? _formatSex(String? sex) => switch (sex) {
      'male' => 'Мужской',
      'female' => 'Женский',
      _ => null,
    };

String? _formatGoal(String? goal) => switch (goal) {
      'weight_loss' => 'Похудение',
      'muscle_gain' => 'Набор массы',
      'maintenance' => 'Поддержание',
      _ => null,
    };

String? _formatLevel(String? level) => switch (level) {
      'beginner' => 'Новичок',
      'intermediate' => 'Средний',
      'advanced' => 'Продвинутый',
      _ => null,
    };

String _formatDate(DateTime d) =>
    '${d.day.toString().padLeft(2, '0')}.${d.month.toString().padLeft(2, '0')}.${d.year}';

String? _formatEquipment(List<String>? items) {
  if (items == null) return null;
  if (items.isEmpty) return 'Только своё тело';
  if (items.length <= 3) return items.map(equipmentRu).join(', ');
  return '${items.length} элементов: ${items.take(2).map(equipmentRu).join(', ')}…';
}
