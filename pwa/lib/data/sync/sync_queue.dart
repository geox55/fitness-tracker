// SyncQueueWriter — helper для добавления pending-операции в локальную очередь.
//
// Используется репозиториями: при мутации UI вызывает repo.method(), репо
// (1) пишет локально → emit в Stream, (2) добавляет op в sync_queue через
// этот writer. SyncWorker подхватывает op при следующем сетевом окне.

import 'dart:convert';

import 'package:drift/drift.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../local/database.dart';
import '../local/database_provider.dart';

class SyncQueueWriter {
  SyncQueueWriter(this._db);
  final AppDatabase _db;

  /// Добавляет pending-операцию в очередь.
  ///
  /// [clientId] — UUID, кладётся в body запроса как `client_id` для
  /// server-side dedup'а (spec 015 REQ-01/02).
  ///
  /// Возвращает row-id операции (нужен для status-update'ов в SyncWorker).
  Future<int> enqueue({
    required String clientId,
    required String opKind,
    required String endpoint,
    required String httpMethod,
    required Map<String, dynamic> payload,
    Map<String, String>? headers,
  }) {
    return _db.into(_db.syncQueue).insert(
          SyncQueueCompanion.insert(
            clientId: clientId,
            opKind: opKind,
            endpoint: endpoint,
            httpMethod: httpMethod,
            payloadJson: jsonEncode(payload),
            headersJson:
                headers == null ? const Value.absent() : Value(jsonEncode(headers)),
          ),
        );
  }

  /// Возвращает число pending-операций — для UI-бэйджа.
  Stream<int> watchPendingCount() {
    final query = _db.selectOnly(_db.syncQueue)
      ..addColumns([_db.syncQueue.id.count()])
      ..where(_db.syncQueue.status.equals('pending'));
    return query
        .watchSingle()
        .map((row) => row.read(_db.syncQueue.id.count()) ?? 0);
  }
}

final syncQueueWriterProvider = Provider<SyncQueueWriter>((ref) {
  return SyncQueueWriter(ref.read(appDatabaseProvider));
});
