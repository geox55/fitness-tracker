import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/api/auth_api.dart';
import 'auth_storage.dart';

/// Состояние авторизации.
///
/// `unknown` нужен, чтобы router'у понять «мы ещё не закончили первый
/// hydration из storage» и не редиректнуть пользователя на /login до
/// того, как мы прочитали сохранённые токены. Иначе на cold-start
/// браузера-вкладки идёт мерцание /home → /login → /home.
enum AuthStatus { unknown, unauthenticated, authenticated }

class AuthSession {
  const AuthSession({
    required this.status,
    this.accessToken,
    this.refreshToken,
    this.userId,
    this.email,
  });

  const AuthSession.unknown()
      : status = AuthStatus.unknown,
        accessToken = null,
        refreshToken = null,
        userId = null,
        email = null;

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
  bool get isUnknown => status == AuthStatus.unknown;
}

/// Provider обёртка над AuthStorage. Один экземпляр на жизнь приложения;
/// хранит SharedPreferences-handle. Создаётся через override в
/// `main.dart` (см. `runApp` ниже): мы не можем синхронно инициализировать
/// SharedPreferences, поэтому делаем это до runApp.
final authStorageProvider = Provider<AuthStorage>(
  (_) => throw UnimplementedError(
    'authStorageProvider must be overridden in main()',
  ),
);

class AuthSessionController extends Notifier<AuthSession> {
  @override
  AuthSession build() {
    // На cold-start состояние «unknown»; restore() поднимет токены из
    // storage и переключит на authenticated, либо unauthenticated.
    // Это синхронный вызов — read() не дёргает сеть, только prefs.
    final stored = ref.read(authStorageProvider).read();
    if (stored == null) {
      return const AuthSession.unauthenticated();
    }
    return AuthSession(
      status: AuthStatus.authenticated,
      accessToken: stored.accessToken,
      refreshToken: stored.refreshToken,
      userId: stored.userId,
      email: stored.email,
    );
  }

  /// Реальный логин: дёргаем API, сохраняем токены.
  Future<void> login({required String email, required String password}) async {
    final api = ref.read(authApiProvider);
    final pair = await api.login(email: email, password: password);
    final me = await api.me(accessToken: pair.accessToken);
    final newSession = AuthSession(
      status: AuthStatus.authenticated,
      accessToken: pair.accessToken,
      refreshToken: pair.refreshToken,
      userId: me.id,
      email: me.email,
    );
    state = newSession;
    await ref.read(authStorageProvider).save(
          PersistedSession(
            accessToken: pair.accessToken,
            refreshToken: pair.refreshToken,
            userId: me.id,
            email: me.email,
          ),
        );
  }

  /// Регистрация + автологин — UX дизайна предполагает «создать и сразу войти».
  /// `name` опционален: если передан — сразу попадает в UserProfile, чтобы
  /// при первом заходе в /profile поле уже было заполнено.
  Future<void> registerAndLogin({
    required String email,
    required String password,
    String? name,
  }) async {
    final api = ref.read(authApiProvider);
    await api.register(email: email, password: password, name: name);
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
    // Persistence — fire-and-forget, не блокируем interceptor.
    unawaited(
      ref.read(authStorageProvider).updateTokens(
            accessToken: accessToken,
            refreshToken: refreshToken,
          ),
    );
  }

  /// Локальный signOut без вызова сервера. Используется interceptor'ом, когда
  /// refresh-токен уже невалиден — сетевой вызов был бы бессмыслен.
  void signOut() {
    state = const AuthSession.unauthenticated();
    unawaited(ref.read(authStorageProvider).clear());
  }

  /// Полноценный logout с серверным revoke refresh-токена. Используется
  /// кнопкой «Выйти».
  Future<void> logout() async {
    final refresh = state.refreshToken;
    if (refresh != null) {
      await ref.read(authApiProvider).logout(refresh);
    }
    state = const AuthSession.unauthenticated();
    await ref.read(authStorageProvider).clear();
  }
}

final authSessionProvider =
    NotifierProvider<AuthSessionController, AuthSession>(AuthSessionController.new);
