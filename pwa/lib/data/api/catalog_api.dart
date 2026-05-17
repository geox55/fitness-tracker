import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'api_client.dart';
import 'failure.dart';

class ExerciseSummaryDto {
  ExerciseSummaryDto({
    required this.id,
    required this.exerciseId,
    required this.name,
    required this.nameRu,
    required this.primaryMuscleGroup,
    required this.equipment,
    required this.bodyRegion,
    required this.isFavorite,
    required this.isMine,
  });

  factory ExerciseSummaryDto.fromJson(Map<String, dynamic> json) =>
      ExerciseSummaryDto(
        id: json['id'] as String,
        exerciseId: json['exercise_id'] as String,
        name: json['exercise_name'] as String,
        nameRu: json['exercise_name_ru'] as String?,
        primaryMuscleGroup: json['primary_muscle_group'] as String,
        equipment: (json['equipment'] as List<dynamic>).cast<String>(),
        bodyRegion: json['body_region'] as String,
        // Старые ответы (до spec 014) не содержат флагов — дефолтимся в false,
        // чтобы клиент не падал во время раскатки.
        isFavorite: (json['is_favorite'] as bool?) ?? false,
        isMine: (json['is_mine'] as bool?) ?? false,
      );

  final String id;
  final String exerciseId;
  final String name;
  final String? nameRu;
  final String primaryMuscleGroup;
  final List<String> equipment;
  final String bodyRegion;
  final bool isFavorite;
  final bool isMine;

  String get displayName => nameRu ?? name;

  /// Возвращает копию с переключённым isFavorite — для оптимистичного UI:
  /// сначала перерисовать звезду, потом дёрнуть API.
  ExerciseSummaryDto copyWithFavorite(bool value) => ExerciseSummaryDto(
        id: id,
        exerciseId: exerciseId,
        name: name,
        nameRu: nameRu,
        primaryMuscleGroup: primaryMuscleGroup,
        equipment: equipment,
        bodyRegion: bodyRegion,
        isFavorite: value,
        isMine: isMine,
      );
}

class ExerciseListResult {
  ExerciseListResult({required this.items, required this.total});
  final List<ExerciseSummaryDto> items;
  final int total;
}

/// Поля для создания/редактирования своего упражнения. Все обязательные
/// поля у create — обязательные; у patch — все опциональные (передаём только
/// то, что меняется).
class ExerciseEditFields {
  ExerciseEditFields({
    this.name,
    this.nameRu,
    this.primaryMuscleGroup,
    this.secondaryMuscleGroup,
    this.equipment,
    this.bodyRegion,
  });

  final String? name;
  final String? nameRu;
  final String? primaryMuscleGroup;
  final List<String>? secondaryMuscleGroup;
  final List<String>? equipment;
  final String? bodyRegion;

  Map<String, dynamic> toJson() => {
        if (name != null) 'exercise_name': name,
        if (nameRu != null) 'exercise_name_ru': nameRu,
        if (primaryMuscleGroup != null) 'primary_muscle_group': primaryMuscleGroup,
        if (secondaryMuscleGroup != null)
          'secondary_muscle_group': secondaryMuscleGroup,
        if (equipment != null) 'equipment': equipment,
        if (bodyRegion != null) 'body_region': bodyRegion,
      };
}

class CatalogApi {
  CatalogApi(this._dio);
  final Dio _dio;

  Future<ExerciseListResult> list({
    String? query,
    String? muscleGroup,
    int limit = 30,
    int offset = 0,
  }) async {
    return _getList(
      '/exercises',
      queryParameters: {
        if (query != null && query.length >= 2) 'q': query,
        if (muscleGroup != null) 'muscle_group': muscleGroup,
        'limit': limit,
        'offset': offset,
      },
    );
  }

  Future<ExerciseListResult> listFavorites() => _getList('/exercises/favorites');

  Future<ExerciseListResult> listMine() => _getList('/exercises/mine');

  Future<void> addFavorite(String exerciseId) async {
    try {
      await _dio.post<void>('/exercises/$exerciseId/favorite');
    } on DioException catch (e) {
      throw mapDioToFailure(e);
    }
  }

  Future<void> removeFavorite(String exerciseId) async {
    try {
      await _dio.delete<void>('/exercises/$exerciseId/favorite');
    } on DioException catch (e) {
      throw mapDioToFailure(e);
    }
  }

  Future<ExerciseSummaryDto> createOwned(ExerciseEditFields fields) async {
    try {
      final res = await _dio.post<Map<String, dynamic>>(
        '/exercises',
        data: fields.toJson(),
      );
      return ExerciseSummaryDto.fromJson(res.data!);
    } on DioException catch (e) {
      throw mapDioToFailure(e);
    }
  }

  Future<ExerciseSummaryDto> updateOwned(
    String exerciseId,
    ExerciseEditFields fields,
  ) async {
    try {
      final res = await _dio.patch<Map<String, dynamic>>(
        '/exercises/$exerciseId',
        data: fields.toJson(),
      );
      return ExerciseSummaryDto.fromJson(res.data!);
    } on DioException catch (e) {
      throw mapDioToFailure(e);
    }
  }

  Future<void> deleteOwned(String exerciseId) async {
    try {
      await _dio.delete<void>('/exercises/$exerciseId');
    } on DioException catch (e) {
      throw mapDioToFailure(e);
    }
  }

  Future<ExerciseListResult> _getList(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) async {
    try {
      final res = await _dio.get<Map<String, dynamic>>(
        path,
        queryParameters: queryParameters,
      );
      final data = res.data!;
      return ExerciseListResult(
        items: (data['items'] as List<dynamic>)
            .map((e) => ExerciseSummaryDto.fromJson(e as Map<String, dynamic>))
            .toList(),
        total: (data['total'] as num).toInt(),
      );
    } on DioException catch (e) {
      throw mapDioToFailure(e);
    }
  }
}

final catalogApiProvider =
    Provider<CatalogApi>((ref) => CatalogApi(ref.watch(dioProvider)));
