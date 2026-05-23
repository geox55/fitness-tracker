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
// Spec 010 §9 — объём и кол-во тренировок по периодам (REQ-07/08)
// ---------------------------------------------------------------------------

/// Упражнение, по которому у пользователя есть хотя бы один лог.
/// Используется на экране «Прогресс по упражнению» как стартовый список.
class TrainedExerciseDto {
  TrainedExerciseDto({
    required this.id,
    required this.exerciseName,
    required this.exerciseNameRu,
    required this.primaryMuscleGroup,
    required this.equipment,
    required this.setsCount,
    required this.lastLoggedAt,
  });

  factory TrainedExerciseDto.fromJson(Map<String, dynamic> json) =>
      TrainedExerciseDto(
        id: json['id'] as String,
        exerciseName: json['exercise_name'] as String,
        exerciseNameRu: json['exercise_name_ru'] as String?,
        primaryMuscleGroup: json['primary_muscle_group'] as String,
        equipment: (json['equipment'] as List<dynamic>).cast<String>(),
        setsCount: (json['sets_count'] as num).toInt(),
        lastLoggedAt: DateTime.parse(json['last_logged_at'] as String),
      );

  final String id;
  final String exerciseName;
  final String? exerciseNameRu;
  final String primaryMuscleGroup;
  final List<String> equipment;
  final int setsCount;
  final DateTime lastLoggedAt;

  String get displayName => exerciseNameRu ?? exerciseName;
}

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
// Spec 010 §9 — прогресс по конкретному упражнению (REQ-09)
// ---------------------------------------------------------------------------

/// Один интервал серии — ISO-неделя (понедельник) с агрегатами по
/// упражнению: лучший рабочий вес, лучший оценочный 1RM по Эпли,
/// количество сетов и объём.
class ExerciseProgressWeekDto {
  ExerciseProgressWeekDto({
    required this.weekStart,
    required this.bestWeightKg,
    required this.bestE1rmKg,
    required this.sets,
    required this.tonnageKg,
  });

  factory ExerciseProgressWeekDto.fromJson(Map<String, dynamic> json) =>
      ExerciseProgressWeekDto(
        weekStart: DateTime.parse(json['week_start'] as String),
        bestWeightKg: (json['best_weight_kg'] as num).toDouble(),
        bestE1rmKg: (json['best_e1rm_kg'] as num).toDouble(),
        sets: (json['sets'] as num).toInt(),
        tonnageKg: (json['tonnage_kg'] as num).toDouble(),
      );

  final DateTime weekStart;
  final double bestWeightKg;
  final double bestE1rmKg;
  final int sets;
  final double tonnageKg;
}

class ExerciseProgressResponseDto {
  ExerciseProgressResponseDto({
    required this.exerciseId,
    required this.exerciseTitle,
    required this.weeks,
  });

  factory ExerciseProgressResponseDto.fromJson(Map<String, dynamic> json) =>
      ExerciseProgressResponseDto(
        exerciseId: json['exercise_id'] as String,
        exerciseTitle: json['exercise_title'] as String?,
        weeks: (json['weeks'] as List<dynamic>)
            .map((e) =>
                ExerciseProgressWeekDto.fromJson(e as Map<String, dynamic>))
            .toList(),
      );

  final String exerciseId;
  // null если у упражнения нет ни name_ru, ни name (на практике не бывает,
  // но схема разрешает).
  final String? exerciseTitle;
  final List<ExerciseProgressWeekDto> weeks;
}

// ---------------------------------------------------------------------------
// Spec 010 §3 Scenario 5 — экспорт PDF-отчёта (REQ-10..12)
// ---------------------------------------------------------------------------

/// Параметры запроса POST /analytics/export-pdf. Все поля опциональны:
/// без `from/to` — вся история; без `sections` — все четыре секции.
class ExportPdfRequestDto {
  ExportPdfRequestDto({this.from, this.to, this.sections});

  final DateTime? from;
  final DateTime? to;
  final List<String>? sections; // profile | inbody | workouts | goal

