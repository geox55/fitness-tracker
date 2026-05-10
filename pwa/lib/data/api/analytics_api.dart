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

// ---------------------------------------------------------------------------
// Spec 010 §9 — InBody-серия (для графиков «Тело»)
// ---------------------------------------------------------------------------

/// Точка истории по одной метрике InBody.
class SeriesPointDto {
  SeriesPointDto({required this.date, required this.value});

  factory SeriesPointDto.fromJson(Map<String, dynamic> json) => SeriesPointDto(
        date: DateTime.parse(json['date'] as String),
        value: (json['value'] as num).toDouble(),
      );

  final DateTime date;
  final double value;
}

/// Точка прогноза с CI-полосой (overlay поверх графика истории, REQ-03).
class ForecastSeriesPointDto {
  ForecastSeriesPointDto({
    required this.date,
    required this.value,
    required this.ciLow,
    required this.ciHigh,
  });

  factory ForecastSeriesPointDto.fromJson(Map<String, dynamic> json) =>
      ForecastSeriesPointDto(
        date: DateTime.parse(json['date'] as String),
        value: (json['value'] as num).toDouble(),
        ciLow: (json['ci_low'] as num).toDouble(),
        ciHigh: (json['ci_high'] as num).toDouble(),
      );

  final DateTime date;
  final double value;
  final double ciLow;
  final double ciHigh;
}

class InBodySeriesResponseDto {
  InBodySeriesResponseDto({
    required this.metric,
    required this.points,
    required this.forecast,
  });

  factory InBodySeriesResponseDto.fromJson(Map<String, dynamic> json) {
    final fc = json['forecast'] as Map<String, dynamic>?;
    return InBodySeriesResponseDto(
      metric: json['metric'] as String,
      points: (json['points'] as List<dynamic>)
          .map((e) => SeriesPointDto.fromJson(e as Map<String, dynamic>))
          .toList(),
      forecast: fc == null
          ? null
          : (fc['points'] as List<dynamic>)
              .map((e) =>
                  ForecastSeriesPointDto.fromJson(e as Map<String, dynamic>))
              .toList(),
    );
  }

  final String metric;
  final List<SeriesPointDto> points;
  // null → метрика не из FORECASTABLE_METRICS spec 008 (например, bmi).
  final List<ForecastSeriesPointDto>? forecast;
}

// ---------------------------------------------------------------------------
// Spec 010 §9 — сравнение двух замеров (REQ-04)
// ---------------------------------------------------------------------------

class FieldDeltaDto {
  FieldDeltaDto({
    required this.field,
    required this.valueA,
    required this.valueB,
    required this.deltaAbsolute,
    required this.deltaPercent,
  });

  factory FieldDeltaDto.fromJson(Map<String, dynamic> json) => FieldDeltaDto(
        field: json['field'] as String,
        valueA: (json['value_a'] as num?)?.toDouble(),
        valueB: (json['value_b'] as num?)?.toDouble(),
        deltaAbsolute: (json['delta_absolute'] as num?)?.toDouble(),
        deltaPercent: (json['delta_percent'] as num?)?.toDouble(),
      );

  final String field;
  final double? valueA;
  final double? valueB;
  final double? deltaAbsolute;
  final double? deltaPercent;
}

class CompareMeasurementDto {
  CompareMeasurementDto({required this.id, required this.measuredAt});

  factory CompareMeasurementDto.fromJson(Map<String, dynamic> json) =>
      CompareMeasurementDto(
        id: json['id'] as String,
        measuredAt: DateTime.parse(json['measured_at'] as String),
      );

  final String id;
  final DateTime measuredAt;
}

class CompareResponseDto {
  CompareResponseDto({
    required this.a,
    required this.b,
    required this.deltas,
  });

