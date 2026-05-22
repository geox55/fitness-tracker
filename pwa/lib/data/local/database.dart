// Локальная БД клиента — spec 015 (offline-first).
//
// drift как кросс-платформенный ORM: SQLite на Android, WASM SQLite поверх
// IndexedDB на Web. Один код на обе платформы, schema-as-Dart-code +
// генерация в database.g.dart через build_runner.
//
// Стартовая схема (M2.1) минимальна — будем разрастать поэтапно:
//   - profiles: read-through кэш профиля (зеркало user_profiles на сервере)
//   - sync_queue: pending-операции, ждущие сетевого окна
//
// В следующих M2.x добавим: workouts, exercise_logs, inbody_measurements,
// plans, forecasts, exercises_catalog.

import 'package:drift/drift.dart';
import 'package:drift_flutter/drift_flutter.dart';

part 'database.g.dart';

/// Локальное зеркало профиля пользователя.
///
/// Чтения экранов профиля идут из этой таблицы — UI всегда мгновенно что-то
/// показывает (Repository pattern). API-обновления приходят фоном.
/// При локальном PATCH помечаем `dirty=true` и кладём операцию в sync_queue.
class Profiles extends Table {
  TextColumn get userId => text()();
  TextColumn get email => text()();
  TextColumn get name => text().nullable()();
  TextColumn get sex => text().nullable()();
  DateTimeColumn get birthDate => dateTime().nullable()();
  RealColumn get heightCm => real().nullable()();
  RealColumn get baselineWeightKg => real().nullable()();
  TextColumn get goal => text().nullable()();
  RealColumn get targetWeightKg => real().nullable()();
  RealColumn get targetMuscleKg => real().nullable()();
  DateTimeColumn get goalStartedAt => dateTime().nullable()();
  TextColumn get trainingLevel => text().nullable()();
  IntColumn get trainingFrequency => integer().nullable()();
  TextColumn get allergiesJson => text().withDefault(const Constant('[]'))();
  TextColumn get equipmentAvailableJson => text().nullable()();
  TextColumn get photoUrl => text().nullable()();
  IntColumn get bmrKcal => integer().nullable()();
  DateTimeColumn get onboardingCompletedAt => dateTime().nullable()();
  BoolColumn get planRebuildRequired =>
      boolean().withDefault(const Constant(false))();
  // spec 015 REQ-06: для If-Unmodified-Since.
  DateTimeColumn get updatedAt => dateTime()();
  // spec 015 §2: «dirty» помечает несинхронизированные локальные изменения.
  BoolColumn get dirty => boolean().withDefault(const Constant(false))();

  @override
  Set<Column> get primaryKey => {userId};
}

/// Очередь pending-операций, ждущих отправки на сервер.
///
/// FIFO; каждая op-я идемпотентна по `client_id`. SyncWorker берёт самую
/// раннюю pending-запись с `next_retry_at <= now()`, шлёт на сервер,
/// помечает `applied` или ретрайтит с exponential backoff.
class SyncQueue extends Table {
  IntColumn get id => integer().autoIncrement()();

  /// UUID, который клиент кладёт в `client_id` payload'а на сервере.
  /// Server-side UNIQUE-индекс (migration 0021) дедуплицирует ретраи.
  TextColumn get clientId => text()();

  /// Тип операции для удобства логирования и debounce-логики.
  /// 'CREATE_WORKOUT' / 'LOG_SET' / 'CREATE_INBODY' / 'PATCH_PROFILE' / ...
  TextColumn get opKind => text()();

  /// Полный путь эндпоинта (например, '/api/v1/workouts').
  TextColumn get endpoint => text()();

  /// HTTP-метод.
  TextColumn get httpMethod => text()();

  /// Body запроса как JSON-string.
  TextColumn get payloadJson => text()();

  /// Доп. заголовки (например, If-Unmodified-Since) как JSON {name: value}.
  TextColumn get headersJson => text().nullable()();

  IntColumn get attempts => integer().withDefault(const Constant(0))();
  TextColumn get lastError => text().nullable()();

  /// `pending` — ждёт; `in_flight` — отправляется прямо сейчас (защита от
  /// двойного запуска воркера); `applied` — синхронизировано; `failed` —
  /// неуспех (можно ретрайнуть руками).
  TextColumn get status =>
      text().withDefault(const Constant('pending'))();

  DateTimeColumn get createdAt =>
      dateTime().withDefault(currentDateAndTime)();
  DateTimeColumn get nextRetryAt => dateTime().nullable()();
  DateTimeColumn get appliedAt => dateTime().nullable()();
}

@DriftDatabase(tables: [Profiles, SyncQueue])
class AppDatabase extends _$AppDatabase {
  AppDatabase([QueryExecutor? executor])
      : super(executor ?? _openConnection());

  @override
  int get schemaVersion => 1;

  /// Кросс-платформенный конструктор соединения.
  /// - Android/iOS: SQLite в documents-папке через path_provider.
  /// - Web: WASM SQLite поверх OPFS или IndexedDB.
  static QueryExecutor _openConnection() {
    return driftDatabase(name: 'portal_local');
  }
}
