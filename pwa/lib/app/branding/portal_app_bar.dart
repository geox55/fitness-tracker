// PortalAppBar — единый header для всех "вглубь" экранов: внутренних
// деталей, модалок, форм. Прозрачный фон (чтобы PortalBackdrop под ним
// был виден), стрелка-back по умолчанию (если context.canPop()), один
// и тот же visual стиль.
//
// На shell-экранах (home/training/stats/profile) этот AppBar не нужен —
// у них собственный inline-header с аватаркой/датой.

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class PortalAppBar extends StatelessWidget implements PreferredSizeWidget {
  const PortalAppBar({
    super.key,
    this.title,
    this.actions,
    this.leading,
    this.backFallbackPath = '/home',
    this.bottom,
  });

  /// Заголовок — обычно Text('...'), но можно сложный Widget.
  final Widget? title;

  final List<Widget>? actions;

  /// Заменяет дефолтную back-стрелку. По умолчанию — Icons.arrow_back
  /// → context.pop(). На shell-tab (canPop=false) leading не показывается.
  final Widget? leading;

  /// Зарезервирован: куда уходить, если придумаем кнопку back на shell-tab.
  /// Сейчас не используется (canPop=false → leading=null).
  final String backFallbackPath;

  final PreferredSizeWidget? bottom;

  @override
  Size get preferredSize => Size.fromHeight(
        kToolbarHeight + (bottom?.preferredSize.height ?? 0),
      );

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final canPop = GoRouter.of(context).canPop();
    // Если есть custom leading — используем его. Иначе:
    // - canPop=true (push сюда) → arrow_back с context.pop()
    // - canPop=false (shell-tab или initial-route) → ничего, чистый header
    final Widget? effectiveLeading = leading ??
        (canPop
            ? IconButton(
                icon: const Icon(Icons.arrow_back),
                tooltip: 'Назад',
                onPressed: () => context.pop(),
              )
            : backFallbackPath.isNotEmpty
                ? IconButton(
                    icon: const Icon(Icons.arrow_back),
                    tooltip: 'Назад',
                    onPressed: () => GoRouter.of(context).go(backFallbackPath),
                  )
                : null);

    return AppBar(
      backgroundColor: Colors.transparent,
      surfaceTintColor: Colors.transparent,
      elevation: 0,
      scrolledUnderElevation: 0,
      leading: effectiveLeading,
      title: title,
      titleTextStyle: theme.textTheme.titleLarge,
      centerTitle: false,
      actions: actions,
      bottom: bottom,
    );
  }
}
