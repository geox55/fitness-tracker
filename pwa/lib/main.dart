import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'app/app.dart';
import 'features/auth/auth_state.dart';
import 'features/auth/auth_storage.dart';

Future<void> main() async {
  // Storage инициализируем до runApp: SharedPreferences.getInstance() —
  // async, а Riverpod-Notifier'у в build() нужен sync read. Кладём
  // готовый handle в override authStorageProvider.
  WidgetsFlutterBinding.ensureInitialized();
  final storage = await AuthStorage.create();

  runApp(
    ProviderScope(
      overrides: [authStorageProvider.overrideWithValue(storage)],
      child: const FitnessTrackerApp(),
    ),
  );
}
