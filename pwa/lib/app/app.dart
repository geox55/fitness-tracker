import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'branding/portal_backdrop.dart';
import 'l10n/generated/app_localizations.dart';
import 'router.dart';
import 'theme/app_theme.dart';

class FitnessTrackerApp extends ConsumerWidget {
  const FitnessTrackerApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);

    return MaterialApp.router(
      onGenerateTitle: (context) => AppLocalizations.of(context).appName,
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light(),
      darkTheme: AppTheme.dark(),
      themeMode: ThemeMode.dark,
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      routerConfig: router,
      // Глобальный PortalBackdrop за всеми экранами: даёт animated
      // portal-blobs (приглушённые, intensity=0.4) + diagonal stripes.
      // На светлой теме оставляем чистый surface — Portal-эстетика только
      // для dark mode (основной режим приложения).
      builder: (context, child) {
        final isDark = Theme.of(context).brightness == Brightness.dark;
        final content = child ?? const SizedBox.shrink();
        if (!isDark) return content;
        return PortalBackdrop(intensity: 0.4, child: content);
      },
    );
  }
}
