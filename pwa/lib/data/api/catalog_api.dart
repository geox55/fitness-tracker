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
      );

  final String id;
  final String exerciseId;
  final String name;
  final String? nameRu;
  final String primaryMuscleGroup;
  final List<String> equipment;
  final String bodyRegion;

  String get displayName => nameRu ?? name;
}

class ExerciseListResult {
  ExerciseListResult({required this.items, required this.total});
  final List<ExerciseSummaryDto> items;
  final int total;
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
    try {
      final res = await _dio.get<Map<String, dynamic>>(
        '/exercises',
        queryParameters: {
          if (query != null && query.length >= 2) 'q': query,
          if (muscleGroup != null) 'muscle_group': muscleGroup,
          'limit': limit,
          'offset': offset,
        },
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
