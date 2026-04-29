import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'api_client.dart';
import 'failure.dart';

class OverviewMetricsDto {
  OverviewMetricsDto({
    required this.workoutsThisMonth,
    required this.totalWeightKg,
    required this.totalWeightDeltaPercent,
    required this.activeStreakDays,
    required this.streakIsPersonalBest,
  });

  factory OverviewMetricsDto.fromJson(Map<String, dynamic> json) =>
      OverviewMetricsDto(
        workoutsThisMonth: (json['workouts_this_month'] as num).toInt(),
        totalWeightKg: (json['total_weight_kg'] as num).toInt(),
        totalWeightDeltaPercent:
            (json['total_weight_delta_percent'] as num).toInt(),
        activeStreakDays: (json['active_streak_days'] as num).toInt(),
        streakIsPersonalBest: json['streak_is_personal_best'] as bool,
      );

  final int workoutsThisMonth;
  final int totalWeightKg;
  final int totalWeightDeltaPercent;
  final int activeStreakDays;
  final bool streakIsPersonalBest;
}

class StrengthPointDto {
  StrengthPointDto({required this.dayOffset, required this.weightKg});

  factory StrengthPointDto.fromJson(Map<String, dynamic> json) => StrengthPointDto(
        dayOffset: (json['day_offset'] as num).toInt(),
        weightKg: (json['weight_kg'] as num).toDouble(),
      );

  final int dayOffset;
  final double weightKg;
}

class StrengthProgressDto {
  StrengthProgressDto({
    required this.exerciseTitle,
    required this.currentMaxKg,
    required this.points,
  });

  factory StrengthProgressDto.fromJson(Map<String, dynamic> json) =>
      StrengthProgressDto(
        exerciseTitle: json['exercise_title'] as String?,
        currentMaxKg: (json['current_max_kg'] as num).toInt(),
        points: (json['points'] as List<dynamic>)
            .map((e) => StrengthPointDto.fromJson(e as Map<String, dynamic>))
            .toList(),
      );

  final String? exerciseTitle;
  final int currentMaxKg;
  final List<StrengthPointDto> points;
}

class RecentWorkoutDto {
  RecentWorkoutDto({
    required this.id,
    required this.dayLabel,
    required this.title,
    required this.sets,
    required this.reps,
    required this.weightKg,
    required this.kind,
  });

  factory RecentWorkoutDto.fromJson(Map<String, dynamic> json) => RecentWorkoutDto(
        id: json['id'] as String,
        dayLabel: json['day_label'] as String,
        title: json['title'] as String,
        sets: (json['sets'] as num).toInt(),
        reps: (json['reps'] as num).toInt(),
        weightKg: (json['weight_kg'] as num).toInt(),
        kind: json['kind'] as String,
      );

  final String id;
  final String dayLabel;
  final String title;
  final int sets;
  final int reps;
  final int weightKg;
  final String kind;
}

class OverviewResponseDto {
  OverviewResponseDto({
    required this.metrics,
    required this.strength,
    required this.recent,
  });

  factory OverviewResponseDto.fromJson(Map<String, dynamic> json) =>
      OverviewResponseDto(
        metrics: OverviewMetricsDto.fromJson(
          json['metrics'] as Map<String, dynamic>,
        ),
        strength: json['strength'] == null
            ? null
            : StrengthProgressDto.fromJson(
                json['strength'] as Map<String, dynamic>,
              ),
        recent: (json['recent'] as List<dynamic>)
            .map((e) => RecentWorkoutDto.fromJson(e as Map<String, dynamic>))
            .toList(),
      );

  final OverviewMetricsDto metrics;
  final StrengthProgressDto? strength;
  final List<RecentWorkoutDto> recent;
}

class AnalyticsApi {
  AnalyticsApi(this._dio);
  final Dio _dio;

  Future<OverviewResponseDto> overview() async {
    try {
      final res = await _dio.get<Map<String, dynamic>>('/analytics/overview');
      return OverviewResponseDto.fromJson(res.data!);
    } on DioException catch (e) {
      throw mapDioToFailure(e);
    }
  }
}

final analyticsApiProvider =
    Provider<AnalyticsApi>((ref) => AnalyticsApi(ref.watch(dioProvider)));

final overviewProvider = FutureProvider.autoDispose<OverviewResponseDto>(
  (ref) => ref.watch(analyticsApiProvider).overview(),
);
