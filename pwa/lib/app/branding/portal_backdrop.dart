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
        // Двойной portal-glow через RadialGradient (GPU-нативно, без
        // CPU MaskFilter.blur — на Flutter web в Skia он очень дорогой
        // и блочил main-thread при переключении страниц).
        // RepaintBoundary изолирует пере-paint анимации от контента.
        RepaintBoundary(
          child: AnimatedBuilder(
            animation: _ctrl,
            builder: (context, _) {
              final t = _ctrl.value;
              final pulse = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(t * 2 * math.pi));
              final breath = math.sin(t * 2 * math.pi);
              return Stack(
                fit: StackFit.expand,
                children: [
                  _Blob(
                    alignment: Alignment(-0.7 + 0.05 * breath, -0.65),
                    color: AppPalette.primary.withValues(
                      alpha: 0.32 * pulse * widget.intensity,
                    ),
                  ),
                  _Blob(
                    alignment: Alignment(0.75 - 0.05 * breath, 0.7),
                    color: AppPalette.secondary.withValues(
                      alpha: 0.26 * pulse * widget.intensity,
                    ),
                  ),
                ],
              );
            },
          ),
        ),
        // Subtle diagonal warning-stripes (~4% opacity).
        IgnorePointer(
          child: CustomPaint(
            painter: _DiagonalStripesPainter(
              color: theme.colorScheme.onSurface.withValues(alpha: 0.04),
            ),
            child: const SizedBox.expand(),
          ),
        ),
        widget.child,
      ],
    );
  }
}

class _Blob extends StatelessWidget {
  const _Blob({required this.alignment, required this.color});
  final Alignment alignment;
  final Color color;

  @override
  Widget build(BuildContext context) {
    // Размер blob'а — ~65% от меньшей стороны экрана. С таким размером
    // alignment(-0.7..-0.65) реально утаскивает blob в угол. Если делать
    // 90% — оба blob'а перекрываются в центре независимо от Alignment.
    return Align(
      alignment: alignment,
      child: FractionallySizedBox(
        widthFactor: 0.65,
        heightFactor: 0.65,
        child: DecoratedBox(
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            gradient: RadialGradient(
              colors: [color, color.withValues(alpha: 0)],
              stops: const [0.0, 1.0],
            ),
          ),
        ),
      ),
    );
  }
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
