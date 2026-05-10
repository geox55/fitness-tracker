import 'package:flutter/material.dart';

import 'app_colors.dart';
import 'app_spacing.dart';
import 'app_typography.dart';

abstract final class AppTheme {
  static ThemeData light() => _buildTheme(_lightScheme);
  static ThemeData dark() => _buildTheme(_darkScheme);

  static const ColorScheme _darkScheme = ColorScheme(
    brightness: Brightness.dark,
    primary: AppPalette.primary,
    onPrimary: AppPalette.white,
    primaryContainer: AppPalette.primaryDeep,
    onPrimaryContainer: AppPalette.white,
    secondary: AppPalette.primarySoft,
    onSecondary: AppPalette.white,
    error: AppPalette.danger,
    onError: AppPalette.white,
    surface: AppPalette.surfaceDark,
    onSurface: AppPalette.textOnDarkPrimary,
    surfaceContainerLowest: AppPalette.black,
    surfaceContainerLow: AppPalette.surfaceDark,
    surfaceContainer: AppPalette.surfaceDark,
    surfaceContainerHigh: AppPalette.surfaceDarkElevated,
    surfaceContainerHighest: AppPalette.surfaceDarkElevated,
    onSurfaceVariant: AppPalette.textOnDarkSecondary,
    outline: AppPalette.borderDark,
    outlineVariant: AppPalette.borderDark,
  );

  static const ColorScheme _lightScheme = ColorScheme(
    brightness: Brightness.light,
    primary: AppPalette.primary,
    onPrimary: AppPalette.white,
    primaryContainer: Color(0xFFEDE3FE),
    onPrimaryContainer: AppPalette.primaryDeep,
    secondary: AppPalette.primarySoft,
    onSecondary: AppPalette.white,
    error: AppPalette.danger,
    onError: AppPalette.white,
    surface: AppPalette.surfaceLight,
    onSurface: AppPalette.textOnLightPrimary,
    surfaceContainerLowest: AppPalette.white,
    surfaceContainerLow: AppPalette.surfaceLightElevated,
    surfaceContainer: AppPalette.surfaceLightElevated,
    surfaceContainerHigh: AppPalette.white,
    surfaceContainerHighest: AppPalette.white,
    onSurfaceVariant: AppPalette.textOnLightSecondary,
    outline: AppPalette.borderLight,
    outlineVariant: AppPalette.borderLight,
  );

  static ThemeData _buildTheme(ColorScheme scheme) {
    final isDark = scheme.brightness == Brightness.dark;
    final textTheme = AppTypography.textTheme(scheme.brightness).apply(
      bodyColor: scheme.onSurface,
      displayColor: scheme.onSurface,
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      // Дизайн-система Fitness OS v1.0: фон solid #0A0A0A на тёмной теме,
      // никаких диагональных градиентов (они перегружают экран и плохо
      // сочетаются с purple-акцентами). Тонкий ambient-glow добавлен
      // отдельным слоем в MaterialApp.builder.
      scaffoldBackgroundColor: isDark ? AppPalette.black : AppPalette.surfaceLight,
      textTheme: textTheme,
      // Карточки, контейнеры
      cardTheme: CardThemeData(
        color: scheme.surfaceContainerHigh,
        elevation: 0,
        margin: EdgeInsets.zero,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppRadius.lg),
          side: BorderSide(color: scheme.outline),
        ),
      ),
      // Поля ввода
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: isDark ? AppPalette.surfaceDarkElevated : AppPalette.white,
        contentPadding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.lg,
          vertical: AppSpacing.lg,
        ),
        hintStyle: textTheme.bodyMedium?.copyWith(
          color: isDark ? AppPalette.textOnDarkMuted : AppPalette.textOnLightMuted,
        ),
        labelStyle: textTheme.bodyMedium,
        prefixIconColor: scheme.primary,
        suffixIconColor: scheme.onSurfaceVariant,
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppRadius.lg),
          borderSide: BorderSide(color: scheme.outline),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppRadius.lg),
          borderSide: BorderSide(color: scheme.primary, width: 1.5),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppRadius.lg),
          borderSide: BorderSide(color: scheme.error),
        ),
      ),
      // Primary CTA — solid purple, ALLCAPS letterspaced, edge-to-edge.
      // Из дизайн-системы: «START WORKOUT ▷» — кнопка плотная, текст
      // labelLarge с tracking 0.8; небольшой elevation даёт purple-glow
      // снизу, что в дизайне отчётливо видно.
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: scheme.primary,
          foregroundColor: scheme.onPrimary,
          textStyle: textTheme.labelLarge?.copyWith(letterSpacing: 0.8),
          minimumSize: const Size.fromHeight(52),
          padding: const EdgeInsets.symmetric(horizontal: AppSpacing.xxl),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppRadius.lg),
          ),
          elevation: isDark ? 8 : 4,
          shadowColor: scheme.primary.withValues(alpha: 0.45),
        ),
      ),
      // Outlined — тонкий purple border, такой же ALLCAPS-tracking текст.
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: scheme.primary,
          side: BorderSide(color: scheme.primary, width: 1.4),
          textStyle: textTheme.labelLarge?.copyWith(letterSpacing: 0.8),
          minimumSize: const Size.fromHeight(52),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppRadius.lg),
          ),
        ),
      ),
      // Text-only
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: scheme.primary,
          textStyle: textTheme.labelLarge,
        ),
      ),
      // Bottom nav
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: isDark ? AppPalette.surfaceDark : AppPalette.white,
        indicatorColor: scheme.primary.withValues(alpha: 0.16),
        labelTextStyle: WidgetStatePropertyAll(textTheme.labelMedium),
        iconTheme: WidgetStateProperty.resolveWith(
          (states) => IconThemeData(
            color: states.contains(WidgetState.selected)
                ? scheme.primary
                : scheme.onSurfaceVariant,
          ),
        ),
        height: 72,
      ),
      // FAB
      floatingActionButtonTheme: FloatingActionButtonThemeData(
        backgroundColor: scheme.primary,
        foregroundColor: scheme.onPrimary,
        elevation: 4,
        shape: const CircleBorder(),
      ),
      // App bar
      appBarTheme: AppBarTheme(
        backgroundColor: Colors.transparent,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: true,
        titleTextStyle: textTheme.titleLarge,
        iconTheme: IconThemeData(color: scheme.onSurface),
      ),
    );
  }
}
