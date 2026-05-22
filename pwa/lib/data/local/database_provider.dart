// Singleton-провайдер локальной БД. Один экземпляр на жизнь приложения,
// dispose при выгрузке Riverpod-контейнера.

import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'database.dart';

final appDatabaseProvider = Provider<AppDatabase>((ref) {
  final db = AppDatabase();
  ref.onDispose(db.close);
  return db;
});
