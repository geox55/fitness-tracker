// ProfileRepository — read-through кэш профиля (spec 015 REQ-03).
//
// Чтения:
//   - watchProfile(): Stream<ProfileDto?> подписан на локальную таблицу;
//     UI всегда что-то показывает, как только в БД появилась запись.
//   - refresh(): фоном дёргает GET /profile, обновляет локальную копию,
//     срабатывает emit в Stream.
//
// Запись (PATCH/photo) — добавим в M2.4 вместе с SyncWorker'ом. Сейчас
// репозиторий выступает как «read-only smart cache».

import 'dart:async';
import 'dart:convert';

import 'package:drift/drift.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../api/profile_api.dart';
import '../local/database.dart';
import '../local/database_provider.dart';
import '../sync/sync_queue.dart';

class ProfileRepository {
  ProfileRepository(this._db, this._api, this._queue);

  final AppDatabase _db;
  final ProfileApi _api;
  final SyncQueueWriter _queue;

  /// Подписка на локальную копию профиля.
  /// `null` пока initial-sync не отработал.
  Stream<ProfileDto?> watch(String userId) {
    final query = (_db.select(_db.profiles)
      ..where((t) => t.userId.equals(userId)));
    return query.watchSingleOrNull().map(_rowToDto);
  }

  /// Pull-обновление из API → запись в локальную БД.
  /// Вызывается: при холодном старте экрана, при pull-to-refresh,
  /// после события ConnectivityListener (online).
  Future<void> refresh() async {
    final dto = await _api.get();
    await _upsertFromDto(dto);
  }

  /// Локальный PATCH профиля (optimistic update) + enqueue PATCH-операции
  /// на сервер. UI получает свежий emit мгновенно через watch().
  ///
  /// Все поля nullable — null означает «не трогаем» (как у PATCH /profile).
  /// Спека 015 REQ-06: для last-write-wins передаётся If-Unmodified-Since
  /// с текущим updated_at локальной копии.
  Future<void> patch({
    required String userId,
    String? name,
    String? sex,
    DateTime? birthDate,
    double? heightCm,
    double? baselineWeightKg,
    String? goal,
    double? targetWeightKg,
    double? targetMuscleKg,
    DateTime? goalStartedAt,
    String? trainingLevel,
    int? trainingFrequency,
    List<String>? allergies,
    List<String>? equipmentAvailable,
  }) async {
    // 1) Подготовить тело запроса для сервера.
    final body = <String, dynamic>{};
    if (name != null) body['name'] = name;
    if (sex != null) body['sex'] = sex;
    if (birthDate != null) {
      body['birth_date'] = birthDate.toIso8601String().split('T').first;
    }
    if (heightCm != null) body['height_cm'] = heightCm;
    if (baselineWeightKg != null) body['baseline_weight_kg'] = baselineWeightKg;
    if (goal != null) body['goal'] = goal;
    if (targetWeightKg != null) body['target_weight_kg'] = targetWeightKg;
    if (targetMuscleKg != null) body['target_muscle_kg'] = targetMuscleKg;
    if (goalStartedAt != null) {
      body['goal_started_at'] =
          goalStartedAt.toIso8601String().split('T').first;
    }
    if (trainingLevel != null) body['training_level'] = trainingLevel;
    if (trainingFrequency != null) body['training_frequency'] = trainingFrequency;
    if (allergies != null) body['allergies'] = allergies;
    if (equipmentAvailable != null) {
      body['equipment_available'] = equipmentAvailable;
    }

    // 2) Применить локально (optimistic update) + dirty=true.
    final current = await getCached(userId);
    if (current != null) {
      await (_db.update(_db.profiles)
            ..where((t) => t.userId.equals(userId)))
          .write(
        ProfilesCompanion(
          name: name == null ? const Value.absent() : Value(name),
          sex: sex == null ? const Value.absent() : Value(sex),
          birthDate:
              birthDate == null ? const Value.absent() : Value(birthDate),
          heightCm:
              heightCm == null ? const Value.absent() : Value(heightCm),
          baselineWeightKg: baselineWeightKg == null
              ? const Value.absent()
              : Value(baselineWeightKg),
          goal: goal == null ? const Value.absent() : Value(goal),
          targetWeightKg: targetWeightKg == null
              ? const Value.absent()
              : Value(targetWeightKg),
          targetMuscleKg: targetMuscleKg == null
              ? const Value.absent()
              : Value(targetMuscleKg),
          goalStartedAt: goalStartedAt == null
              ? const Value.absent()
              : Value(goalStartedAt),
          trainingLevel: trainingLevel == null
              ? const Value.absent()
              : Value(trainingLevel),
          trainingFrequency: trainingFrequency == null
              ? const Value.absent()
              : Value(trainingFrequency),
          allergiesJson: allergies == null
              ? const Value.absent()
              : Value(jsonEncode(allergies)),
          equipmentAvailableJson: equipmentAvailable == null
              ? const Value.absent()
              : Value(jsonEncode(equipmentAvailable)),
          dirty: const Value(true),
        ),
      );
    }

    // 3) Поставить операцию в очередь — sync_worker'у её довести до сервера.
    await _queue.enqueue(
      clientId: _newUuidV4(),
      opKind: 'PATCH_PROFILE',
      endpoint: '/profile',
      httpMethod: 'PATCH',
      payload: body,
      headers: current == null
          ? null
          : {'If-Unmodified-Since': current.updatedAt.toUtc().toIso8601String()},
    );
  }

