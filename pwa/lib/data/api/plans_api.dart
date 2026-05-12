// Клиент для /plans/* — spec 006 §9.
//
// Структура DTO зеркалит ответ бэкенда (api/v1/plans.py::PlanRead):
//   PlanDto → PlanWeekDto → PlanDayDto → PlanExerciseDto.
//
// Cardio-дни на текущий момент персистятся без exercise_id (placeholder
// без FK на каталог, см. сервис) — UI это рендерит как «N мин LISS/HIIT»
// без подробного экрана упражнения.

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'api_client.dart';
import 'failure.dart';

class PlanExerciseDto {
  PlanExerciseDto({
    required this.id,
    required this.exerciseId,
    required this.exerciseName,
    required this.orderNo,
    required this.targetSets,
    required this.targetRepsMin,
    required this.targetRepsMax,
    required this.targetRpe,
    required this.restSeconds,
    required this.targetWeightKg,
    required this.notes,
  });

  factory PlanExerciseDto.fromJson(Map<String, dynamic> json) =>
      PlanExerciseDto(
        id: json['id'] as String,
        exerciseId: json['exercise_id'] as String?,
        exerciseName: json['exercise_name'] as String,
        orderNo: (json['order_no'] as num).toInt(),
        targetSets: (json['target_sets'] as num).toInt(),
        targetRepsMin: (json['target_reps_min'] as num).toInt(),
        targetRepsMax: (json['target_reps_max'] as num).toInt(),
        targetRpe: (json['target_rpe'] as num?)?.toInt(),
        restSeconds: (json['rest_seconds'] as num?)?.toInt(),
        targetWeightKg: (json['target_weight_kg'] as num?)?.toDouble(),
        notes: json['notes'] as String?,
      );

  final String id;
  final String? exerciseId;
  final String exerciseName;
  final int orderNo;
  final int targetSets;
  final int targetRepsMin;
  final int targetRepsMax;
  final int? targetRpe;
  final int? restSeconds;
  final double? targetWeightKg;
  final String? notes;
}

class PlanDayDto {
  PlanDayDto({
    required this.id,
    required this.dayNo,
    required this.name,
    required this.type,
    required this.exercises,
  });

  factory PlanDayDto.fromJson(Map<String, dynamic> json) => PlanDayDto(
        id: json['id'] as String,
        dayNo: (json['day_no'] as num).toInt(),
        name: json['name'] as String,
        type: json['type'] as String,
        exercises: (json['exercises'] as List<dynamic>)
            .map((e) => PlanExerciseDto.fromJson(e as Map<String, dynamic>))
            .toList(),
      );

  final String id;
  final int dayNo;
  final String name;
  final String type; // strength | cardio | rest
  final List<PlanExerciseDto> exercises;
}

class PlanWeekDto {
  PlanWeekDto({required this.id, required this.weekNo, required this.days});

  factory PlanWeekDto.fromJson(Map<String, dynamic> json) => PlanWeekDto(
        id: json['id'] as String,
        weekNo: (json['week_no'] as num).toInt(),
        days: (json['days'] as List<dynamic>)
            .map((e) => PlanDayDto.fromJson(e as Map<String, dynamic>))
            .toList(),
      );

  final String id;
  final int weekNo;
  final List<PlanDayDto> days;
}

class PlanDto {
  PlanDto({
    required this.id,
    required this.status,
    required this.generatedAt,
    required this.validUntil,
    required this.goal,
    required this.trainingLevel,
    required this.frequency,
    required this.modelVersion,
    required this.weeks,
    required this.warnings,
  });

  factory PlanDto.fromJson(Map<String, dynamic> json) => PlanDto(
        id: json['id'] as String,
        status: json['status'] as String,
        generatedAt: DateTime.parse(json['generated_at'] as String),
        validUntil: DateTime.parse(json['valid_until'] as String),
        goal: json['goal'] as String,
        trainingLevel: json['training_level'] as String,
        frequency: (json['frequency'] as num).toInt(),
        modelVersion: json['model_version'] as String,
        weeks: (json['weeks'] as List<dynamic>)
            .map((e) => PlanWeekDto.fromJson(e as Map<String, dynamic>))
            .toList(),
        warnings: ((json['warnings'] as List<dynamic>?) ?? const [])
            .map((e) => e as String)
            .toList(),
      );