  factory CompareResponseDto.fromJson(Map<String, dynamic> json) =>
      CompareResponseDto(
        a: CompareMeasurementDto.fromJson(json['a'] as Map<String, dynamic>),
        b: CompareMeasurementDto.fromJson(json['b'] as Map<String, dynamic>),
        deltas: (json['deltas'] as List<dynamic>)
            .map((e) => FieldDeltaDto.fromJson(e as Map<String, dynamic>))
            .toList(),
      );

  final CompareMeasurementDto a;
  final CompareMeasurementDto b;
  final List<FieldDeltaDto> deltas;
}

// ---------------------------------------------------------------------------
// Spec 010 §9 — тоннаж и кол-во тренировок по периодам (REQ-07/08)
// ---------------------------------------------------------------------------

class WorkoutsBucketDto {
  WorkoutsBucketDto({
    required this.periodStart,
    required this.tonnageKg,
    required this.workoutsCount,
  });

  factory WorkoutsBucketDto.fromJson(Map<String, dynamic> json) =>
      WorkoutsBucketDto(
        periodStart: DateTime.parse(json['period_start'] as String),
        tonnageKg: (json['tonnage_kg'] as num).toDouble(),
        workoutsCount: (json['workouts_count'] as num).toInt(),
      );

  final DateTime periodStart;
  final double tonnageKg;
  final int workoutsCount;
}

class WorkoutsAnalyticsResponseDto {
  WorkoutsAnalyticsResponseDto({required this.bucket, required this.items});

  factory WorkoutsAnalyticsResponseDto.fromJson(Map<String, dynamic> json) =>
      WorkoutsAnalyticsResponseDto(
        bucket: json['bucket'] as String,
        items: (json['items'] as List<dynamic>)
            .map((e) => WorkoutsBucketDto.fromJson(e as Map<String, dynamic>))
            .toList(),
      );

  final String bucket; // day | week | month
  final List<WorkoutsBucketDto> items;
}

// ---------------------------------------------------------------------------
// Spec 010 §3 Sc.3 — прогресс по цели (sealed: Data | Empty)
// ---------------------------------------------------------------------------

/// Один из двух payload'ов /analytics/goal-progress. UI делает
/// `switch (state) { GoalProgressDataDto → bar, GoalProgressEmptyDto → CTA }`.
sealed class GoalProgressDto {
  const GoalProgressDto();

  /// Дискриминатор: бэкенд возвращает либо `goal: ...`, либо `reason: ...`.
  /// Это надёжнее, чем сравнивать набор ключей.
  factory GoalProgressDto.fromJson(Map<String, dynamic> json) {
    if (json.containsKey('reason')) {
      return GoalProgressEmptyDto.fromJson(json);
    }
    return GoalProgressDataDto.fromJson(json);
  }
}

class GoalProgressDataDto extends GoalProgressDto {
  GoalProgressDataDto({
    required this.goal,
    required this.startValue,
    required this.currentValue,
    required this.targetValue,
    required this.progressPercent,
    required this.alreadyReached,
    required this.startedAt,
    required this.eta,
    required this.etaConfidence,
  });

  factory GoalProgressDataDto.fromJson(Map<String, dynamic> json) =>
      GoalProgressDataDto(
        goal: json['goal'] as String,
        startValue: (json['start_value'] as num).toDouble(),
        currentValue: (json['current_value'] as num).toDouble(),
        targetValue: (json['target_value'] as num).toDouble(),
        progressPercent: (json['progress_percent'] as num).toInt(),
        alreadyReached: json['already_reached'] as bool,
        startedAt: DateTime.parse(json['started_at'] as String),
        eta: json['eta'] == null ? null : DateTime.parse(json['eta'] as String),
        etaConfidence: json['eta_confidence'] as String?,
      );

  final String goal; // weight_loss | muscle_gain
  final double startValue;
  final double currentValue;
  final double targetValue;
  final int progressPercent;
  final bool alreadyReached;
  final DateTime startedAt;
  final DateTime? eta;
  final String? etaConfidence; // low | medium | high
}

class GoalProgressEmptyDto extends GoalProgressDto {
  GoalProgressEmptyDto({required this.reason, required this.missingFields});

