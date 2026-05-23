import 'package:flutter/material.dart';
import '../../app/branding/portal_app_bar.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../app/theme/app_spacing.dart';
import '../../data/api/catalog_api.dart';
import '../../data/api/failure.dart';
import 'exercise_edit_screen.dart';

/// Экран выбора упражнения. Открывается из активной тренировки.
/// Возвращает [ExerciseSummaryDto] через `Navigator.pop(context, ex)`.
///
/// Три таба:
/// - «Избранные» — отмеченные пользователем (spec 014 §3 Sc.2).
/// - «Свои» — пользовательские упражнения (`owner_id == user.id`).
/// - «Все» — глобальный каталог + свои, с фильтром по категории; избранные
///   текущей категории идут в верху списка (sort выполняется на бэке).
class ExercisePickerScreen extends ConsumerStatefulWidget {
  const ExercisePickerScreen({super.key});

  @override
  ConsumerState<ExercisePickerScreen> createState() => _ExercisePickerScreenState();
}

class _ExercisePickerScreenState extends ConsumerState<ExercisePickerScreen> {
  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 3,
      // По умолчанию открываем «Все» — это самый частый сценарий выбора.
      // Избранные и свои — power-user shortcut'ы.
      initialIndex: 2,
      child: Scaffold(
        appBar: PortalAppBar(
          title: const Text('Выбрать упражнение'),
          leading: IconButton(
            onPressed: () => Navigator.of(context).pop(),
            icon: const Icon(Icons.arrow_back),
          ),
          bottom: const TabBar(
            tabs: [
              Tab(text: 'Избранные'),
              Tab(text: 'Свои'),
              Tab(text: 'Все'),
            ],
          ),
        ),
        body: const TabBarView(
          children: [
            _FavoritesTab(),
            _OwnedTab(),
            _AllTab(),
          ],
        ),
      ),
    );
  }
}

// --- Shared providers ------------------------------------------------------

/// Список избранных. autoDispose — при выходе из пикера освобождаем кеш,
/// чтобы при следующем заходе подтянуть свежее.
final _favoritesListProvider =
    FutureProvider.autoDispose<ExerciseListResult>((ref) {
  return ref.watch(catalogApiProvider).listFavorites();
});

final _ownedListProvider =
    FutureProvider.autoDispose<ExerciseListResult>((ref) {
  return ref.watch(catalogApiProvider).listMine();
});

/// Инвалидация всех 3 списков. Зовём после любой мутации (toggle favorite,
/// create/update/delete owned), чтобы соседние табы при открытии увидели
/// актуальное состояние.
void _invalidateAllLists(WidgetRef ref) {
  ref.invalidate(_favoritesListProvider);
  ref.invalidate(_ownedListProvider);
  // _AllTab перезагружает себя через ValueNotifier — см. ниже.
  _AllTabState._refreshSignal.value++;
}

// --- Tab: Избранные --------------------------------------------------------

class _FavoritesTab extends ConsumerWidget {
  const _FavoritesTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(_favoritesListProvider);
    return async.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, _) => _ErrorView(
        error: e,
        onRetry: () => ref.invalidate(_favoritesListProvider),
      ),
      data: (data) {
        if (data.items.isEmpty) {
          return const _EmptyState(
            icon: Icons.star_border,
            title: 'Пока пусто',
            message: 'Помечайте упражнения звёздочкой на вкладке «Все».',
          );
        }
        return _ExerciseListView(items: data.items);
      },
    );
  }
}

// --- Tab: Свои -------------------------------------------------------------

