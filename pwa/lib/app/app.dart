import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'l10n/generated/app_localizations.dart';
import 'router.dart';
import 'theme/app_colors.dart';
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
      // Один градиент на всё приложение: Scaffold'ы прозрачные (см. theme),
      // фон отрисовывается здесь и не пересобирается при навигации между
      // экранами. SnackBar'ы и dialog'и продолжают работать поверх.
      builder: (context, child) {
        final isDark = Theme.of(context).brightness == Brightness.dark;
        return DecoratedBox(
          decoration: BoxDecoration(
            gradient: isDark
                ? AppGradients.darkAppBackground
                : AppGradients.lightAppBackground,
          ),
          child: child ?? const SizedBox.shrink(),
        );
      },
    );
  }
}
