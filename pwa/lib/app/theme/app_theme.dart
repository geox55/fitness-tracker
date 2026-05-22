import 'package:flutter/material.dart';

import 'app_colors.dart';
import 'app_spacing.dart';
import 'app_typography.dart';

/// Тема приложения — «Athletic Dark + Electric Violet».
///
/// Решения по компонентам:
/// - Карточки: flat fill + hairline border, `elevation: 0`. Тени уходят
///   совсем: на Flutter web blur-shadow тормозят и выглядят винтажно.
/// - Кнопки: 56dp high, 14px radius. Primary = filled violet, Secondary =
///   surfaceElevated с тонким бордером, Text = просто текст с violet'ом.
/// - Чипы: full-pill, filled-style. Selected = violet fill + чёрный текст
///   (контраст AA на ярком фоне).
/// - InputField: 16px radius, filled, фокус-кольцо в violet.
/// - NavBar: surfaceElevated с тонкой границей сверху, indicator — tint
///   primary (не сплошная плашка).
abstract final class AppTheme {
  static ThemeData light() => _buildTheme(_lightScheme);
  static ThemeData dark() => _buildTheme(_darkScheme);

  // ---------------------------------------------------------------------
  // ColorScheme
  // ---------------------------------------------------------------------

  static const ColorScheme _darkScheme = ColorScheme(
    brightness: Brightness.dark,
    primary: AppPalette.primary,
    onPrimary: AppPalette.textOnDarkPrimary,
    primaryContainer: AppPalette.primaryDeep,
    onPrimaryContainer: AppPalette.textOnDarkPrimary,
    secondary: AppPalette.primarySoft,
    onSecondary: AppPalette.darkBg,
    secondaryContainer: AppPalette.primaryTint,
    onSecondaryContainer: AppPalette.primarySoft,
    tertiary: AppPalette.primarySoft,
    onTertiary: AppPalette.darkBg,
    error: AppPalette.danger,
    onError: AppPalette.textOnDarkPrimary,
    surface: AppPalette.darkSurface,
    onSurface: AppPalette.textOnDarkPrimary,
    surfaceContainerLowest: AppPalette.darkBg,
    surfaceContainerLow: AppPalette.darkSurface,
    surfaceContainer: AppPalette.darkSurface,
    surfaceContainerHigh: AppPalette.darkSurfaceElevated,
    surfaceContainerHighest: AppPalette.darkSurfaceElevated,
    onSurfaceVariant: AppPalette.textOnDarkSecondary,
    outline: AppPalette.darkBorder,
    outlineVariant: AppPalette.darkBorderStrong,
  );

  static const ColorScheme _lightScheme = ColorScheme(
    brightness: Brightness.light,
    primary: AppPalette.primary,
    onPrimary: AppPalette.lightSurface,
    primaryContainer: Color(0xFFEDE3FE),
    onPrimaryContainer: AppPalette.primaryDeep,
    secondary: AppPalette.primarySoft,
    onSecondary: AppPalette.lightSurface,
    secondaryContainer: Color(0xFFF3EDFF),
    onSecondaryContainer: AppPalette.primaryDeep,
    tertiary: AppPalette.primarySoft,
    onTertiary: AppPalette.lightSurface,
    error: AppPalette.danger,
    onError: AppPalette.lightSurface,
    surface: AppPalette.lightBg,
    onSurface: AppPalette.textOnLightPrimary,
    surfaceContainerLowest: AppPalette.lightSurface,
    surfaceContainerLow: AppPalette.lightSurface,
    surfaceContainer: AppPalette.lightSurface,
    surfaceContainerHigh: AppPalette.lightSurface,
    surfaceContainerHighest: AppPalette.lightSurface,
    onSurfaceVariant: AppPalette.textOnLightSecondary,
    outline: AppPalette.lightBorder,
    outlineVariant: AppPalette.lightBorderStrong,
  );

  // ---------------------------------------------------------------------
  // Theme builder
  // ---------------------------------------------------------------------