  final String id;
  final String status; // active | archived
  final DateTime generatedAt;
  final DateTime validUntil;
  final String goal;
  final String trainingLevel;
  final int frequency;
  final String modelVersion;
  final List<PlanWeekDto> weeks;
  final List<String> warnings;
}

/// Override-параметры для POST /plans/generate. Все поля опциональны —
/// `null` означает «взять из профиля» на бэкенде.
class PlanGenerateOverrideDto {
  PlanGenerateOverrideDto({
    this.goal,
    this.trainingLevel,
    this.trainingFrequency,
    this.equipmentAvailable,
  });

  final String? goal;
  final String? trainingLevel;
  final int? trainingFrequency;
  final List<String>? equipmentAvailable;

  Map<String, dynamic> toJson() {
    final out = <String, dynamic>{};
    if (goal != null) out['goal'] = goal;
    if (trainingLevel != null) out['training_level'] = trainingLevel;
    if (trainingFrequency != null) out['training_frequency'] = trainingFrequency;
    if (equipmentAvailable != null) {
      out['equipment_available'] = equipmentAvailable;
    }
    return out;
  }
}

/// Дискриминатор для 400 preconditions_not_met на старте генерации.
/// `AppFailure` sealed внутри `failure.dart`, наследоваться нельзя, поэтому
/// возвращаем код через ApiFailure.code, а список `missing` нести
/// нечем — UI просто ведёт на /profile.
const planPreconditionsCode = 'preconditions_not_met';

class PlansApi {
  PlansApi(this._dio);
  final Dio _dio;

  /// REQ-12: ручная регенерация. 201 с warnings в payload.
  ///
  /// Особая обработка 400 preconditions_not_met — мапим в типизированный
  /// failure, чтобы UI мог показать конкретный CTA «Перейти в профиль».
  Future<PlanDto> generate({PlanGenerateOverrideDto? override}) async {
    try {
      final body = override == null
          ? <String, dynamic>{}
          : {'override': override.toJson()};
      final res = await _dio.post<Map<String, dynamic>>(
        '/plans/generate',
        data: body,
      );
      return PlanDto.fromJson(res.data!);
    } on DioException catch (e) {
      final data = e.response?.data;
      if (e.response?.statusCode == 400 && data is Map<String, dynamic>) {
        final detail = data['detail'];
        if (detail is Map && detail['error'] == planPreconditionsCode) {
          final missing = ((detail['missing'] as List?) ?? const [])
              .map((x) => x.toString())
              .join(', ');
          throw ApiFailure(
            code: planPreconditionsCode,
            message: missing.isEmpty
                ? 'Заполните профиль перед генерацией плана'
                : 'Заполните в профиле: $missing',
          );
        }
      }
      throw mapDioToFailure(e);
    }
  }

  /// 200 PlanDto / 404 если нет активного — мапим 404 в null.
  Future<PlanDto?> getActive() async {
    try {
      final res = await _dio.get<Map<String, dynamic>>('/plans/active');
      return PlanDto.fromJson(res.data!);
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) return null;
      throw mapDioToFailure(e);
    }
  }

  Future<PlanDto> getById(String id) async {
    try {
      final res = await _dio.get<Map<String, dynamic>>('/plans/$id');
      return PlanDto.fromJson(res.data!);
    } on DioException catch (e) {
      throw mapDioToFailure(e);
    }
  }

  Future<PlanDto> archive(String id) async {
    try {
      final res = await _dio.post<Map<String, dynamic>>('/plans/$id/archive');
      return PlanDto.fromJson(res.data!);
    } on DioException catch (e) {
      throw mapDioToFailure(e);
    }
  }
}

final plansApiProvider =
    Provider<PlansApi>((ref) => PlansApi(ref.watch(dioProvider)));

/// Активный план. Возвращает null если плана нет — UI рендерит empty
/// state с CTA на /plan/generate.
final activePlanProvider = FutureProvider.autoDispose<PlanDto?>(
  (ref) => ref.watch(plansApiProvider).getActive(),
);
