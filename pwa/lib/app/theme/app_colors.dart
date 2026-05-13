import 'package:flutter/material.dart';

/// Палитра «Athletic Dark + Electric Violet» — фитнес-продукт уровня 2025.
///
/// Принципы:
/// - фон **нейтральный** (без примеси винного/баклажанового, как в старой
///   теме): чистый почти-чёрный, чтобы фиолет действительно «выстреливал»;
/// - **один** яркий violet — он же CTA, активный чип, акцент в графиках;
/// - hairline-границы вместо теней (Flutter web рендерит дешевле и выглядит
///   современнее, чем layered shadows).
///
/// Все производные цвета — в [AppTheme] через ColorScheme; здесь только
/// палитра-источник.
abstract final class AppPalette {
  // ---------- Brand: electric violet ---------------------------------------
  // 8B5CF6 — Tailwind violet-500. Точка попадает по контрасту с почти-
  // чёрным фоном (AA на 16 pt+), и при этом не «слепит» на больших площадях.
  static const Color primary = Color(0xFF8B5CF6);
  static const Color primarySoft = Color(0xFFA78BFA); // violet-400, hover/glow
  static const Color primaryDeep = Color(0xFF6D28D9); // violet-700, pressed
  // Чуть-разбавленный фиолет для tonal-fill (selected-chip background,
  // badges) — 14% алфа от primary в композитах, но прибит как const.
  static const Color primaryTint = Color(0x238B5CF6); // ~14% alpha

  // ---------- Status -------------------------------------------------------
  static const Color success = Color(0xFF22C55E);
  static const Color warning = Color(0xFFF59E0B);
  static const Color danger = Color(0xFFEF4444);

  // ---------- Dark theme (нейтральные, без винного оттенка) ----------------
  static const Color darkBg = Color(0xFF0A0A0F); // приложение
  static const Color darkSurface = Color(0xFF15151C); // карточка
  static const Color darkSurfaceElevated = Color(0xFF1C1C25); // модалка/нав
  static const Color darkBorder = Color(0xFF232330); // hairline
  static const Color darkBorderStrong = Color(0xFF2D2D3D); // выделенная

  // ---------- Light theme (cool off-white, парный со старым brand'ом) -----
  static const Color lightBg = Color(0xFFF6F6FA);
  static const Color lightSurface = Color(0xFFFFFFFF);
  static const Color lightSurfaceElevated = Color(0xFFFFFFFF);
  static const Color lightBorder = Color(0xFFE4E4EE);
  static const Color lightBorderStrong = Color(0xFFD1D1DD);

  // ---------- Text ---------------------------------------------------------
  // Контраст подобран под WCAG AA на соответствующих surface'ах.
  static const Color textOnDarkPrimary = Color(0xFFF5F5F8); // 16.4:1 на bg
  static const Color textOnDarkSecondary = Color(0xFFB4B4C2); // muted
  static const Color textOnDarkMuted = Color(0xFF8E8E9E); // labels
  static const Color textOnDarkDisabled = Color(0xFF5A5A6A);

  static const Color textOnLightPrimary = Color(0xFF15151C);
  static const Color textOnLightSecondary = Color(0xFF55555F);
  static const Color textOnLightMuted = Color(0xFF7E7E8A);
  static const Color textOnLightDisabled = Color(0xFFB8B8C2);

  // ---------- Data viz (8 серий, colorblind-aware) -------------------------
  // Для графиков InBody (вес/мышцы/жир/forecast overlay). Подобрано так,
  // чтобы violet был в начале (primary metric), а остальные не конфликтовали
  // ни с ним, ни друг с другом при печати/grayscale.
  static const List<Color> chartSeries = [
    Color(0xFF8B5CF6), // violet — primary
    Color(0xFF22D3EE), // cyan
    Color(0xFFFB923C), // orange
    Color(0xFF22C55E), // green
    Color(0xFFF472B6), // pink
    Color(0xFFFBBF24), // amber
    Color(0xFF94A3B8), // slate
    Color(0xFFA78BFA), // violet light (forecast overlay)
  ];
}