class _OwnedTab extends ConsumerWidget {
  const _OwnedTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(_ownedListProvider);
    return Stack(
      children: [
        async.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (e, _) => _ErrorView(
            error: e,
            onRetry: () => ref.invalidate(_ownedListProvider),
          ),
          data: (data) {
            if (data.items.isEmpty) {
              return const _EmptyState(
                icon: Icons.add_circle_outline,
                title: 'Своих упражнений ещё нет',
                message: 'Кнопка «+» — добавить упражнение, видимое только вам.',
              );
            }
            return _ExerciseListView(items: data.items, withOwnerActions: true);
          },
        ),
        Positioned(
          right: AppSpacing.lg,
          bottom: AppSpacing.lg,
          child: FloatingActionButton.extended(
            onPressed: () => _openCreate(context, ref),
            icon: const Icon(Icons.add),
            label: const Text('Добавить'),
          ),
        ),
      ],
    );
  }

  Future<void> _openCreate(BuildContext context, WidgetRef ref) async {
    final created = await Navigator.of(context).push<ExerciseSummaryDto>(
      MaterialPageRoute(builder: (_) => const ExerciseEditScreen()),
    );
    if (created != null) _invalidateAllLists(ref);
  }
}

// --- Tab: Все --------------------------------------------------------------

class _AllTab extends ConsumerStatefulWidget {
  const _AllTab();

  @override
  ConsumerState<_AllTab> createState() => _AllTabState();
}

class _AllTabState extends ConsumerState<_AllTab> {
  // Тик-сигнал инвалидации — статический ValueNotifier, чтобы любая мутация
  // в чужом виджете могла попросить «Все» перезагрузиться. Это не глобальный
  // стейт приложения, а deduplicated событийный канал для этого экрана.
  static final ValueNotifier<int> _refreshSignal = ValueNotifier<int>(0);

  final _searchCtrl = TextEditingController();
  String? _muscleGroup; // null = "Все"

  // Порядок чипов — по убыванию числа упражнений в каталоге (так чаще
  // используемое попадает первым), плюс «Все» в начале.
  static const _groups = <(String label, String? value)>[
    ('Все', null),
    ('Ноги', 'quads'),
    ('Плечи', 'shoulders'),
    ('Кор', 'abs'),
    ('Грудь', 'chest'),
    ('Бицепс бедра', 'hamstrings'),
    ('Трицепс', 'triceps'),
    ('Бицепс', 'biceps'),
    ('Спина', 'back'),
    ('Широчайшие', 'lats'),
    ('Ягодицы', 'glutes'),
    ('Икры', 'calves'),
    ('Поясница', 'lower_back'),
    ('Предплечья', 'forearms'),
    ('Трапеции', 'traps'),
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
    return Column(
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
          // Перерисовываемся при изменении query/filter и при refresh-сигнале
          // (мутация favorite/owned в соседнем табе).
          child: ValueListenableBuilder<int>(
            valueListenable: _refreshSignal,
            builder: (_, tick, __) => _AllList(
              query: _searchCtrl.text.trim(),
              muscleGroup: _muscleGroup,
              // Ключ заставляет FutureBuilder перевыполнить запрос при
              // изменении параметров или тика.
              key: ValueKey('all-$tick-${_searchCtrl.text}-$_muscleGroup'),
            ),
          ),
        ),
      ],
    );
  }
}

class _AllList extends ConsumerWidget {
  const _AllList({required this.query, required this.muscleGroup, super.key});

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
          return _ErrorView(
            error: snap.error!,
            onRetry: () {
              // Триггерим перерисовку родителя через bump тика.
              _AllTabState._refreshSignal.value++;
            },
          );
        }
        final items = snap.data!.items;
        if (items.isEmpty) {
          return const _EmptyState(
            icon: Icons.search_off,
            title: 'Ничего не нашлось',
            message: 'Попробуйте другое название или категорию.',
          );
        }
        return _ExerciseListView(items: items);
      },
    );
  }
}

// --- Shared list view ------------------------------------------------------

class _ExerciseListView extends StatelessWidget {
  const _ExerciseListView({
    required this.items,
    this.withOwnerActions = false,
  });

