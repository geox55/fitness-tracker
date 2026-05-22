// Декоративный фон в стиле «двух порталов» — для auth-экранов.
//
// Два больших размытых круга разного цвета (portal-blue + aperture-orange),
// расположенных в противоположных углах, медленно пульсируют по opacity и
// чуть-чуть дышат по позиции. Накладывается под form-card'у на login и
// register-экранах. CustomPaint + AnimationController, без сторонних
// картинок.

import 'dart:math' as math;
import 'dart:ui';

import 'package:flutter/material.dart';

import '../theme/app_colors.dart';

class PortalBackdrop extends StatefulWidget {
  const PortalBackdrop({
    super.key,
    required this.child,
    this.intensity = 1.0,
  });
  final Widget child;

  /// 1.0 — полный «hero» эффект (auth-экраны), 0.4 — «muted» (главная и т. п.).
  final double intensity;

  @override
  State<PortalBackdrop> createState() => _PortalBackdropState();
}

class _PortalBackdropState extends State<PortalBackdrop>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 8),
    )..repeat();
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Stack(
      fit: StackFit.expand,
      children: [
        ColoredBox(color: theme.colorScheme.surface),
        // Двойной portal-glow на фоне.
        AnimatedBuilder(
          animation: _ctrl,
          builder: (context, _) {
            final t = _ctrl.value;
            // Лёгкая пульсация opacity (0.6..1.0) и микро-сдвиг.
            final pulse = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(t * 2 * math.pi));
            return CustomPaint(
              painter: _PortalBlobsPainter(
                pulse: pulse,
                phase: t,
                blueColor: AppPalette.primary,
                orangeColor: AppPalette.secondary,
                intensity: widget.intensity,
              ),
              child: const SizedBox.expand(),
            );
          },
        ),
        // Subtle diagonal warning-stripes (~4% opacity).
        CustomPaint(
          painter: _DiagonalStripesPainter(
            color: theme.colorScheme.onSurface.withValues(alpha: 0.04),
          ),
          child: const SizedBox.expand(),
        ),
        widget.child,
      ],
    );
  }
}

class _PortalBlobsPainter extends CustomPainter {
  _PortalBlobsPainter({
    required this.pulse,
    required this.phase,
    required this.blueColor,
    required this.orangeColor,
    required this.intensity,
  });

  final double pulse;
  final double phase;
  final Color blueColor;
  final Color orangeColor;
  final double intensity;

  @override
  void paint(Canvas canvas, Size size) {
    // Дыхание: ±8 px по обеим осям, фаза против-фаза для blue/orange.
    final breathBlue = Offset(
      math.sin(phase * 2 * math.pi) * 8,
      math.cos(phase * 2 * math.pi) * 8,
    );
    final breathOrange = -breathBlue;

    final blueBlob = Paint()
      ..color = blueColor.withValues(alpha: 0.28 * pulse * intensity)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 120);
    canvas.drawCircle(
      Offset(size.width * 0.18, size.height * 0.20) + breathBlue,
      math.min(size.width, size.height) * 0.42,
      blueBlob,
    );

    final orangeBlob = Paint()
      ..color = orangeColor.withValues(alpha: 0.22 * pulse * intensity)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 140);
    canvas.drawCircle(
      Offset(size.width * 0.85, size.height * 0.85) + breathOrange,
      math.min(size.width, size.height) * 0.38,
      orangeBlob,
    );
  }

  @override
  bool shouldRepaint(covariant _PortalBlobsPainter old) =>
      old.pulse != pulse ||
      old.phase != phase ||
      old.intensity != intensity;
}

