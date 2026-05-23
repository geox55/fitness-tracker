// Клиент для CRUD InBody-замеров (spec 003). Используется на экране
// «Сравнить замеры» — список даёт два селектора по дате (REQ-04).
//
// PDF-импорт живёт в `inbody_pdf_api.dart` — это отдельный поток.

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'api_client.dart';
import 'failure.dart';

/// DTO одного замера. Снапшот основных полей; для compare-экрана важна
/// дата + id, остальные мы тоже отображаем при выборе.
class MeasurementDto {
  MeasurementDto({
    required this.id,
    required this.measuredAt,
    required this.weightKg,
    required this.bodyFatPercent,
    required this.muscleMassKg,
    required this.source,
  });

  factory MeasurementDto.fromJson(Map<String, dynamic> json) => MeasurementDto(
        id: json['id'] as String,
        measuredAt: DateTime.parse(json['measured_at'] as String),
        weightKg: (json['weight_kg'] as num).toDouble(),
        bodyFatPercent: (json['body_fat_percent'] as num).toDouble(),
        muscleMassKg: (json['muscle_mass_kg'] as num?)?.toDouble(),
        source: json['source'] as String,
      );

  final String id;
  final DateTime measuredAt;
  final double weightKg;
  final double bodyFatPercent;
  final double? muscleMassKg;
  final String source; // manual | pdf
}

class MeasurementListResponseDto {
  MeasurementListResponseDto({required this.items, required this.total});

  factory MeasurementListResponseDto.fromJson(Map<String, dynamic> json) =>
      MeasurementListResponseDto(
        items: (json['items'] as List<dynamic>)
            .map((e) => MeasurementDto.fromJson(e as Map<String, dynamic>))
            .toList(),
        total: (json['total'] as num).toInt(),
      );

  final List<MeasurementDto> items;
  final int total;
}

class InBodyApi {
  InBodyApi(this._dio);
  final Dio _dio;

  Future<MeasurementDto> create({
    required DateTime measuredAt,
    required double weightKg,
    required double bodyFatPercent,
    double? muscleMassKg,
  }) async {
    try {
      final res = await _dio.post<Map<String, dynamic>>(
        '/inbody/measurements',
        data: {
          'measured_at': measuredAt.toUtc().toIso8601String(),
          'weight_kg': weightKg,
          'body_fat_percent': bodyFatPercent,
          if (muscleMassKg != null) 'muscle_mass_kg': muscleMassKg,
        },
      );
      return MeasurementDto.fromJson(res.data!);
    } on DioException catch (e) {
      throw mapDioToFailure(e);
    }
  }

  /// Список замеров пользователя, отсортированный backend'ом по
  /// `measured_at desc` (см. `list_for_user`). Для compare-селектора
  /// достаточно лимита в 100 — спецификация ограничивает PDF-историю
  /// 50 страницами, на одну сторону этого с запасом хватает.
  Future<MeasurementListResponseDto> list({
    int limit = 100,
    int offset = 0,
  }) async {
    try {
      final res = await _dio.get<Map<String, dynamic>>(
        '/inbody/measurements',
        queryParameters: {'limit': limit, 'offset': offset},
      );
      return MeasurementListResponseDto.fromJson(res.data!);
    } on DioException catch (e) {
      throw mapDioToFailure(e);
    }
  }
}

final inBodyApiProvider = Provider<InBodyApi>(
  (ref) => InBodyApi(ref.watch(dioProvider)),
);

/// Список всех замеров пользователя — используется compare-экраном
/// для двух селекторов. AutoDispose: после выхода с экрана отпускаем.
final measurementsListProvider =
    FutureProvider.autoDispose<MeasurementListResponseDto>(
  (ref) => ref.watch(inBodyApiProvider).list(),
);