  final List<ExerciseSummaryDto> items;
  final bool withOwnerActions;

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      padding: const EdgeInsets.fromLTRB(
        AppSpacing.lg,
        AppSpacing.sm,
        AppSpacing.lg,
        // Padding снизу — место под FAB на вкладке «Свои».
        AppSpacing.xxxl * 2,
      ),
      itemCount: items.length,
      separatorBuilder: (_, __) => const SizedBox(height: AppSpacing.sm),
      itemBuilder: (context, i) => _ExerciseTile(
        item: items[i],
        withOwnerActions: withOwnerActions && items[i].isMine,
      ),
    );
  }
}

// --- Tile ------------------------------------------------------------------

class _ExerciseTile extends ConsumerStatefulWidget {
  const _ExerciseTile({
    required this.item,
    required this.withOwnerActions,
  });

  final ExerciseSummaryDto item;
  final bool withOwnerActions;

  @override
  ConsumerState<_ExerciseTile> createState() => _ExerciseTileState();
}

class _ExerciseTileState extends ConsumerState<_ExerciseTile> {
  // Локальная копия для оптимистичного toggle: пользователь видит изменение
  // звезды до ответа сервера. На ошибке откатываемся.
  late ExerciseSummaryDto _item = widget.item;

  @override
  void didUpdateWidget(covariant _ExerciseTile old) {
    super.didUpdateWidget(old);
    if (old.item.id != widget.item.id ||
        old.item.isFavorite != widget.item.isFavorite) {
      _item = widget.item;
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final equipmentLabel =
        _item.equipment.isEmpty ? '' : ' · ${_equipmentRu(_item.equipment.first)}';
    return Material(
      color: theme.colorScheme.surfaceContainerHigh,
      borderRadius: BorderRadius.circular(AppRadius.lg),
      child: InkWell(
        onTap: () => Navigator.of(context).pop(_item),
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
                    Text(_item.displayName, style: theme.textTheme.titleMedium),
                    const SizedBox(height: 2),
                    Text(
                      '${_muscleRu(_item.primaryMuscleGroup)}$equipmentLabel',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ],
                ),
              ),
              IconButton(
                tooltip: _item.isFavorite ? 'Убрать из избранного' : 'В избранное',
                onPressed: _toggleFavorite,
                icon: Icon(
                  _item.isFavorite ? Icons.star : Icons.star_border,
                  color: _item.isFavorite
                      ? theme.colorScheme.primary
                      : theme.colorScheme.onSurfaceVariant,
                ),
              ),
              if (widget.withOwnerActions)
                PopupMenuButton<_OwnerAction>(
                  tooltip: 'Действия',
                  onSelected: _onOwnerAction,
                  itemBuilder: (_) => const [
                    PopupMenuItem(
                      value: _OwnerAction.edit,
                      child: ListTile(
                        leading: Icon(Icons.edit_outlined),
                        title: Text('Редактировать'),
                      ),
                    ),
                    PopupMenuItem(
                      value: _OwnerAction.delete,
                      child: ListTile(
                        leading: Icon(Icons.delete_outline),
                        title: Text('Удалить'),
                      ),
                    ),
                  ],
                ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _toggleFavorite() async {
    final api = ref.read(catalogApiProvider);
    final next = !_item.isFavorite;
    setState(() => _item = _item.copyWithFavorite(next));
    try {
      if (next) {
        await api.addFavorite(_item.id);
      } else {
        await api.removeFavorite(_item.id);
      }
      // Синхронизируем соседние табы — на них уже могло быть открыто
      // устаревшее значение.
      _invalidateAllLists(ref);
    } on AppFailure catch (f) {
      if (!mounted) return;
      setState(() => _item = _item.copyWithFavorite(!next));
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(f.message)),
      );
    }
  }

  Future<void> _onOwnerAction(_OwnerAction a) async {
    switch (a) {
      case _OwnerAction.edit:
        final updated = await Navigator.of(context).push<ExerciseSummaryDto>(
          MaterialPageRoute(
            builder: (_) => ExerciseEditScreen(initial: _item),
          ),
        );
        if (updated != null) {
          if (mounted) setState(() => _item = updated);
          _invalidateAllLists(ref);
        }
      case _OwnerAction.delete:
        final ok = await showDialog<bool>(
          context: context,
          builder: (_) => AlertDialog(
            title: const Text('Удалить упражнение?'),
            content: Text(
              '«${_item.displayName}» исчезнет из ваших списков. '
              'Раньше залогированные подходы останутся в истории.',
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: const Text('Отмена'),
              ),
              TextButton(
                onPressed: () => Navigator.pop(context, true),
                child: const Text('Удалить'),
              ),
            ],
          ),
        );
        if (ok != true) return;
        try {
          await ref.read(catalogApiProvider).deleteOwned(_item.id);
          _invalidateAllLists(ref);
        } on AppFailure catch (f) {
          if (!mounted) return;
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(f.message)),
          );
        }
    }
  }
}

