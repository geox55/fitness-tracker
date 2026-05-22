// Эмблема приложения «Portal» — стилизованная Aperture-like форма.
//
// Геометрия: внешнее кольцо + 8 трапециевидных лопастей внутрь + центральная
// точка. Это **собственная стилизация**, а не воспроизведение оригинального
// логотипа Valve — концентрические кольца как намёк на «затвор камеры»,
// два акцентных цвета (portal-blue + aperture-orange) на противоположных
// секторах.

import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../theme/app_colors.dart';

class ApertureLogo extends StatelessWidget {
  const ApertureLogo({
    super.key,
    this.size = 88,
    this.blueColor,
    this.orangeColor,
    this.ringColor,
  });

  final double size;
  final Color? blueColor;
  final Color? orangeColor;
  final Color? ringColor;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return SizedBox(
      width: size,
      height: size,
      child: CustomPaint(
        painter: _AperturePainter(
          blueColor: blueColor ?? AppPalette.primary,
          orangeColor: orangeColor ?? AppPalette.secondary,
          ringColor:
              ringColor ?? theme.colorScheme.onSurface.withValues(alpha: 0.92),
        ),
      ),
    );
  }
}

class _AperturePainter extends CustomPainter {
  _AperturePainter({
    required this.blueColor,
    required this.orangeColor,
    required this.ringColor,
  });

  final Color blueColor;
  final Color orangeColor;
  final Color ringColor;

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = math.min(size.width, size.height) / 2;

    // Внешнее кольцо (тонкое).
    final outerRing = Paint()
      ..color = ringColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = radius * 0.06;
    canvas.drawCircle(center, radius * 0.94, outerRing);

    // Внутреннее кольцо (потолще), фон лопастей.
    final innerRing = Paint()
      ..color = ringColor.withValues(alpha: 0.9)
      ..style = PaintingStyle.stroke
      ..strokeWidth = radius * 0.04;
    canvas.drawCircle(center, radius * 0.62, innerRing);

    // 8 лопастей-трапеций, чередующих оттенок (blue / orange / ring).
    // Сектор 1 (верх) — blue, сектор 5 (низ) — orange; остальные — ringColor.
    const bladeCount = 8;
    for (var i = 0; i < bladeCount; i++) {
      final angleStart = -math.pi / 2 + (2 * math.pi / bladeCount) * i;
      final angleEnd = angleStart + (2 * math.pi / bladeCount) * 0.78;

      final color = switch (i) {
        0 => blueColor, // верх — синий портал
        4 => orangeColor, // низ — оранжевый портал
        _ => ringColor.withValues(alpha: 0.55),
      };

      final path = Path()
        ..moveTo(
          center.dx + radius * 0.62 * math.cos(angleStart),
          center.dy + radius * 0.62 * math.sin(angleStart),
        )
        ..lineTo(
          center.dx + radius * 0.88 * math.cos(angleStart),
          center.dy + radius * 0.88 * math.sin(angleStart),
        )
        ..arcToPoint(
          Offset(
            center.dx + radius * 0.88 * math.cos(angleEnd),
            center.dy + radius * 0.88 * math.sin(angleEnd),
          ),
          radius: Radius.circular(radius * 0.88),
        )
        ..lineTo(
          center.dx + radius * 0.62 * math.cos(angleEnd),
          center.dy + radius * 0.62 * math.sin(angleEnd),
        )
        ..arcToPoint(
          Offset(
            center.dx + radius * 0.62 * math.cos(angleStart),
            center.dy + radius * 0.62 * math.sin(angleStart),
          ),
          radius: Radius.circular(radius * 0.62),
          clockwise: false,
        );

      canvas.drawPath(path, Paint()..color = color);
    }

    // Центральная точка (зрачок).
    final pupil = Paint()..color = ringColor;
    canvas.drawCircle(center, radius * 0.12, pupil);
  }

  @override
  bool shouldRepaint(covariant _AperturePainter old) =>
      old.blueColor != blueColor ||
      old.orangeColor != orangeColor ||
      old.ringColor != ringColor;
}
