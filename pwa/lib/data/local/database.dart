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

// ---------------------------------------------------------------------------
// Read-through cache таблицы (зеркало серверных сущностей)
// ---------------------------------------------------------------------------

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

/// Локальное зеркало workouts. PK здесь — server-side UUID (когда уже
/// синхронизированы), либо client_id (для pending-records, ещё не получивших
/// server-side id). После sync клиент обновляет PK на server-side значение
/// в одной транзакции.
class LocalWorkouts extends Table {
  @override
  String get tableName => 'workouts';

  TextColumn get id => text()();
  TextColumn get userId => text()();
  TextColumn get clientId => text().nullable()();
  DateTimeColumn get performedAt => dateTime()();
  DateTimeColumn get finishedAt => dateTime().nullable()();
  TextColumn get status => text()();
  TextColumn get origin => text()();
  TextColumn get planDayId => text().nullable()();
  TextColumn get notes => text().nullable()();
  // spec 015 §4.D: статус синхронизации.
  // 'synced' (есть на сервере) / 'pending' (висит в sync_queue) /
  // 'failed' (попытка отправки вернула не-2xx).
  TextColumn get syncStatus =>
      text().withDefault(const Constant('synced'))();
  DateTimeColumn get createdAt =>
      dateTime().withDefault(currentDateAndTime)();

  @override
  Set<Column> get primaryKey => {id};
}

/// Логи подходов. Не имеют отдельного userId — он определяется через FK
/// на workouts (упростили схему: лог без тренировки невозможен).
class LocalExerciseLogs extends Table {
  @override
  String get tableName => 'exercise_logs';

  TextColumn get id => text()();
  TextColumn get workoutId => text()();
  TextColumn get exerciseId => text()();
  TextColumn get clientId => text().nullable()();
  IntColumn get setNumber => integer()();
  IntColumn get reps => integer()();
  RealColumn get weightKg => real()();
  IntColumn get rpe => integer().nullable()();
  IntColumn get restSeconds => integer().nullable()();
  BoolColumn get skipped => boolean().withDefault(const Constant(false))();
  DateTimeColumn get loggedAt => dateTime()();
  TextColumn get syncStatus =>
      text().withDefault(const Constant('synced'))();

  @override
  Set<Column> get primaryKey => {id};
}

/// Замеры InBody — append-only, никогда не редактируются, только удаление.
class LocalInBodyMeasurements extends Table {
  @override
  String get tableName => 'inbody_measurements';

  TextColumn get id => text()();
  TextColumn get userId => text()();
  TextColumn get clientId => text().nullable()();
  DateTimeColumn get measuredAt => dateTime()();
  RealColumn get weightKg => real()();
  RealColumn get heightCm => real()();
  TextColumn get sex => text()();
  RealColumn get bodyFatPercent => real()();
  RealColumn get muscleMassKg => real().nullable()();
  RealColumn get bodyWaterPercent => real().nullable()();
  RealColumn get proteinKg => real().nullable()();
  RealColumn get mineralsKg => real().nullable()();
  IntColumn get visceralFatLevel => integer().nullable()();
  IntColumn get bmrKcal => integer().nullable()();
  RealColumn get fatFreeMassKg => real().nullable()();
  RealColumn get bmi => real()();
  TextColumn get source => text()();
  // Signed URL'ы протухают, поэтому здесь храним только storage-key;
  // URL пересчитывается при заходе на экран (см. репозиторий).
  TextColumn get originalPdfKey => text().nullable()();
  TextColumn get syncStatus =>
      text().withDefault(const Constant('synced'))();
  DateTimeColumn get createdAt => dateTime()();

  @override
  Set<Column> get primaryKey => {id};
}

/// Активный план — read-only с клиента. На сервере генерирует composer,
/// клиент просто кэширует ответ /api/v1/plans/active. Старые планы
/// эвиктятся когда приходит новый active.
class LocalPlans extends Table {
  @override
  String get tableName => 'plans';

  TextColumn get id => text()();
  TextColumn get userId => text()();
  TextColumn get status => text()();
  TextColumn get goal => text()();
  IntColumn get trainingFrequency => integer().nullable()();
  DateTimeColumn get validFrom => dateTime()();
  DateTimeColumn get validUntil => dateTime()();
  // Целиком сериализованные weeks→days→exercises как JSON, чтобы не
  // плодить три зеркальные таблицы и не возиться с FK в SQLite. Это
  // pragmatic-выбор: план денормализован и отдаётся UI одним куском.
  TextColumn get payloadJson => text()();
  DateTimeColumn get fetchedAt =>
      dateTime().withDefault(currentDateAndTime)();

  @override
  Set<Column> get primaryKey => {id};
}

/// Последний прогноз InBody (spec 008) — singleton по user.
/// TTL 24ч, после старее показываем с предупреждением «нет связи».
class LocalForecasts extends Table {
  @override
  String get tableName => 'forecasts';

  TextColumn get userId => text()();
  TextColumn get modelVersion => text()();
  TextColumn get confidence => text()();
  BoolColumn get fallback => boolean()();
  DateTimeColumn get generatedAt => dateTime()();
  // Полный JSON ответа /api/v1/forecast/inbody (метрики + интерпретация).
  TextColumn get payloadJson => text()();
  DateTimeColumn get fetchedAt =>
      dateTime().withDefault(currentDateAndTime)();

  @override
  Set<Column> get primaryKey => {userId};
}

/// Кэш каталога упражнений (~400 записей). Версионируется через
/// `version` — сервер отдаёт diff при `GET /catalog/exercises?since=<v>`
/// (если такой эндпоинт появится).
class LocalExercises extends Table {
  @override
  String get tableName => 'exercises_catalog';

  TextColumn get id => text()();
  TextColumn get exerciseId => text()();
  TextColumn get exerciseName => text()();
  TextColumn get exerciseNameRu => text().nullable()();
  TextColumn get primaryMuscleGroup => text()();
  TextColumn get secondaryMuscleGroupJson =>
      text().withDefault(const Constant('[]'))();
  TextColumn get equipmentJson =>
      text().withDefault(const Constant('[]'))();
  TextColumn get bodyRegion => text()();
  IntColumn get version => integer().withDefault(const Constant(1))();
  DateTimeColumn get fetchedAt =>
      dateTime().withDefault(currentDateAndTime)();

  @override
  Set<Column> get primaryKey => {id};
}

// ---------------------------------------------------------------------------
// Sync queue (spec 015 §4 REQ-04/05)
// ---------------------------------------------------------------------------

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

@DriftDatabase(tables: [
  Profiles,
  LocalWorkouts,
  LocalExerciseLogs,
  LocalInBodyMeasurements,
  LocalPlans,
  LocalForecasts,
  LocalExercises,
  SyncQueue,
])
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
