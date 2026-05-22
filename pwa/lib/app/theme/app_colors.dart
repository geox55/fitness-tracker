import 'package:flutter/material.dart';

/// Палитра «Athletic Dark + Portal Blue / Aperture Orange» —
/// стилизация, отсылающая к Aperture Science (вселенная Portal).
///
/// Принципы:
/// - фон **нейтральный** (без примеси винного/баклажанового): чистый
///   почти-чёрный, чтобы portal-blue «выстреливал»;
/// - **двухцветный акцент**: portal-blue — основной CTA, portal-orange —
///   декоративный (glow на login-экране, акцент на иконке);
/// - hairline-границы вместо теней (Flutter web рендерит дешевле и
///   выглядит современнее, чем layered shadows).
///
/// Все производные цвета — в [AppTheme] через ColorScheme; здесь только
/// палитра-источник.
abstract final class AppPalette {
  // ---------- Brand: portal blue (primary) ---------------------------------
  // 0EA5E9 — Tailwind sky-500. Электрик-голубой, «луч» синего портала.
  // Контраст AA на 16 pt+ против darkBg.
  static const Color primary = Color(0xFF0EA5E9);
  static const Color primarySoft = Color(0xFF38BDF8); // sky-400, hover/glow
  static const Color primaryDeep = Color(0xFF0284C7); // sky-600, pressed
  static const Color primaryTint = Color(0x230EA5E9); // ~14% alpha — tonal

  // ---------- Brand: aperture orange (secondary) ---------------------------
  // F97316 — Tailwind orange-500. «Оранжевый портал». Декоративный
  // вторичный акцент: glow, иконка-аккомпанемент, лента CI на графиках.
  static const Color secondary = Color(0xFFF97316);
  static const Color secondarySoft = Color(0xFFFB923C); // orange-400
  static const Color secondaryDeep = Color(0xFFC2410C); // orange-700

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
    Color(0xFF0EA5E9), // portal-blue (sky-500) — primary
    Color(0xFFF97316), // portal-orange (orange-500) — secondary
    Color(0xFF22D3EE), // cyan
    Color(0xFF22C55E), // green
    Color(0xFFF472B6), // pink
    Color(0xFFFBBF24), // amber
    Color(0xFF94A3B8), // slate
    Color(0xFF38BDF8), // sky-400 (forecast CI overlay)
  ];
}

/// Декоративные акценты для тёмной темы. Не перекрывают основной фон,
/// а добавляют тонкий «ambient»-glow — как на login-скрине дизайн-системы
/// (см. docs/design/screenshots/screen-09.png). Радиальный, у верхней
/// центральной точки, очень слабая alpha — без ущерба контрасту.
abstract final class AppGradients {
  static const RadialGradient darkAmbientGlow = RadialGradient(
    center: Alignment(0.0, -0.85),
    radius: 0.9,
    colors: [
      Color(0x3338BDF8), // ~20% sky-400 — portal-blue glow
      Color(0x00000000),
    ],
    stops: [0.0, 1.0],
  );

  // Двухпортальный glow: blue слева, orange справа — для login-экрана.
  static const LinearGradient portalBackdrop = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [
      Color(0x220EA5E9), // portal-blue
      Color(0x00000000),
      Color(0x22F97316), // aperture-orange
    ],
    stops: [0.0, 0.5, 1.0],
  );
}
