import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Типографика «Space Grotesk» — гротеск с характером.
/// Особенно живая на цифрах (одноэтажная 4, выразительные 6/9) — идеально
/// для hero-метрик: «78.4 кг», «12 348 шагов».
///
/// Стратегия весов:
///   700 (bold)       — display-заголовки, hero-метрики
///   600 (semibold)   — H заголовки, section titles, button labels
///   500 (medium)     — body, chips
///   400 (regular)    — muted captions
///
/// Note: Space Grotesk начинается с 300, максимум 700 (нет 800). Везде,
/// где раньше был w800, используем w700 + чуть-более тугой letter-spacing.
///
/// `fontFeatures: [FontFeature.tabularFigures()]` — чтобы числа в столбце
/// графиков не «прыгали» при изменении значений.
abstract final class AppTypography {
  static const _tabular = [FontFeature.tabularFigures()];

  static TextTheme textTheme(Brightness brightness) {
    final base = GoogleFonts.spaceGroteskTextTheme();
    return base.copyWith(
      // Маркетинговый заголовок (auth-экраны, splash).
      displayLarge: base.displayLarge?.copyWith(
        fontSize: 48,
        fontWeight: FontWeight.w700,
        letterSpacing: -2.4,
        height: 1.0,
      ),
      // Hero-метрики на дашборде («78.4 кг», большое число).
      displayMedium: base.displayMedium?.copyWith(
        fontSize: 36,
        fontWeight: FontWeight.w700,
        letterSpacing: -1.1,
        height: 1.05,
        fontFeatures: _tabular,
      ),
      displaySmall: base.displaySmall?.copyWith(
        fontSize: 28,
        fontWeight: FontWeight.w700,
        letterSpacing: -0.4,
        height: 1.1,
        fontFeatures: _tabular,
      ),
      // Экранные H1 / большие section titles.
      headlineLarge: base.headlineLarge?.copyWith(
        fontSize: 26,
        fontWeight: FontWeight.w700,
        letterSpacing: -0.4,
        height: 1.2,
      ),
      headlineMedium: base.headlineMedium?.copyWith(
        fontSize: 22,
        fontWeight: FontWeight.w700,
        letterSpacing: -0.2,
        height: 1.2,
      ),
      headlineSmall: base.headlineSmall?.copyWith(
        fontSize: 18,
        fontWeight: FontWeight.w600,
        height: 1.3,
      ),
      // Subheadings, list titles.
      titleLarge: base.titleLarge?.copyWith(
        fontSize: 18,
        fontWeight: FontWeight.w600,
        height: 1.3,
      ),
      titleMedium: base.titleMedium?.copyWith(
        fontSize: 16,
        fontWeight: FontWeight.w600,
        height: 1.3,
      ),
      titleSmall: base.titleSmall?.copyWith(
        fontSize: 14,
        fontWeight: FontWeight.w600,
        height: 1.3,
      ),
      // Body.
      bodyLarge: base.bodyLarge?.copyWith(
        fontSize: 16,
        fontWeight: FontWeight.w500,
        height: 1.45,
      ),
      bodyMedium: base.bodyMedium?.copyWith(
        fontSize: 14,
        fontWeight: FontWeight.w500,
        height: 1.45,
      ),
      bodySmall: base.bodySmall?.copyWith(
        fontSize: 13,
        fontWeight: FontWeight.w400,
        height: 1.4,
      ),
      // Кнопки.
      labelLarge: base.labelLarge?.copyWith(
        fontSize: 15,
        fontWeight: FontWeight.w600,
        letterSpacing: 0.1,
      ),
      // Nav-bar labels, chip labels.
      labelMedium: base.labelMedium?.copyWith(
        fontSize: 12,
        fontWeight: FontWeight.w600,
        letterSpacing: 0.2,
      ),
      // Overline (UPPERCASE captions, badges).
      labelSmall: base.labelSmall?.copyWith(
        fontSize: 11,
        fontWeight: FontWeight.w600,
        letterSpacing: 0.8,
      ),
    );
  }
}
