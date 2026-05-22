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

class ProfileRepository {
  ProfileRepository(this._db, this._api);

  final AppDatabase _db;
  final ProfileApi _api;

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
  );
});
