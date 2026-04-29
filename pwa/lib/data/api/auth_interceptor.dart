import 'dart:async';

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../features/auth/auth_state.dart';
import 'api_client.dart';
import 'auth_api.dart';

/// Interceptor авторизации:
///
/// 1. Подкладывает текущий access-токен в Authorization-header.
/// 2. На 401 пытается единожды обновить пару через /auth/refresh и повторить
///    оригинальный запрос с новым токеном.
/// 3. Сериализует параллельные refresh'ы через единый Future, иначе 5
///    одновременных 401 отправят 5 refresh-запросов и сервер срабатает
///    reuse-detection (rotation помечает старый токен used → второй
///    параллельный запрос увидит «used» → 401 refresh_reused → инвалидация
///    всех сессий).
/// 4. На повторный 401 после refresh, на refresh_reused/refresh_invalid и
///    отсутствие refresh-токена — signOut, чтобы UI перебросило на /login.
class AuthInterceptor extends Interceptor {
  AuthInterceptor(this._ref);
  final Ref _ref;

  /// Открытый refresh-полёт. Если несколько запросов одновременно получили
  /// 401, они дожидаются того же Future и повторяются с обновлённым access.
  Future<bool>? _refreshing;

  // Маркер на RequestOptions: запрос уже был повторён, второй раз refresh не
  // делаем (иначе loop при системной 401).
  static const _retriedKey = '__auth_retried__';

  static const _refreshPath = '/auth/refresh';
  static const _logoutPath = '/auth/logout';

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    final token = _ref.read(authSessionProvider).accessToken;
    if (token != null && options.headers['Authorization'] == null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    super.onRequest(options, handler);
  }

  @override
  Future<void> onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    final response = err.response;
    final request = err.requestOptions;

    // Чужие ошибки и не-401 — пробрасываем дальше без изменений.
    if (response?.statusCode != 401 ||
        request.path == _refreshPath ||
        request.path == _logoutPath ||
        request.extra[_retriedKey] == true) {
      return handler.next(err);
    }

    final session = _ref.read(authSessionProvider);
    final refreshToken = session.refreshToken;
    if (refreshToken == null) {
      _ref.read(authSessionProvider.notifier).signOut();
      return handler.next(err);
    }

    // Сериализуем refresh: первый запрос запускает _doRefresh, остальные
    // ждут тот же future.
    final ok = await (_refreshing ??= _doRefresh(refreshToken));
    if (!ok) {
      // refresh не получился — все ждавшие выкидываются на /login.
      return handler.next(err);
    }

    // Повторяем оригинальный запрос с новым токеном через тот же Dio.
    // _retriedKey защитит от рекурсии: interceptor пропустит повторный 401.
    final newToken = _ref.read(authSessionProvider).accessToken;
    request.headers['Authorization'] = 'Bearer $newToken';
    request.extra[_retriedKey] = true;
    try {
      final retried = await _ref.read(dioProvider).fetch<dynamic>(request);
      return handler.resolve(retried);
    } on DioException catch (e) {
      return handler.next(e);
    }
  }

  Future<bool> _doRefresh(String refreshToken) async {
    try {
      final api = _ref.read(authApiProvider);
      final pair = await api.refresh(refreshToken);
      _ref
          .read(authSessionProvider.notifier)
          .applyTokens(pair.accessToken, pair.refreshToken);
      return true;
    } on Object {
      // Refresh-токен невалиден / reused / истёк — выходим из аккаунта.
      _ref.read(authSessionProvider.notifier).signOut();
      return false;
    } finally {
      _refreshing = null;
    }
  }
}