class _DiagonalStripesPainter extends CustomPainter {
  _DiagonalStripesPainter({required this.color});
  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = 1
      ..style = PaintingStyle.stroke;
    const step = 14.0;
    // Диагональные линии под углом 45°.
    for (var x = -size.height; x < size.width; x += step) {
      canvas.drawLine(
        Offset(x, 0),
        Offset(x + size.height, size.height),
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant _DiagonalStripesPainter old) =>
      old.color != color;
}

/// Liquid Glass-карточка (вдохновлено Apple Liquid Glass из iOS 26).
///
/// Многослойный композит:
///   1) BackdropFilter blur 28 + saturate-ish tint (полупрозрачный surface);
///   2) Specular highlight сверху — тонкая лента blue-tinted alpha gradient,
///      имитирует «блик» на изогнутой поверхности;
///   3) Inner glow по нижней грани — orange-tinted alpha gradient, как
///      слабое refracted отражение второго портала;
///   4) Gradient stroke (border) — sweep blue → transparent → orange,
///      даёт ощущение «преломления света по контуру стекла»;
///   5) Лёгкая «noise»-текстура (диагональные hairline-линии 1.5% opacity)
///      — антибандинг + чуть-чуть «матовости».
class GlassCard extends StatelessWidget {
  const GlassCard({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.all(24),
    this.tintColor,
    this.borderRadius = 22,
  });

  final Widget child;
  final EdgeInsetsGeometry padding;
  final Color? tintColor;
  final double borderRadius;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final radius = BorderRadius.circular(borderRadius);
    return ClipRRect(
      borderRadius: radius,
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 28, sigmaY: 28),
        child: Stack(
          children: [
            // Базовый полупрозрачный fill.
            Positioned.fill(
              child: DecoratedBox(
                decoration: BoxDecoration(
                  color: theme.colorScheme.surfaceContainerHigh
                      .withValues(alpha: 0.42),
                ),
              ),
            ),
            // Specular highlight: светлая лента у верхней грани.
            Positioned.fill(
              child: DecoratedBox(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.center,
                    colors: [
                      Colors.white.withValues(alpha: 0.10),
                      Colors.white.withValues(alpha: 0.0),
                    ],
                  ),
                ),
              ),
            ),
            // Refracted glow снизу — портально-оранжевый.
            Positioned.fill(
              child: DecoratedBox(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.center,
                    end: Alignment.bottomCenter,
                    colors: [
                      Colors.transparent,
                      AppPalette.secondary.withValues(alpha: 0.06),
                    ],
                  ),
                ),
              ),
            ),
            // Тонкая «matte»-текстура (диагональные линии 1.5%).
            Positioned.fill(
              child: IgnorePointer(
                child: CustomPaint(
                  painter: _MicroGrainPainter(
                    color: theme.colorScheme.onSurface.withValues(alpha: 0.015),
                  ),
                ),
              ),
            ),
            // Контент.
            Padding(padding: padding, child: child),
            // Gradient stroke — «преломление по контуру».
            Positioned.fill(
              child: IgnorePointer(
                child: DecoratedBox(
                  decoration: BoxDecoration(
                    borderRadius: radius,
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [
                        (tintColor ?? AppPalette.primary)
                            .withValues(alpha: 0.45),
                        Colors.white.withValues(alpha: 0.06),
                        AppPalette.secondary.withValues(alpha: 0.30),
                      ],
                      stops: const [0.0, 0.5, 1.0],
                    ),
                  ),
                  position: DecorationPosition.foreground,
                  child: _BorderMask(radius: radius),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Маска, оставляющая видимым только тонкий ободок шириной 1px поверх
/// градиента — даёт эффект «преломлённого по контуру стекла». Внутри —
/// прозрачно, снаружи — обрезано родительским ClipRRect.
class _BorderMask extends StatelessWidget {
  const _BorderMask({required this.radius});
  final BorderRadius radius;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.all(1),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.all(
          Radius.circular(radius.topLeft.x - 1),
        ),
        color: const Color(0xFF000000),
        backgroundBlendMode: BlendMode.dstOut,
      ),
    );
  }
}

class _MicroGrainPainter extends CustomPainter {
  _MicroGrainPainter({required this.color});
  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = 0.7
      ..style = PaintingStyle.stroke;
    const step = 3.5;
    for (var x = -size.height; x < size.width; x += step) {
      canvas.drawLine(
        Offset(x, 0),
        Offset(x + size.height, size.height),
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant _MicroGrainPainter old) => old.color != color;
}