enum _OwnerAction { edit, delete }

// --- Empty / Error views ---------------------------------------------------

class _EmptyState extends StatelessWidget {
  const _EmptyState({
    required this.icon,
    required this.title,
    required this.message,
  });

  final IconData icon;
  final String title;
  final String message;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.xxl),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 48, color: theme.colorScheme.onSurfaceVariant),
            const SizedBox(height: AppSpacing.md),
            Text(title, style: theme.textTheme.titleMedium),
            const SizedBox(height: AppSpacing.sm),
            Text(
              message,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
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
    final msg = error is AppFailure
        ? (error as AppFailure).message
        : 'Не удалось загрузить';
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.xxl),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.cloud_off, size: 48, color: theme.colorScheme.error),
            const SizedBox(height: AppSpacing.md),
            Text(msg, textAlign: TextAlign.center),
            const SizedBox(height: AppSpacing.md),
            OutlinedButton(onPressed: onRetry, child: const Text('Повторить')),
          ],
        ),
      ),
    );
  }
}

// --- i18n labels (shared with edit screen) --------------------------------

// Подписи синхронизированы с чипами фильтра в _groups — иначе чип «Ноги»
// расходится с подписью «Квадрицепс» на той же карточке.
String muscleRu(String key) => switch (key) {
      'chest' => 'Грудь',
      'back' => 'Спина',
      'quads' => 'Ноги',
      'hamstrings' => 'Бицепс бедра',
      'glutes' => 'Ягодицы',
      'calves' => 'Икры',
      'shoulders' => 'Плечи',
      'biceps' => 'Бицепс',
      'triceps' => 'Трицепс',
      'lats' => 'Широчайшие',
      'traps' => 'Трапеции',
      'lower_back' => 'Поясница',
      'forearms' => 'Предплечья',
      'abs' => 'Кор',
      'cardio' => 'Кардио',
      _ => key,
    };

// Полный enum spec 004 §6. Используется и каталогом, и экраном профиля
// (поле equipment_available). При расширении бэка — обновить mapping здесь.
String equipmentRu(String key) => switch (key) {
      'barbell' => 'штанга',
      'dumbbell' => 'гантели',
      'kettlebell' => 'гиря',
      'machine' => 'тренажёр',
      'cable' => 'блок',
      'bodyweight' => 'без оборудования',
      'bench' => 'скамья',
      'pullup_bar' => 'турник',
      'dip_bars' => 'брусья',
      'resistance_band' => 'резинка',
      'medicine_ball' => 'медбол',
      'treadmill' => 'дорожка',
      'stationary_bike' => 'велотренажёр',
      'rowing_machine' => 'гребной тренажёр',
      'other' => 'другое',
      _ => key,
    };

// Локальные shadow'ы для tile (исторически были private — оставляю, чтобы
// не плодить imports снаружи).
String _muscleRu(String key) => muscleRu(key);
String _equipmentRu(String key) => equipmentRu(key);
