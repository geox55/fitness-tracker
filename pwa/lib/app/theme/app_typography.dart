import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Типографика по дизайн-системе (screen-09.png):
///   H1   Inter ExtraBold 48 / -0.05em
///   H2   Inter Bold      30 / -0.025em
///   Sub  Inter SemiBold  20
///   Body Inter Regular   16
///   Caption / Overline Inter Medium 10 / 0.1em
///
/// На реальных мобильных экранах H1=48 слишком крупный, в продуктовых местах
/// используем меньшие H заголовки (28..36); H1=48 — для маркетинговых блоков.
abstract final class AppTypography {
  static TextTheme textTheme(Brightness brightness) {
    final base = GoogleFonts.interTextTheme();
    return base.copyWith(
      // Маркетинговый огромный заголовок
      displayLarge: base.displayLarge?.copyWith(
        fontSize: 48,
        fontWeight: FontWeight.w800,
        letterSpacing: -2.4, // -0.05em
        height: 1.05,
      ),
      // Заголовок крупного экрана
      displayMedium: base.displayMedium?.copyWith(
        fontSize: 36,
        fontWeight: FontWeight.w700,
        letterSpacing: -0.9,
        height: 1.1,
      ),
      // H2 / экранные заголовки
      headlineLarge: base.headlineLarge?.copyWith(
        fontSize: 30,
        fontWeight: FontWeight.w700,
        letterSpacing: -0.75,
        height: 1.15,
      ),
      headlineMedium: base.headlineMedium?.copyWith(
        fontSize: 24,
        fontWeight: FontWeight.w700,
        height: 1.2,
      ),
      // Subheading
      titleLarge: base.titleLarge?.copyWith(
        fontSize: 20,
        fontWeight: FontWeight.w600,
        height: 1.3,
      ),
      titleMedium: base.titleMedium?.copyWith(
        fontSize: 18,
        fontWeight: FontWeight.w600,
        height: 1.3,
      ),
      titleSmall: base.titleSmall?.copyWith(
        fontSize: 16,
        fontWeight: FontWeight.w600,
        height: 1.3,
      ),
      // Body
      bodyLarge: base.bodyLarge?.copyWith(
        fontSize: 16,
        fontWeight: FontWeight.w400,
        height: 1.45,
      ),
      bodyMedium: base.bodyMedium?.copyWith(
        fontSize: 14,
        fontWeight: FontWeight.w400,
        height: 1.45,
      ),
      bodySmall: base.bodySmall?.copyWith(
        fontSize: 12,
        fontWeight: FontWeight.w400,
        height: 1.45,
      ),
      // Caption / button label
      labelLarge: base.labelLarge?.copyWith(
        fontSize: 14,
        fontWeight: FontWeight.w600,
        letterSpacing: 0.2,
      ),
      labelMedium: base.labelMedium?.copyWith(
        fontSize: 12,
        fontWeight: FontWeight.w500,
        letterSpacing: 0.5,
      ),
      // Overline (UPPERCASE caption)
      labelSmall: base.labelSmall?.copyWith(
        fontSize: 10,
        fontWeight: FontWeight.w500,
        letterSpacing: 1.0,
      ),
    );
  }
}
