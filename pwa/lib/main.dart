import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'app/app.dart';
import 'app/theme/theme_mode_provider.dart';
import 'features/auth/auth_state.dart';
import 'features/auth/auth_storage.dart';

Future<void> main() async {
  // Storage инициализируем до runApp: SharedPreferences.getInstance() —
  // async, а Riverpod-Notifier'ам в build() нужен sync read. Один handle
  // на оба провайдера — auth-токены и выбранная тема.
  WidgetsFlutterBinding.ensureInitialized();
  final prefs = await SharedPreferences.getInstance();
  final storage = AuthStorage(prefs);

  runApp(
    ProviderScope(
      overrides: [
        authStorageProvider.overrideWithValue(storage),
        sharedPreferencesProvider.overrideWithValue(prefs),
      ],
      child: const FitnessTrackerApp(),
    ),
  );
}