  Map<String, dynamic> toJson() {
    final out = <String, dynamic>{};
    if (from != null) out['from'] = _toDate(from!);
    if (to != null) out['to'] = _toDate(to!);
    if (sections != null) out['sections'] = sections;
    return out;
  }
}

/// 202 ответ на старте — клиент должен опрашивать GET по job_id.
class ExportPdfAcceptedDto {
  ExportPdfAcceptedDto({required this.jobId, required this.status});

  factory ExportPdfAcceptedDto.fromJson(Map<String, dynamic> json) =>
      ExportPdfAcceptedDto(
        jobId: json['job_id'] as String,
        status: json['status'] as String,
      );

  final String jobId;
  final String status; // pending | running | ready | failed
}

/// Полный статус job'а; `url`/`expiresAt` появляются только при `ready`,
/// `errorMessage` — только при `failed`. UI крутит поллинг с 0.5-1с
/// интервалом, пока status не станет терминальным.
class ExportPdfStatusDto {
  ExportPdfStatusDto({
    required this.jobId,
    required this.status,
    required this.sections,
    required this.createdAt,
    this.url,
    this.expiresAt,
    this.errorMessage,
    this.periodFrom,
    this.periodTo,
    this.readyAt,
  });

  factory ExportPdfStatusDto.fromJson(Map<String, dynamic> json) =>
      ExportPdfStatusDto(
        jobId: json['job_id'] as String,
        status: json['status'] as String,
        sections: (json['sections'] as List<dynamic>)
            .map((e) => e as String)
            .toList(),
        createdAt: DateTime.parse(json['created_at'] as String),
        url: json['url'] as String?,
        expiresAt: json['expires_at'] == null
            ? null
            : DateTime.parse(json['expires_at'] as String),
        errorMessage: json['error_message'] as String?,
        periodFrom: json['period_from'] == null
            ? null
            : DateTime.parse(json['period_from'] as String),
        periodTo: json['period_to'] == null
            ? null
            : DateTime.parse(json['period_to'] as String),
        readyAt: json['ready_at'] == null
            ? null
            : DateTime.parse(json['ready_at'] as String),
      );

  final String jobId;
  final String status;
  final List<String> sections;
  final DateTime createdAt;
  final String? url;
  final DateTime? expiresAt;
  final String? errorMessage;
  final DateTime? periodFrom;
  final DateTime? periodTo;
  final DateTime? readyAt;

  bool get isTerminal => status == 'ready' || status == 'failed';
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

