import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../app/env.dart';
import 'auth_interceptor.dart';

/// Базовый Dio-клиент с auth-interceptor'ом.
Dio _buildDio(Ref ref, {String? baseUrl}) {
  final dio = Dio(
    BaseOptions(
      baseUrl: baseUrl ?? AppEnv.apiBaseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 30),
      headers: {'Content-Type': 'application/json'},
      validateStatus: (s) => s != null && s < 400,
    ),
  );
  dio.interceptors.add(AuthInterceptor(ref));
  return dio;
}

final dioProvider = Provider<Dio>(_buildDio);
