// PrimaryGlowButton — primary CTA с blue-glow по умолчанию.
//
// Поверх обычной ElevatedButton добавляется decorative shadow,
// дающий ощущение «свечения портала». Используется на главных
// формах (login/register/generate plan и т.п.). Не делает кнопку
// тяжелее логически — это обычный ElevatedButton с тенями.

import 'package:flutter/material.dart';

import '../theme/app_colors.dart';

class PrimaryGlowButton extends StatelessWidget {
  const PrimaryGlowButton({
    super.key,
    required this.onPressed,
    required this.child,
    this.glowColor,
    this.height = 52,
  });

  final VoidCallback? onPressed;
  final Widget child;
  final Color? glowColor;
  final double height;

  @override
  Widget build(BuildContext context) {
    final glow = glowColor ?? AppPalette.primary;
    return Container(
      height: height,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(14),
        boxShadow: onPressed == null
            ? null
            : [
                BoxShadow(
                  color: glow.withValues(alpha: 0.45),
                  blurRadius: 28,
                  spreadRadius: -4,
                  offset: const Offset(0, 8),
                ),
                BoxShadow(
                  color: glow.withValues(alpha: 0.2),
                  blurRadius: 12,
                  spreadRadius: -2,
                ),
              ],
      ),
      child: ElevatedButton(
        onPressed: onPressed,
        style: ElevatedButton.styleFrom(
          minimumSize: const Size.fromHeight(double.infinity),
          padding: EdgeInsets.zero,
        ),
        child: child,
      ),
    );
  }
}
