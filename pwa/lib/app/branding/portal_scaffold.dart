// PortalScaffold — обёртка над Scaffold, которая под body кладёт
// PortalBackdrop (animated portal-blobs blue + orange + diagonal stripes).
//
// Зачем не глобальный wrapper в MaterialApp.builder:
// При прозрачном scaffoldBackgroundColor Flutter Navigator на 1 кадр
// показывает старый экран сквозь новый — визуально это "наложение".
// Локальный backdrop под body конкретного экрана + непрозрачный
// scaffoldBackgroundColor устраняет проблему: при смене экранов новый
// scaffold перекрывает старый сразу, и его backdrop стартует с нуля.

import 'package:flutter/material.dart';

import 'portal_backdrop.dart';

class PortalScaffold extends StatelessWidget {
  const PortalScaffold({
    super.key,
    this.appBar,
    this.body,
    this.floatingActionButton,
    this.floatingActionButtonLocation,
    this.bottomNavigationBar,
    this.drawer,
    this.endDrawer,
    this.resizeToAvoidBottomInset,
    this.extendBody = false,
    this.extendBodyBehindAppBar = false,
    this.backgroundColor,
    this.intensity = 1.0,
  });

  final PreferredSizeWidget? appBar;
  final Widget? body;
  final Widget? floatingActionButton;
  final FloatingActionButtonLocation? floatingActionButtonLocation;
  final Widget? bottomNavigationBar;
  final Widget? drawer;
  final Widget? endDrawer;
  final bool? resizeToAvoidBottomInset;
  final bool extendBody;
  final bool extendBodyBehindAppBar;
  final Color? backgroundColor;

  /// intensity для PortalBackdrop. По умолчанию 1.0 — как на auth-экранах
  /// (user попросила одинаковый яркий фон везде). Можно понизить на конкретном
  /// экране если контента слишком много и blob'ы отвлекают.
  final double intensity;

  @override
  Widget build(BuildContext context) {
    final wrappedBody = body == null
        ? null
        : PortalBackdrop(intensity: intensity, child: body!);
    return Scaffold(
      appBar: appBar,
      body: wrappedBody,
      floatingActionButton: floatingActionButton,
      floatingActionButtonLocation: floatingActionButtonLocation,
      bottomNavigationBar: bottomNavigationBar,
      drawer: drawer,
      endDrawer: endDrawer,
      resizeToAvoidBottomInset: resizeToAvoidBottomInset,
      extendBody: extendBody,
      extendBodyBehindAppBar: extendBodyBehindAppBar,
      backgroundColor: backgroundColor,
    );
  }
}