  Future<List<TrainedExerciseDto>> trainedExercises() async {
    try {
      final res = await _dio.get<Map<String, dynamic>>(
        '/analytics/exercises-trained',
      );
      return (res.data!['items'] as List<dynamic>)
          .map((e) => TrainedExerciseDto.fromJson(e as Map<String, dynamic>))
          .toList();
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

  /// REQ-09: прогресс по конкретному упражнению.
  /// `exerciseId` — UUID из каталога; пустая история → `weeks` пустой
  /// (не ошибка). 404 поднимется как Failure, если такого упражнения
  /// нет в каталоге вовсе.
  Future<ExerciseProgressResponseDto> exerciseProgress({
    required String exerciseId,
    DateTime? from,
    DateTime? to,
  }) async {
    final qp = <String, dynamic>{'exercise_id': exerciseId};
    if (from != null) qp['from'] = _toDate(from);
    if (to != null) qp['to'] = _toDate(to);
    try {
      final res = await _dio.get<Map<String, dynamic>>(
        '/analytics/exercise-progress',
        queryParameters: qp,
      );
      return ExerciseProgressResponseDto.fromJson(res.data!);
    } on DioException catch (e) {
      throw mapDioToFailure(e);
    }
  }

  /// REQ-10: создать job на экспорт PDF. Сервер вернёт 202 с job_id;
  /// дальше — `getExportPdf(jobId)` в цикле, пока `isTerminal`.
  Future<ExportPdfAcceptedDto> startExportPdf(ExportPdfRequestDto req) async {
    try {
      final res = await _dio.post<Map<String, dynamic>>(
        '/analytics/export-pdf',
        data: req.toJson(),
      );
      return ExportPdfAcceptedDto.fromJson(res.data!);
    } on DioException catch (e) {
      throw mapDioToFailure(e);
    }
  }

  /// REQ-10: опросить статус job'а; при `ready` — в `url` свежий signed
  /// URL (TTL 1 час). Если истёк — клиент может ещё раз дёрнуть GET,
  /// signed URL пересоздаётся каждый запрос.
  Future<ExportPdfStatusDto> getExportPdf(String jobId) async {
    try {
      final res = await _dio.get<Map<String, dynamic>>(
        '/analytics/export-pdf/$jobId',
      );
      return ExportPdfStatusDto.fromJson(res.data!);
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

/// Параметры запроса /analytics/workouts. Используется параметрическим
/// провайдером ниже — выделено в типизированный value, чтобы Riverpod
/// корректно ловил equality.
class WorkoutsAnalyticsArgs {
  const WorkoutsAnalyticsArgs({
    required this.bucket,
    required this.from,
    this.to,
  });
  final String bucket; // day | week | month
  final DateTime? from;
  final DateTime? to;

  @override
  bool operator ==(Object other) =>
      other is WorkoutsAnalyticsArgs &&
      other.bucket == bucket &&
      other.from == from &&
      other.to == to;

  @override
  int get hashCode => Object.hash(bucket, from, to);
}

final workoutsAnalyticsFamily = FutureProvider.autoDispose
    .family<WorkoutsAnalyticsResponseDto, WorkoutsAnalyticsArgs>(
  (ref, args) => ref.watch(analyticsApiProvider).workouts(
        bucket: args.bucket,
        from: args.from,
        to: args.to,
      ),
);

/// Список упражнений, по которым у пользователя есть хотя бы один лог.
/// Используется как стартовый экран «Прогресс по упражнению».
final trainedExercisesProvider =
    FutureProvider.autoDispose<List<TrainedExerciseDto>>(
  (ref) => ref.watch(analyticsApiProvider).trainedExercises(),
);

/// Прогресс по конкретному упражнению — family по exercise_id.
/// Экран «Прогресс по упражнению» вызывает один раз с выбранным id;
/// при смене селекта получим свежий запрос.
final exerciseProgressProvider = FutureProvider.autoDispose
    .family<ExerciseProgressResponseDto, String>(
  (ref, exerciseId) => ref
      .watch(analyticsApiProvider)
      .exerciseProgress(exerciseId: exerciseId),
);

// --- Tips (рекомендации на основе ML-прогноза) ---------------------------

class TipDto {
  TipDto({
    required this.icon,
    required this.title,
    required this.body,
    required this.severity,
  });

  factory TipDto.fromJson(Map<String, dynamic> json) => TipDto(
        icon: json['icon'] as String,
        title: json['title'] as String,
        body: json['body'] as String,
        severity: json['severity'] as String,
      );

  final String icon;
  final String title;
  final String body;
  final String severity;
}

class TipsResponseDto {
  TipsResponseDto({required this.tips, required this.basedOnForecast});

  factory TipsResponseDto.fromJson(Map<String, dynamic> json) =>
      TipsResponseDto(
        tips: (json['tips'] as List<dynamic>)
            .map((e) => TipDto.fromJson(e as Map<String, dynamic>))
            .toList(),
        basedOnForecast: json['based_on_forecast'] as bool,
      );

  final List<TipDto> tips;
  final bool basedOnForecast;
}

final tipsProvider = FutureProvider.autoDispose<TipsResponseDto>((ref) async {
  final dio = ref.watch(dioProvider);
  try {
    final res = await dio.get<Map<String, dynamic>>('/forecast/inbody/tips');
    return TipsResponseDto.fromJson(res.data!);
  } on DioException catch (e) {
    throw mapDioToFailure(e);
  }
});