  factory GoalProgressEmptyDto.fromJson(Map<String, dynamic> json) =>
      GoalProgressEmptyDto(
        reason: json['reason'] as String,
        missingFields: ((json['missing_fields'] as List<dynamic>?) ?? const [])
            .map((e) => e as String)
            .toList(),
      );

  /// no_goal_in_profile | no_target_set | no_inbody_measurements
  final String reason;
  final List<String> missingFields;
}

// ---------------------------------------------------------------------------
// API
// ---------------------------------------------------------------------------

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

  /// Серия одной метрики InBody + опц. overlay-прогноз.
  Future<InBodySeriesResponseDto> inbodySeries({
    required String metric,
    DateTime? from,
    DateTime? to,
    bool forecast = true,
  }) async {
    final qp = <String, dynamic>{'metric': metric, 'forecast': forecast};
    if (from != null) qp['from'] = _toDate(from);
    if (to != null) qp['to'] = _toDate(to);
    try {
      final res = await _dio.get<Map<String, dynamic>>(
        '/analytics/inbody',
        queryParameters: qp,
      );
      return InBodySeriesResponseDto.fromJson(res.data!);
    } on DioException catch (e) {
      throw mapDioToFailure(e);
    }
  }

  Future<CompareResponseDto> inbodyCompare({
    required String aId,
    required String bId,
  }) async {
    try {
      final res = await _dio.get<Map<String, dynamic>>(
        '/analytics/inbody/compare',
        queryParameters: {'a': aId, 'b': bId},
      );
      return CompareResponseDto.fromJson(res.data!);
    } on DioException catch (e) {
      throw mapDioToFailure(e);
    }
  }

  Future<WorkoutsAnalyticsResponseDto> workouts({
    String bucket = 'week',
    DateTime? from,
    DateTime? to,
  }) async {
    final qp = <String, dynamic>{'bucket': bucket};
    if (from != null) qp['from'] = _toDate(from);
    if (to != null) qp['to'] = _toDate(to);
    try {
      final res = await _dio.get<Map<String, dynamic>>(
        '/analytics/workouts',
        queryParameters: qp,
      );
      return WorkoutsAnalyticsResponseDto.fromJson(res.data!);
    } on DioException catch (e) {
      throw mapDioToFailure(e);
    }
  }

  Future<GoalProgressDto> goalProgress() async {
    try {
      final res = await _dio.get<Map<String, dynamic>>(
        '/analytics/goal-progress',
      );
      return GoalProgressDto.fromJson(res.data!);
    } on DioException catch (e) {
      throw mapDioToFailure(e);
    }
  }
}

/// `2026-05-10` без времени — бэкенд парсит query-param `date` именно так.
String _toDate(DateTime d) =>
    '${d.year.toString().padLeft(4, '0')}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}';

final analyticsApiProvider =
    Provider<AnalyticsApi>((ref) => AnalyticsApi(ref.watch(dioProvider)));

final overviewProvider = FutureProvider.autoDispose<OverviewResponseDto>(
  (ref) => ref.watch(analyticsApiProvider).overview(),
);

/// Прогресс по цели — отдельный провайдер; invalidate'им его при PATCH
/// профиля (target_*, goal, goal_started_at).
final goalProgressProvider = FutureProvider.autoDispose<GoalProgressDto>(
  (ref) => ref.watch(analyticsApiProvider).goalProgress(),
);

/// Серия одной InBody-метрики. Параметризованный family — экран «Тело»
/// просит три параллельно (weight_kg, body_fat_percent, muscle_mass_kg).
final inbodySeriesProvider = FutureProvider.autoDispose
    .family<InBodySeriesResponseDto, String>(
  (ref, metric) =>
      ref.watch(analyticsApiProvider).inbodySeries(metric: metric),
);

final workoutsAnalyticsProvider =
    FutureProvider.autoDispose<WorkoutsAnalyticsResponseDto>(
  (ref) => ref.watch(analyticsApiProvider).workouts(),
);
