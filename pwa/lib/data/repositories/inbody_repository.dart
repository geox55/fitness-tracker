// InBodyRepository — read-through кэш списка InBody-замеров (spec 015 REQ-03).
//
// Замеры — append-only. Чтения экранов идут из локальной БД. refresh()
// дёргает GET /inbody/measurements и обновляет локальную копию.

import 'dart:async';

import 'package:drift/drift.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../api/inbody_api.dart';
import '../local/database.dart';
import '../local/database_provider.dart';

class InBodyRepository {
  InBodyRepository(this._db, this._api);

  final AppDatabase _db;
  final InBodyApi _api;

  /// Подписка на список замеров пользователя, отсортированный по дате убыв.
  /// UI получает свежий emit при каждом UPSERT'е в локальной таблице.
  Stream<List<MeasurementDto>> watch({
    required String userId,
    int? limit,
  }) {
    final query = _db.select(_db.localInBodyMeasurements)
      ..where((t) => t.userId.equals(userId))
      ..orderBy([
        (t) => OrderingTerm.desc(t.measuredAt),
      ]);
    if (limit != null) query.limit(limit);
    return query.watch().map((rows) => rows.map(_rowToDto).toList());
  }

  /// Pull-обновление списка из API.
  Future<void> refresh({required String userId, int limit = 50}) async {
    final response = await _api.list(limit: limit);
    await _db.transaction(() async {
      for (final dto in response.items) {
        await _upsert(userId: userId, dto: dto);
      }
    });
  }

  Future<void> _upsert({
    required String userId,
    required MeasurementDto dto,
  }) async {
    await _db.into(_db.localInBodyMeasurements).insertOnConflictUpdate(
          LocalInBodyMeasurementsCompanion.insert(
            id: dto.id,
            userId: userId,
            measuredAt: dto.measuredAt,
            weightKg: dto.weightKg,
            // В minimal MeasurementDto нет height/sex/bmi — это short-form,
            // используемый на экранах списка. Полный замер придёт через
            // отдельный GET /{id} и обновит запись. Здесь подставляем
            // заглушки (0/'unknown'), которые будут перезаписаны при
            // detail-fetch'е.
            heightCm: 0,
            sex: 'unknown',
            bodyFatPercent: dto.bodyFatPercent,
            muscleMassKg: Value(dto.muscleMassKg),
            bmi: 0,
            source: dto.source,
            createdAt: dto.measuredAt,
          ),
        );
  }

  MeasurementDto _rowToDto(LocalInBodyMeasurement row) {
    return MeasurementDto(
      id: row.id,
      measuredAt: row.measuredAt,
      weightKg: row.weightKg,
      bodyFatPercent: row.bodyFatPercent,
      muscleMassKg: row.muscleMassKg,
      source: row.source,
    );
  }
}

final inbodyRepositoryProvider = Provider<InBodyRepository>((ref) {
  return InBodyRepository(
    ref.read(appDatabaseProvider),
    ref.read(inBodyApiProvider),
  );
});

