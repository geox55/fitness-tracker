import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../data/sync/sync_worker.dart';
import 'branding/portal_backdrop.dart';
import 'l10n/generated/app_localizations.dart';
import 'router.dart';
import 'theme/app_theme.dart';

class FitnessTrackerApp extends ConsumerWidget {
  const FitnessTrackerApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);
    // spec 015 M2.4: создание SyncWorker'а триггерит подписку на
    // ConnectivityListener и периодический drain очереди. Безопасно
    // вызывать на холодном старте — пустая очередь = no-op.
    ref.watch(syncWorkerProvider);

    return MaterialApp.router(
      onGenerateTitle: (context) => AppLocalizations.of(context).appName,
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light(),
      darkTheme: AppTheme.dark(),
      themeMode: ThemeMode.dark,
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      routerConfig: router,
      // Глобальный PortalBackdrop за всеми экранами:
      // - intensity=1.0 на /login и /register (hero, как в первой версии);
      // - intensity=0.4 на остальных страницах (приглушённый фон).
      // На светлой теме фон чистый — Portal только для dark mode.
      builder: (context, child) {
        final isDark = Theme.of(context).brightness == Brightness.dark;
        final content = child ?? const SizedBox.shrink();
        if (!isDark) return content;
        return _RouteAwarePortalBackdrop(router: router, child: content);
      },
    );
  }
}

/// Подписывается на изменение location'а GoRouter и подкручивает
/// `intensity` PortalBackdrop'а в зависимости от текущего пути:
/// auth-экраны получают полный hero-эффект (1.0), остальные — 0.4.
class _RouteAwarePortalBackdrop extends StatefulWidget {
  const _RouteAwarePortalBackdrop({required this.router, required this.child});

  final GoRouter router;
  final Widget child;

  @override
  State<_RouteAwarePortalBackdrop> createState() =>
      _RouteAwarePortalBackdropState();
}

class _RouteAwarePortalBackdropState extends State<_RouteAwarePortalBackdrop> {
  @override
  void initState() {
    super.initState();
    widget.router.routerDelegate.addListener(_onRouteChange);
  }

  @override
  void dispose() {
    widget.router.routerDelegate.removeListener(_onRouteChange);
    super.dispose();
  }

  void _onRouteChange() {
    if (mounted) setState(() {});
  }

  bool _isAuthRoute(String path) =>
      path.startsWith('/login') ||
      path.startsWith('/register') ||
      path.startsWith('/auth');

  @override
  Widget build(BuildContext context) {
    final path =
        widget.router.routerDelegate.currentConfiguration.uri.path;
    final intensity = _isAuthRoute(path) ? 1.0 : 0.4;
    return PortalBackdrop(intensity: intensity, child: widget.child);
  }
}
