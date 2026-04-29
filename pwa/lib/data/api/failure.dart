import 'package:dio/dio.dart';

/// Унифицированная ошибка для UI. Никаких DioException наружу не отдаём.
sealed class AppFailure implements Exception {
  const AppFailure(this.message);
  final String message;
}

class NetworkFailure extends AppFailure {
  const NetworkFailure() : super('Нет подключения к серверу');
}

class TimeoutFailure extends AppFailure {
  const TimeoutFailure() : super('Сервер не отвечает');
}

class UnauthorizedFailure extends AppFailure {
  const UnauthorizedFailure() : super('Неверный email или пароль');
}

class ApiFailure extends AppFailure {
  const ApiFailure({required this.code, required String message}) : super(message);
  final String code;
}

class UnexpectedFailure extends AppFailure {
  const UnexpectedFailure([String? msg]) : super(msg ?? 'Что-то пошло не так');
}

AppFailure mapDioToFailure(DioException e) {
  switch (e.type) {
    case DioExceptionType.connectionError:
    case DioExceptionType.unknown:
      return const NetworkFailure();
    case DioExceptionType.connectionTimeout:
    case DioExceptionType.receiveTimeout:
    case DioExceptionType.sendTimeout:
      return const TimeoutFailure();
    case DioExceptionType.badResponse:
      final status = e.response?.statusCode;
      final body = e.response?.data;
      if (status == 401) return const UnauthorizedFailure();
      // FastAPI стандарт: { "detail": { "error": "...", "message": "..." } }
      if (body is Map && body['detail'] is Map) {
        final detail = body['detail'] as Map;
        return ApiFailure(
          code: (detail['error'] as String?) ?? 'api_error',
          message:
              (detail['message'] as String?) ?? 'Ошибка ${status ?? "сервера"}',
        );
      }
      // FastAPI ValidationError 422: { "detail": [ { "loc": [...], "msg": "..." } ] }
      if (status == 422) {
        return const ApiFailure(
          code: 'validation_error',
          message: 'Проверьте введённые данные',
        );
      }
      return UnexpectedFailure('Ошибка $status');
    case DioExceptionType.cancel:
    case DioExceptionType.badCertificate:
      return const UnexpectedFailure();
  }
}
