// Тема приложения: system / light / dark. Хранится в SharedPreferences и
// переживает перезагрузку PWA. По умолчанию — system (следует за ОС), чтобы
// светлая Portal-тема включалась автоматически у пользователей со светлой ОС,
// а переключатель в профиле позволял зафиксировать любой режим вручную.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Хэндл SharedPreferences. Переопределяется в main() готовым инстансом —
/// Notifier'у нужен sync-read в build(), а getInstance() async (тот же
/// паттерн, что у authStorageProvider).
final sharedPreferencesProvider = Provider<SharedPreferences>(
  (ref) => throw UnimplementedError('override sharedPreferencesProvider in main()'),
);

const _kThemeMode = 'app.theme_mode';

class ThemeModeNotifier extends Notifier<ThemeMode> {
  @override
  ThemeMode build() {
    final raw = ref.read(sharedPreferencesProvider).getString(_kThemeMode);
    return _decode(raw);
  }

  Future<void> set(ThemeMode mode) async {
    state = mode;
    await ref.read(sharedPreferencesProvider).setString(_kThemeMode, _encode(mode));
  }

  static ThemeMode _decode(String? raw) => switch (raw) {
        'light' => ThemeMode.light,
        'dark' => ThemeMode.dark,
        _ => ThemeMode.system,
      };

  static String _encode(ThemeMode mode) => switch (mode) {
        ThemeMode.light => 'light',
        ThemeMode.dark => 'dark',
        ThemeMode.system => 'system',
      };
}

final themeModeProvider =
    NotifierProvider<ThemeModeNotifier, ThemeMode>(ThemeModeNotifier.new);