  String _newUuidV4() {
    // Простой UUID v4 без зависимости от внешнего пакета: 122 bits случайных.
    final rng = DateTime.now().microsecondsSinceEpoch;
    final r = rng ^ identityHashCode(this);
    final parts = List.generate(
      4,
      (i) => ((r >> (i * 16)) & 0xFFFF).toRadixString(16).padLeft(4, '0'),
    );
    final hi = parts[0];
    final mid = parts[1];
    // Версия 4 в старшем nibble третьего блока.
    final ver = '4${parts[2].substring(1)}';
    // Variant 10xx в старшем nibble четвёртого блока.
    final variant = parts[3];
    final tail = DateTime.now().microsecondsSinceEpoch.toRadixString(16)
        .padLeft(12, '0')
        .substring(0, 12);
    return '$hi$mid-$mid-$ver-$variant-$tail';
  }

  /// Прямое чтение из локальной БД (без подписки) — для случаев,
  /// когда нужно одноразово получить current state.
  Future<ProfileDto?> getCached(String userId) async {
    final row = await (_db.select(_db.profiles)
          ..where((t) => t.userId.equals(userId)))
        .getSingleOrNull();
    return _rowToDto(row);
  }

  Future<void> _upsertFromDto(ProfileDto dto) async {
    await _db.into(_db.profiles).insertOnConflictUpdate(
          ProfilesCompanion.insert(
            userId: dto.userId,
            email: dto.email,
            name: Value(dto.name),
            sex: Value(dto.sex),
            birthDate: Value(dto.birthDate),
            heightCm: Value(dto.heightCm),
            baselineWeightKg: Value(dto.baselineWeightKg),
            goal: Value(dto.goal),
            targetWeightKg: Value(dto.targetWeightKg),
            targetMuscleKg: Value(dto.targetMuscleKg),
            goalStartedAt: Value(dto.goalStartedAt),
            trainingLevel: Value(dto.trainingLevel),
            trainingFrequency: Value(dto.trainingFrequency),
            allergiesJson: Value(jsonEncode(dto.allergies)),
            equipmentAvailableJson: dto.equipmentAvailable == null
                ? const Value.absent()
                : Value(jsonEncode(dto.equipmentAvailable)),
            photoUrl: Value(dto.photoUrl),
            bmrKcal: Value(dto.bmrKcal),
            onboardingCompletedAt: Value(dto.onboardingCompletedAt),
            planRebuildRequired: Value(dto.planRebuildRequired),
            updatedAt: dto.updatedAt,
            dirty: const Value(false),
          ),
        );
  }

  ProfileDto? _rowToDto(Profile? row) {
    if (row == null) return null;
    return ProfileDto(
      userId: row.userId,
      email: row.email,
      name: row.name,
      sex: row.sex,
      birthDate: row.birthDate,
      heightCm: row.heightCm,
      baselineWeightKg: row.baselineWeightKg,
      goal: row.goal,
      targetWeightKg: row.targetWeightKg,
      targetMuscleKg: row.targetMuscleKg,
      goalStartedAt: row.goalStartedAt,
      trainingLevel: row.trainingLevel,
      trainingFrequency: row.trainingFrequency,
      allergies:
          (jsonDecode(row.allergiesJson) as List<dynamic>).cast<String>(),
      equipmentAvailable: row.equipmentAvailableJson == null
          ? null
          : (jsonDecode(row.equipmentAvailableJson!) as List<dynamic>)
              .cast<String>(),
      photoUrl: row.photoUrl,
      bmrKcal: row.bmrKcal,
      onboardingCompletedAt: row.onboardingCompletedAt,
      planRebuildRequired: row.planRebuildRequired,
      updatedAt: row.updatedAt,
    );
  }
}

final profileRepositoryProvider = Provider<ProfileRepository>((ref) {
  return ProfileRepository(
    ref.read(appDatabaseProvider),
    ref.read(profileApiProvider),
    ref.read(syncQueueWriterProvider),
  );
});
