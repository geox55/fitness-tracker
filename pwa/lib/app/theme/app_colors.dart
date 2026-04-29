import 'package:flutter/material.dart';

/// Цветовая палитра из дизайна (см. docs/design/screenshots/screen-09.png).
///
/// Базовые токены — независимы от темы. Производные цвета (фон/текст) живут
/// в [AppColorScheme] и переопределяются для светлой/тёмной тем.
abstract final class AppPalette {
  // Brand
  static const Color primary = Color(0xFF7F0DF2);
  static const Color primarySoft = Color(0xFF9F4DF8);
  static const Color primaryDeep = Color(0xFF5A09AB);

  // Status
  static const Color success = Color(0xFF22C55E);
  static const Color warning = Color(0xFFF59E0B);
  static const Color danger = Color(0xFFEF4444);

  // Greyscale (для тёмной темы)
  static const Color black = Color(0xFF0A0A0A);
  static const Color surfaceDark = Color(0xFF16111D);
  static const Color surfaceDarkElevated = Color(0xFF1E1726);
  static const Color borderDark = Color(0xFF2A2333);

  // Greyscale (для светлой темы)
  static const Color white = Color(0xFFFFFFFF);
  static const Color surfaceLight = Color(0xFFF8F7FB);
  static const Color surfaceLightElevated = Color(0xFFFFFFFF);
  static const Color borderLight = Color(0xFFE5E1EE);

  // Text — нейтральные оттенки
  static const Color textOnDarkPrimary = Color(0xFFFFFFFF);
  static const Color textOnDarkSecondary = Color(0xFFA0A0AF);
  static const Color textOnDarkMuted = Color(0xFF6B6678);

  static const Color textOnLightPrimary = Color(0xFF0F0E14);
  static const Color textOnLightSecondary = Color(0xFF55525F);
  static const Color textOnLightMuted = Color(0xFF8B8794);
}
