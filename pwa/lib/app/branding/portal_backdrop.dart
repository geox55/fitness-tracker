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

  /// 1.0 — полный «hero» эффект (auth-экраны), 0.35 — приглушённо
  /// (главная и внутренние экраны).
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

/// Frosted glass-карточка для login/register: blur backdrop + полупрозрачный
/// fill + tinted border. Современная UI-фишка (glassmorphism).
class GlassCard extends StatelessWidget {
  const GlassCard({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.all(24),
    this.tintColor,
  });

  final Widget child;
  final EdgeInsetsGeometry padding;
  final Color? tintColor;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return ClipRRect(
      borderRadius: BorderRadius.circular(20),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 24, sigmaY: 24),
        child: Container(
          padding: padding,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(20),
            color: theme.colorScheme.surfaceContainerHigh.withValues(alpha: 0.55),
            border: Border.all(
              color: (tintColor ?? AppPalette.primary).withValues(alpha: 0.25),
            ),
          ),
          child: child,
        ),
      ),
    );
  }
}