  static ThemeData _buildTheme(ColorScheme scheme) {
    final isDark = scheme.brightness == Brightness.dark;
    final base = AppTypography.textTheme(scheme.brightness);
    final textTheme = base.apply(
      bodyColor: scheme.onSurface,
      displayColor: scheme.onSurface,
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      // Dark — прозрачный scaffold: под ним лежит глобальный PortalBackdrop
      // (см. app.dart::builder). Light — чистый surface как и было.
      scaffoldBackgroundColor: isDark ? Colors.transparent : scheme.surface,
      textTheme: textTheme,
      // Глобальный splash — приглушаем «лужу» Material на тапах, оставляем
      // только лёгкий hover/pressed (на web это нативное поведение карт).
      splashFactory: NoSplash.splashFactory,
      highlightColor: Colors.transparent,

      // -------- Карточки -------------------------------------------------
      cardTheme: CardThemeData(
        color: scheme.surfaceContainerHigh,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        margin: EdgeInsets.zero,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppRadius.xl),
          side: BorderSide(color: scheme.outline),
        ),
      ),

      // -------- Поля ввода ------------------------------------------------
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: isDark
            ? AppPalette.darkSurfaceElevated
            : AppPalette.lightSurface,
        contentPadding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.lg,
          vertical: AppSpacing.lg,
        ),
        hintStyle: textTheme.bodyMedium?.copyWith(
          color: isDark
              ? AppPalette.textOnDarkMuted
              : AppPalette.textOnLightMuted,
        ),
        labelStyle: textTheme.bodyMedium,
        floatingLabelStyle: textTheme.bodyMedium?.copyWith(
          color: scheme.primary,
          fontWeight: FontWeight.w600,
        ),
        prefixIconColor: scheme.onSurfaceVariant,
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
          borderSide: BorderSide(color: scheme.error, width: 1.2),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppRadius.lg),
          borderSide: BorderSide(color: scheme.error, width: 1.5),
        ),
      ),

      // -------- Primary CTA ----------------------------------------------
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: scheme.primary,
          foregroundColor: scheme.onPrimary,
          disabledBackgroundColor: scheme.primary.withValues(alpha: 0.4),
          disabledForegroundColor: scheme.onPrimary.withValues(alpha: 0.7),
          textStyle: textTheme.labelLarge,
          minimumSize: const Size.fromHeight(56),
          padding: const EdgeInsets.symmetric(horizontal: AppSpacing.xxl),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppRadius.lg),
          ),
          elevation: 0,
          shadowColor: Colors.transparent,
        ),
      ),

      // -------- Secondary / outlined --------------------------------------
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: scheme.onSurface,
          backgroundColor: isDark
              ? AppPalette.darkSurfaceElevated
              : AppPalette.lightSurface,
          side: BorderSide(color: scheme.outline),
          textStyle: textTheme.labelLarge,
          minimumSize: const Size.fromHeight(56),
          padding: const EdgeInsets.symmetric(horizontal: AppSpacing.xxl),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppRadius.lg),
          ),
        ),
      ),

      // -------- Tertiary (text-only) -------------------------------------
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: scheme.primary,
          textStyle: textTheme.labelLarge,
          padding: const EdgeInsets.symmetric(
            horizontal: AppSpacing.md,
            vertical: AppSpacing.sm,
          ),
        ),
      ),

      // -------- Chips -----------------------------------------------------
      chipTheme: ChipThemeData(
        backgroundColor: scheme.surfaceContainerHigh,
        selectedColor: scheme.primary,
        secondarySelectedColor: scheme.primary,
        disabledColor: scheme.surfaceContainerHigh.withValues(alpha: 0.5),
        labelStyle: textTheme.labelMedium!.copyWith(color: scheme.onSurface),
        secondaryLabelStyle: textTheme.labelMedium!.copyWith(
          color: scheme.onPrimary,
          fontWeight: FontWeight.w700,
        ),
        side: BorderSide.none,
        shape: const StadiumBorder(),
        padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.md,
          vertical: AppSpacing.sm,
        ),
        showCheckmark: false,
      ),

      // -------- Bottom navigation ----------------------------------------
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: isDark
            ? AppPalette.darkSurfaceElevated
            : AppPalette.lightSurface,
        indicatorColor: scheme.primary.withValues(alpha: 0.18),
        surfaceTintColor: Colors.transparent,
        labelTextStyle: WidgetStateProperty.resolveWith(
          (states) => textTheme.labelMedium!.copyWith(
            color: states.contains(WidgetState.selected)
                ? scheme.primary
                : scheme.onSurfaceVariant,
            fontWeight: states.contains(WidgetState.selected)
                ? FontWeight.w700
                : FontWeight.w600,
          ),
        ),
        iconTheme: WidgetStateProperty.resolveWith(
          (states) => IconThemeData(
            color: states.contains(WidgetState.selected)
                ? scheme.primary
                : scheme.onSurfaceVariant,
            size: 24,
          ),
        ),
        height: 72,
        elevation: 0,
      ),

      // -------- FAB -------------------------------------------------------
      floatingActionButtonTheme: FloatingActionButtonThemeData(
        backgroundColor: scheme.primary,
        foregroundColor: scheme.onPrimary,
        elevation: 0,
        focusElevation: 0,
        hoverElevation: 0,
        highlightElevation: 0,
        shape: const StadiumBorder(),
      ),

      // -------- App bar ---------------------------------------------------
      appBarTheme: AppBarTheme(
        backgroundColor: Colors.transparent,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: false,
        titleTextStyle: textTheme.titleLarge?.copyWith(
          fontWeight: FontWeight.w700,
        ),
        iconTheme: IconThemeData(color: scheme.onSurface),
      ),

      // -------- Divider ---------------------------------------------------
      dividerTheme: DividerThemeData(
        color: scheme.outline,
        thickness: 1,
        space: 1,
      ),

      // -------- SnackBar --------------------------------------------------
      snackBarTheme: SnackBarThemeData(
        backgroundColor: isDark
            ? AppPalette.darkSurfaceElevated
            : AppPalette.textOnLightPrimary,
        contentTextStyle: textTheme.bodyMedium?.copyWith(
          color: isDark
              ? AppPalette.textOnDarkPrimary
              : AppPalette.lightSurface,
        ),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppRadius.md),
        ),
      ),

      // -------- Switch / Checkbox / Radio --------------------------------
      switchTheme: SwitchThemeData(
        trackColor: WidgetStateProperty.resolveWith(
          (s) => s.contains(WidgetState.selected)
              ? scheme.primary
              : scheme.surfaceContainerHigh,
        ),
        thumbColor: const WidgetStatePropertyAll(Colors.white),
        trackOutlineColor: WidgetStateProperty.resolveWith(
          (s) => s.contains(WidgetState.selected)
              ? scheme.primary
              : scheme.outline,
        ),
      ),
      checkboxTheme: CheckboxThemeData(
        fillColor: WidgetStateProperty.resolveWith(
          (s) => s.contains(WidgetState.selected)
              ? scheme.primary
              : Colors.transparent,
        ),
        checkColor: const WidgetStatePropertyAll(Colors.white),
        side: BorderSide(color: scheme.outline, width: 1.5),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppRadius.sm / 2),
        ),
      ),
      radioTheme: RadioThemeData(
        fillColor: WidgetStateProperty.resolveWith(
          (s) => s.contains(WidgetState.selected)
              ? scheme.primary
              : scheme.outline,
        ),
      ),

      // -------- Progress indicator ---------------------------------------
      progressIndicatorTheme: ProgressIndicatorThemeData(
        color: scheme.primary,
        linearTrackColor: scheme.surfaceContainerHigh,
        circularTrackColor: scheme.surfaceContainerHigh,
      ),

      // -------- Bottom sheet / dialog ------------------------------------
      bottomSheetTheme: BottomSheetThemeData(
        backgroundColor: scheme.surfaceContainerHigh,
        surfaceTintColor: Colors.transparent,
        modalBackgroundColor: scheme.surfaceContainerHigh,
        elevation: 0,
        modalElevation: 0,
        showDragHandle: true,
        dragHandleColor: scheme.outline,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(
            top: Radius.circular(AppRadius.xl),
          ),
        ),
      ),
      dialogTheme: DialogThemeData(
        backgroundColor: scheme.surfaceContainerHigh,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppRadius.xl),
        ),
      ),
    );
  }
}
