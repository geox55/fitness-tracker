import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/api/auth_api.dart';

/// Состояние авторизации.
enum AuthStatus { unknown, unauthenticated, authenticated }

class AuthSession {
  const AuthSession({
    required this.status,
    this.accessToken,
    this.refreshToken,
    this.userId,
    this.email,
  });

  const AuthSession.unauthenticated()
      : status = AuthStatus.unauthenticated,
        accessToken = null,
        refreshToken = null,
        userId = null,
        email = null;

  final AuthStatus status;
  final String? accessToken;
  final String? refreshToken;
  final String? userId;
  final String? email;

  bool get isAuthenticated => status == AuthStatus.authenticated;
  bool get isUnauthenticated => status == AuthStatus.unauthenticated;
}

class AuthSessionController extends Notifier<AuthSession> {
  @override
  AuthSession build() => const AuthSession.unauthenticated();

  /// Реальный логин: дёргаем API, сохраняем токены.
  Future<void> login({required String email, required String password}) async {
    final api = ref.read(authApiProvider);
    final pair = await api.login(email: email, password: password);
    final me = await api.me(accessToken: pair.accessToken);
    state = AuthSession(
      status: AuthStatus.authenticated,
      accessToken: pair.accessToken,
      refreshToken: pair.refreshToken,
      userId: me.id,
      email: me.email,
    );
  }

  /// Регистрация + автологин — UX дизайна предполагает «создать и сразу войти».
  Future<void> registerAndLogin({
    required String email,
    required String password,
  }) async {
    final api = ref.read(authApiProvider);
    await api.register(email: email, password: password);
    await login(email: email, password: password);
  }

  /// Подменить токены без полного login: после успешного refresh-rotation
  /// нам нужен только новый access/refresh, userId/email остаются.
  void applyTokens(String accessToken, String refreshToken) {
    final current = state;
    state = AuthSession(
      status: AuthStatus.authenticated,
      accessToken: accessToken,
      refreshToken: refreshToken,
      userId: current.userId,
      email: current.email,
    );
  }

  /// Локальный signOut без вызова сервера. Используется interceptor'ом, когда
  /// refresh-токен уже невалиден — сетевой вызов был бы бессмыслен.
  void signOut() => state = const AuthSession.unauthenticated();

  /// Полноценный logout с серверным revoke refresh-токена. Используется
  /// кнопкой «Выйти».
  Future<void> logout() async {
    final refresh = state.refreshToken;
    if (refresh != null) {
      await ref.read(authApiProvider).logout(refresh);
    }
    state = const AuthSession.unauthenticated();
  }
}

final authSessionProvider =
    NotifierProvider<AuthSessionController, AuthSession>(AuthSessionController.new);
