import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'api_client.dart';
import 'failure.dart';

/// DTO профиля. Все поля кроме user_id/email/updated_at могут быть null —
/// пользователь заполняет их постепенно через онбординг или PATCH.
class ProfileDto {
  ProfileDto({
    required this.userId,
    required this.email,
    required this.name,
    required this.sex,
    required this.birthDate,
    required this.heightCm,
    required this.baselineWeightKg,
    required this.goal,
    required this.targetWeightKg,
    required this.targetMuscleKg,
    required this.goalStartedAt,
    required this.trainingLevel,
    required this.trainingFrequency,
    required this.allergies,
    required this.equipmentAvailable,
    required this.photoUrl,
    required this.bmrKcal,
    required this.onboardingCompletedAt,
    required this.planRebuildRequired,
    required this.updatedAt,
  });

  factory ProfileDto.fromJson(Map<String, dynamic> json) => ProfileDto(
        userId: json['user_id'] as String,
        email: json['email'] as String,
        name: json['name'] as String?,
        sex: json['sex'] as String?,
        birthDate: json['birth_date'] == null
            ? null
            : DateTime.parse(json['birth_date'] as String),
        heightCm: (json['height_cm'] as num?)?.toDouble(),
        baselineWeightKg: (json['baseline_weight_kg'] as num?)?.toDouble(),
        goal: json['goal'] as String?,
        targetWeightKg: (json['target_weight_kg'] as num?)?.toDouble(),
        targetMuscleKg: (json['target_muscle_kg'] as num?)?.toDouble(),
        goalStartedAt: json['goal_started_at'] == null
            ? null
            : DateTime.parse(json['goal_started_at'] as String),
        trainingLevel: json['training_level'] as String?,
        trainingFrequency: (json['training_frequency'] as num?)?.toInt(),
        allergies: ((json['allergies'] as List<dynamic>?) ?? const [])
            .map((e) => e as String)
            .toList(),
        equipmentAvailable: (json['equipment_available'] as List<dynamic>?)
            ?.map((e) => e as String)
            .toList(),
        photoUrl: json['photo_url'] as String?,
        bmrKcal: (json['bmr_kcal'] as num?)?.toInt(),
        onboardingCompletedAt: json['onboarding_completed_at'] == null
            ? null
            : DateTime.parse(json['onboarding_completed_at'] as String),
        planRebuildRequired: json['plan_rebuild_required'] as bool,
        updatedAt: DateTime.parse(json['updated_at'] as String),
      );

  final String userId;
  final String email;
  final String? name;
  final String? sex;
  final DateTime? birthDate;
  final double? heightCm;
  final double? baselineWeightKg;
  final String? goal;
  // Прогресс по цели (spec 010 §3 Sc.3): без target_* раздел рисует CTA.
  final double? targetWeightKg;
  final double? targetMuscleKg;
  // Дата старта работы над целью; нужна, чтобы старт прогресса не привязывался
  // к самому первому ever-замеру (когда юзер мог иметь другой goal).
  final DateTime? goalStartedAt;
  final String? trainingLevel;
  final int? trainingFrequency;
  final List<String> allergies;
  // null — пользователь не настраивал (тогда генератор плана берёт типовой
  // коммерческий зал по умолчанию); [] — явно «ничего нет», только bodyweight;
  // непустой список — настроенный набор (spec 004 REQ-09).
  final List<String>? equipmentAvailable;
  final String? photoUrl;
  final int? bmrKcal;
  final DateTime? onboardingCompletedAt;
  final bool planRebuildRequired;
  final DateTime updatedAt;

  bool get hasOnboarded => onboardingCompletedAt != null;
}

class ProfileApi {
  ProfileApi(this._dio);
  final Dio _dio;

  Future<ProfileDto> get() async {
    try {
      final res = await _dio.get<Map<String, dynamic>>('/profile');
      return ProfileDto.fromJson(res.data!);
    } on DioException catch (e) {
      throw mapDioToFailure(e);
    }
  }

  /// PATCH принимает любое подмножество полей. Передаём только non-null значения,
  /// чтобы случайно не стереть существующее.
  Future<ProfileDto> patch({
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
    // null = «не трогаем» (как и для остальных полей PATCH); [] и непустой
    // список передаются как есть. Сбросить в NULL из UI пока не нужно
    // (пользователь либо настраивает, либо оставляет «по умолчанию»).
    List<String>? equipmentAvailable,
  }) async {
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

    try {
      final res = await _dio.patch<Map<String, dynamic>>(
        '/profile',
        data: body,
      );
      return ProfileDto.fromJson(res.data!);
    } on DioException catch (e) {
      throw mapDioToFailure(e);
    }
  }

  Future<ProfileDto> uploadPhoto({
    required List<int> bytes,
    required String filename,
    required String contentType,
  }) async {
    try {
      final form = FormData.fromMap({
        'file': MultipartFile.fromBytes(
          bytes,
          filename: filename,
          contentType: DioMediaType.parse(contentType),
        ),
      });
      final res = await _dio.post<Map<String, dynamic>>(
        '/profile/photo',
        data: form,
        options: Options(contentType: 'multipart/form-data'),
      );
      return ProfileDto.fromJson(res.data!);
    } on DioException catch (e) {
      throw mapDioToFailure(e);
    }
  }

  Future<ProfileDto> deletePhoto() async {
    try {
      final res = await _dio.delete<Map<String, dynamic>>('/profile/photo');
      return ProfileDto.fromJson(res.data!);
    } on DioException catch (e) {
      throw mapDioToFailure(e);
    }
  }

  Future<ProfileDto> completeOnboarding() async {
    try {
      final res = await _dio.post<Map<String, dynamic>>(
        '/profile/complete-onboarding',
      );
      return ProfileDto.fromJson(res.data!);
    } on DioException catch (e) {
      throw mapDioToFailure(e);
    }
  }
}

final profileApiProvider = Provider<ProfileApi>(
  (ref) => ProfileApi(ref.watch(dioProvider)),
);

/// Кэш-провайдер: главный экран и шапка читают один и тот же снимок профиля.
/// invalidate(profileProvider) после PATCH/upload/delete.
final profileProvider = FutureProvider.autoDispose<ProfileDto>(
  (ref) => ref.watch(profileApiProvider).get(),
);
