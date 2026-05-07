import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'api_client.dart';
import 'failure.dart';

/// Статусы PdfImportJob — соответствуют backend (spec 013 §6).
enum PdfJobStatus {
  parsing,
  ready,
  partial,
  failed,
  notInbody,
  encrypted,
  scannedUnsupported,
  unknown;

  static PdfJobStatus fromJson(String raw) => switch (raw) {
        'parsing' => PdfJobStatus.parsing,
        'ready' => PdfJobStatus.ready,
        'partial' => PdfJobStatus.partial,
        'failed' => PdfJobStatus.failed,
        'not_inbody' => PdfJobStatus.notInbody,
        'encrypted' => PdfJobStatus.encrypted,
        'scanned_unsupported' => PdfJobStatus.scannedUnsupported,
        _ => PdfJobStatus.unknown,
      };

  bool get isConfirmable =>
      this == PdfJobStatus.ready || this == PdfJobStatus.partial;
}

/// Превью распознанных полей. Все поля опциональны — берём только то,
/// что вернул backend; UI прорисовывает их с пометкой confidence.
class PdfJobDto {
  PdfJobDto({
    required this.id,
    required this.status,
    required this.template,
    required this.extracted,
    required this.confidence,
    required this.missingFields,
    required this.errorMessage,
    required this.createdAt,
    required this.confirmedAt,
  });

  factory PdfJobDto.fromJson(Map<String, dynamic> json) => PdfJobDto(
        id: json['id'] as String,
        status: PdfJobStatus.fromJson(json['status'] as String),
        template: json['template'] as String?,
        extracted: Map<String, dynamic>.from(
          json['extracted'] as Map? ?? const {},
        ),
        confidence: Map<String, dynamic>.from(
          json['confidence'] as Map? ?? const {},
        ),
        missingFields: ((json['missing_fields'] as List?) ?? const [])
            .map((e) => e as String)
            .toList(),
        errorMessage: json['error_message'] as String?,
        createdAt: DateTime.parse(json['created_at'] as String),
        confirmedAt: json['confirmed_at'] == null
            ? null
            : DateTime.parse(json['confirmed_at'] as String),
      );

  final String id;
  final PdfJobStatus status;
  final String? template;
  final Map<String, dynamic> extracted;
  final Map<String, dynamic> confidence;
  final List<String> missingFields;
  final String? errorMessage;
  final DateTime createdAt;
  final DateTime? confirmedAt;
}

/// Минимум, что нужно UI после confirm — id и параметры созданного замера.
/// Берём только то, что показываем на success-экране.
class CreatedMeasurementDto {
  CreatedMeasurementDto({
    required this.id,
    required this.measuredAt,
    required this.weightKg,
    required this.bodyFatPercent,
  });

  factory CreatedMeasurementDto.fromJson(Map<String, dynamic> json) =>
      CreatedMeasurementDto(
        id: json['id'] as String,
        measuredAt: DateTime.parse(json['measured_at'] as String),
        weightKg: (json['weight_kg'] as num).toDouble(),
        bodyFatPercent: (json['body_fat_percent'] as num).toDouble(),
      );

  final String id;
  final DateTime measuredAt;
  final double weightKg;
  final double bodyFatPercent;
}

class InBodyPdfApi {
  InBodyPdfApi(this._dio);
  final Dio _dio;

  Future<PdfJobDto> upload({
    required List<int> bytes,
    required String filename,
  }) async {
    try {
      final form = FormData.fromMap({
        'file': MultipartFile.fromBytes(
          bytes,
          filename: filename,
          contentType: DioMediaType.parse('application/pdf'),
        ),
      });
      final res = await _dio.post<Map<String, dynamic>>(
        '/inbody/measurements/from-pdf',
        data: form,
        options: Options(contentType: 'multipart/form-data'),
      );
      return PdfJobDto.fromJson(res.data!);
    } on DioException catch (e) {
      throw mapDioToFailure(e);
    }
  }

  Future<PdfJobDto> getJob(String jobId) async {
    try {
      final res = await _dio.get<Map<String, dynamic>>(
        '/inbody/measurements/from-pdf/$jobId',
      );
      return PdfJobDto.fromJson(res.data!);
    } on DioException catch (e) {
      throw mapDioToFailure(e);
    }
  }

  /// Подтвердить импорт. `overrides` — поля, которые пользователь поправил
  /// в превью; `measuredAt` берётся из формы (по умолчанию — сейчас).
  Future<CreatedMeasurementDto> confirm({
    required String jobId,
    required DateTime measuredAt,
    Map<String, dynamic>? overrides,
  }) async {
    try {
      final body = <String, dynamic>{
        'measured_at': measuredAt.toUtc().toIso8601String(),
        if (overrides != null && overrides.isNotEmpty) 'overrides': overrides,
      };
      final res = await _dio.post<Map<String, dynamic>>(
        '/inbody/measurements/from-pdf/$jobId/confirm',
        data: body,
      );
      final data = (res.data!['measurement'] as Map<String, dynamic>);
      return CreatedMeasurementDto.fromJson(data);
    } on DioException catch (e) {
      throw mapDioToFailure(e);
    }
  }
}

final inBodyPdfApiProvider = Provider<InBodyPdfApi>(
  (ref) => InBodyPdfApi(ref.watch(dioProvider)),
);
