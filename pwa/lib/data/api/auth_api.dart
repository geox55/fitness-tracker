import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'api_client.dart';
import 'failure.dart';

class TokenPair {
  TokenPair({
    required this.accessToken,
    required this.refreshToken,
    required this.expiresIn,
  });

  factory TokenPair.fromJson(Map<String, dynamic> json) => TokenPair(
        accessToken: json['access_token'] as String,
        refreshToken: json['refresh_token'] as String,
        expiresIn: json['expires_in'] as int,
      );

  final String accessToken;
  final String refreshToken;
  final int expiresIn;
}

class MeResponse {
  MeResponse({
    required this.id,
    required this.email,
    required this.emailStatus,
  });

  factory MeResponse.fromJson(Map<String, dynamic> json) => MeResponse(
        id: json['id'] as String,
        email: json['email'] as String,
        emailStatus: json['email_status'] as String,
      );

  final String id;
  final String email;
  final String emailStatus;
}

class AuthApi {
  AuthApi(this._dio);
  final Dio _dio;

  Future<({String userId, String emailStatus})> register({
    required String email,
    required String password,
    String? name,
  }) async {
    final body = <String, dynamic>{'email': email, 'password': password};
    if (name != null && name.trim().isNotEmpty) body['name'] = name.trim();
    final res = await _safe(() => _dio.post<Map<String, dynamic>>(
          '/auth/register',
          data: body,
        ));
    return (
      userId: res!['user_id'] as String,
      emailStatus: res['email_status'] as String,
    );
  }

  Future<TokenPair> login({
    required String email,
    required String password,
  }) async {
    final res = await _safe(() => _dio.post<Map<String, dynamic>>(
          '/auth/login',
          data: {'email': email, 'password': password},
        ));
    return TokenPair.fromJson(res!);
  }

  /// Обмен refresh-токена на новую пару. Сервер делает rotation: refresh_token
  /// в ответе — новый, старый помечается used. Бросает AppFailure с code
  /// 'refresh_invalid' или 'refresh_reused' при провале.
  Future<TokenPair> refresh(String refreshToken) async {
    final res = await _safe(() => _dio.post<Map<String, dynamic>>(
          '/auth/refresh',
          data: {'refresh_token': refreshToken},
        ));
    return TokenPair.fromJson(res!);
  }

  Future<void> logout(String refreshToken) async {
    try {
      await _dio.post<void>(
        '/auth/logout',
        data: {'refresh_token': refreshToken},
      );
    } on DioException {
      // Logout идемпотентен на бэке — игнорируем сетевые ошибки на выходе.
    }
  }

  Future<MeResponse> me({required String accessToken}) async {
    final res = await _safe(() => _dio.get<Map<String, dynamic>>(
          '/profile/me',
          options: Options(headers: {'Authorization': 'Bearer $accessToken'}),
        ));
    return MeResponse.fromJson(res!);
  }

  Future<void> forgotPassword({required String email}) async {
    try {
      await _dio.post<Map<String, dynamic>>(
        '/auth/forgot-password',
        data: {'email': email},
      );
    } on DioException catch (e) {
      throw mapDioToFailure(e);
    }
  }

  static Future<Map<String, dynamic>?> _safe(
    Future<Response<Map<String, dynamic>>> Function() fn,
  ) async {
    try {
      final response = await fn();
      return response.data;
    } on DioException catch (e) {
      throw mapDioToFailure(e);
    }
  }
}

final authApiProvider = Provider<AuthApi>((ref) => AuthApi(ref.watch(dioProvider)));
