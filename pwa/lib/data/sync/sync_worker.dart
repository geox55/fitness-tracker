// SyncWorker — фоновый драйвер sync_queue (spec 015 REQ-04/05).
//
// Слушает connectivity_plus; при переходе offline → online запускает drain
// очереди. Также drain можно дёрнуть вручную (например, из UI «Повторить
// сейчас») и периодическим таймером каждые 30 секунд для долгих ретраев.
//
// Алгоритм drain'а:
//   1) SELECT pending-op с минимальным id и next_retry_at <= now.
//   2) Помечаем status='in_flight' (защита от двойного запуска воркера).
//   3) Шлём HTTP через Dio (метод/endpoint/payload/headers из row'а).
//   4) На 2xx → status='applied', appliedAt=now. Иначе → attempts++,
//      lastError=сообщение, status='pending', nextRetryAt=now + backoff,
//      где backoff = min(2^attempts, 30 sec).
//   5) После N=10 неудач → status='failed' (видим в UI, ждём ручного «retry»).
//
// Не блокирует UI: всё через async-методы, ConnectivityListener — Stream.

import 'dart:async';
import 'dart:convert';
import 'dart:math' as math;

import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:dio/dio.dart';
import 'package:drift/drift.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../api/api_client.dart';
import '../local/database.dart';
import '../local/database_provider.dart';

const _maxAttempts = 10;
const _maxBackoffSeconds = 30;

class SyncWorker {
  SyncWorker(this._db, this._dio);

  final AppDatabase _db;
  final Dio _dio;

  StreamSubscription<List<ConnectivityResult>>? _connSub;
  Timer? _periodicTimer;
  bool _draining = false;

  /// Запустить наблюдение за сетью + периодический drain.
  void start() {
    _connSub = Connectivity().onConnectivityChanged.listen((results) {
      final online = results.any((r) => r != ConnectivityResult.none);
      if (online) {
        // Не ждём — fire-and-forget. drain() сам защищается от двойного входа.
        unawaited(drain());
      }
    });
    _periodicTimer = Timer.periodic(const Duration(seconds: 30), (_) {
      unawaited(drain());
    });
    unawaited(drain());
  }

  void stop() {
    _connSub?.cancel();
    _connSub = null;
    _periodicTimer?.cancel();
    _periodicTimer = null;
  }

  /// Прогнать очередь до конца (или до первой не-исправимой ошибки).
  /// Защищён от двойного запуска — параллельные вызовы no-op.
  Future<void> drain() async {
    if (_draining) return;
    _draining = true;
    try {
      while (true) {
        final next = await _pickNextPending();
        if (next == null) break;
        await _processOne(next);
      }
    } finally {
      _draining = false;
    }
  }

  Future<SyncQueueData?> _pickNextPending() async {
    final now = DateTime.now();
    final query = _db.select(_db.syncQueue)
      ..where(
        (t) =>
            t.status.equals('pending') &
            (t.nextRetryAt.isNull() | t.nextRetryAt.isSmallerOrEqualValue(now)),
      )
      ..orderBy([(t) => OrderingTerm.asc(t.id)])
      ..limit(1);
    return query.getSingleOrNull();
  }

  Future<void> _processOne(SyncQueueData row) async {
    // Защита от двойного запуска: переводим в 'in_flight' атомарно.
    final claimed = await (_db.update(_db.syncQueue)
          ..where((t) => t.id.equals(row.id) & t.status.equals('pending')))
        .write(const SyncQueueCompanion(status: Value('in_flight')));
    if (claimed == 0) return; // кто-то уже забрал

    try {
      final payload = jsonDecode(row.payloadJson) as Map<String, dynamic>;
      final headers = row.headersJson == null
          ? <String, String>{}
          : (jsonDecode(row.headersJson!) as Map<String, dynamic>)
              .map((k, v) => MapEntry(k, v.toString()));

      await _dio.request<dynamic>(
        row.endpoint,
        data: payload,
        options: Options(
          method: row.httpMethod,
          headers: headers.isEmpty ? null : headers,
        ),
      );

      await (_db.update(_db.syncQueue)..where((t) => t.id.equals(row.id)))
          .write(SyncQueueCompanion(
        status: const Value('applied'),
        appliedAt: Value(DateTime.now()),
      ));
    } on DioException catch (e) {
      await _markRetryOrFailed(row, _formatError(e));
    } catch (e) {
      await _markRetryOrFailed(row, e.toString());
    }
  }

  Future<void> _markRetryOrFailed(SyncQueueData row, String error) async {
    final nextAttempts = row.attempts + 1;
    final isExhausted = nextAttempts >= _maxAttempts;
    final backoff = math.min(
      math.pow(2, nextAttempts).toInt(),
      _maxBackoffSeconds,
    );
    await (_db.update(_db.syncQueue)..where((t) => t.id.equals(row.id)))
        .write(
      SyncQueueCompanion(
        attempts: Value(nextAttempts),
        lastError: Value(error),
        status: Value(isExhausted ? 'failed' : 'pending'),
        nextRetryAt: Value(
          isExhausted ? null : DateTime.now().add(Duration(seconds: backoff)),
        ),
      ),
    );
  }

  String _formatError(DioException e) {
    final status = e.response?.statusCode;
    if (status != null) return 'HTTP $status: ${e.message ?? e.type.name}';
    return e.type.name;
  }
}

final syncWorkerProvider = Provider<SyncWorker>((ref) {
  final worker = SyncWorker(
    ref.read(appDatabaseProvider),
    ref.read(dioProvider),
  );
  ref.onDispose(worker.stop);
  return worker;
});
