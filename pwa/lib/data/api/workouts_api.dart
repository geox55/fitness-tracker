import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'api_client.dart';
import 'failure.dart';

class ExerciseLogDto {
  ExerciseLogDto({
    required this.id,
    required this.exerciseId,
    required this.setNumber,
    required this.reps,
    required this.weightKg,
    required this.rpe,
    required this.restSeconds,
    required this.skipped,
    required this.loggedAt,
  });

  factory ExerciseLogDto.fromJson(Map<String, dynamic> json) => ExerciseLogDto(
        id: json['id'] as String,
        exerciseId: json['exercise_id'] as String,
        setNumber: (json['set_number'] as num).toInt(),
        reps: (json['reps'] as num).toInt(),
        weightKg: (json['weight_kg'] as num).toDouble(),
        rpe: (json['rpe'] as num?)?.toInt(),
        restSeconds: (json['rest_seconds'] as num?)?.toInt(),
        skipped: json['skipped'] as bool,
        loggedAt: DateTime.parse(json['logged_at'] as String),
      );

  final String id;
  final String exerciseId;
  final int setNumber;
  final int reps;
  final double weightKg;
  final int? rpe;
  final int? restSeconds;
  final bool skipped;
  final DateTime loggedAt;
}

class WorkoutDto {
  WorkoutDto({
    required this.id,
    required this.performedAt,
    required this.finishedAt,
    required this.status,
    required this.origin,
    required this.notes,
    required this.logs,
  });

  factory WorkoutDto.fromJson(Map<String, dynamic> json) => WorkoutDto(
        id: json['id'] as String,
        performedAt: DateTime.parse(json['performed_at'] as String),
        finishedAt: json['finished_at'] == null
            ? null
            : DateTime.parse(json['finished_at'] as String),
        status: json['status'] as String,
        origin: json['origin'] as String,
        notes: json['notes'] as String?,
        logs: ((json['logs'] as List<dynamic>?) ?? [])
            .map((e) => ExerciseLogDto.fromJson(e as Map<String, dynamic>))
            .toList(),
      );

  final String id;
  final DateTime performedAt;
  final DateTime? finishedAt;
  final String status;
  final String origin;
  final String? notes;
  final List<ExerciseLogDto> logs;
}

class WorkoutSummaryDto {
  WorkoutSummaryDto({
    required this.id,
    required this.performedAt,
    required this.finishedAt,
    required this.status,
    required this.origin,
    required this.setsCount,
    required this.totalTonnage,
  });

  factory WorkoutSummaryDto.fromJson(Map<String, dynamic> json) =>
      WorkoutSummaryDto(
        id: json['id'] as String,
        performedAt: DateTime.parse(json['performed_at'] as String),
        finishedAt: json['finished_at'] == null
            ? null
            : DateTime.parse(json['finished_at'] as String),
        status: json['status'] as String,
        origin: json['origin'] as String,
        setsCount: (json['sets_count'] as num).toInt(),
        totalTonnage: (json['total_tonnage'] as num).toDouble(),
      );

  final String id;
  final DateTime performedAt;
  final DateTime? finishedAt;
  final String status;
  final String origin;
  final int setsCount;
  final double totalTonnage;
}

class WorkoutsApi {
  WorkoutsApi(this._dio);
  final Dio _dio;

  /// Старт тренировки. `planDayId != null` запускает её из дня плана
  /// (spec 005 REQ-12): бэк выставит `origin='plan'` и линкует FK.
  Future<WorkoutDto> start({String? planDayId}) async {
    return _try(() async {
      final body = <String, dynamic>{
        'origin': planDayId != null ? 'plan' : 'freestyle',
      };
      if (planDayId != null) body['plan_day_id'] = planDayId;
      final res = await _dio.post<Map<String, dynamic>>(
        '/workouts',
        data: body,
      );
      return WorkoutDto.fromJson(res.data!);
    });
  }

  Future<WorkoutDto?> active() async {
    return _try(() async {
      final res = await _dio.get<Map<String, dynamic>>('/workouts/active');
      if (res.data == null) return null;
      return WorkoutDto.fromJson(res.data!);
    });
  }

  Future<List<WorkoutSummaryDto>> history({int limit = 20, int offset = 0}) async {
    return _try(() async {
      final res = await _dio.get<Map<String, dynamic>>(
        '/workouts',
        queryParameters: {'limit': limit, 'offset': offset},
      );
      return (res.data!['items'] as List<dynamic>)
          .map((e) => WorkoutSummaryDto.fromJson(e as Map<String, dynamic>))
          .toList();
    });
  }

  Future<WorkoutDto> get(String workoutId) async {
    return _try(() async {
      final res =
          await _dio.get<Map<String, dynamic>>('/workouts/$workoutId');
      return WorkoutDto.fromJson(res.data!);
    });
  }

  Future<ExerciseLogDto> logSet(
    String workoutId, {
    required String exerciseId,
    required int setNumber,
    required int reps,
    required double weightKg,
    int? rpe,
    int? restSeconds,
  }) async {
    return _try(() async {
      final res = await _dio.post<Map<String, dynamic>>(
        '/workouts/$workoutId/logs',
        data: {
          'exercise_id': exerciseId,
          'set_number': setNumber,
          'reps': reps,
          'weight_kg': weightKg,
          if (rpe != null) 'rpe': rpe,
          if (restSeconds != null) 'rest_seconds': restSeconds,
        },
      );
      return ExerciseLogDto.fromJson(res.data!);
    });
  }

  Future<void> deleteLog(String workoutId, String logId) async {
    await _try(() => _dio.delete<void>('/workouts/$workoutId/logs/$logId'));
  }

  Future<WorkoutDto> finish(String workoutId) async {
    return _try(() async {
      final res =
          await _dio.post<Map<String, dynamic>>('/workouts/$workoutId/finish');
      return WorkoutDto.fromJson(res.data!);
    });
  }

  Future<void> cancel(String workoutId) async {
    await _try(() => _dio.post<void>('/workouts/$workoutId/cancel'));
  }

  Future<void> delete(String workoutId) async {
    await _try(() => _dio.delete<void>('/workouts/$workoutId'));
  }

  static Future<T> _try<T>(Future<T> Function() fn) async {
    try {
      return await fn();
    } on DioException catch (e) {
      throw mapDioToFailure(e);
    }
  }
}

final workoutsApiProvider =
    Provider<WorkoutsApi>((ref) => WorkoutsApi(ref.watch(dioProvider)));

final activeWorkoutProvider = FutureProvider.autoDispose<WorkoutDto?>(
  (ref) => ref.watch(workoutsApiProvider).active(),
);

final workoutHistoryProvider = FutureProvider.autoDispose<List<WorkoutSummaryDto>>(
  (ref) => ref.watch(workoutsApiProvider).history(),
);
