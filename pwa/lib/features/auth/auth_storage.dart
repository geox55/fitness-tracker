// Persistence слой для auth-токенов. На Flutter Web shared_preferences под
// капотом — localStorage; на мобильных — нативный KV. Один interface,
// один контракт.
//
// Что храним:
// - access_token (короткоживущий, ≈15 мин)
// - refresh_token (долгоживущий, ≈30 дней)
// - user_id, email — чтобы при cold-start сразу построить AuthSession без
//   обязательного похода в /profile/me (пойдём за свежим me лениво).
//
// Безопасность: refresh-токен в localStorage уязвим к XSS. Для MVP это
// принятая модель; следующий шаг — backend выдаёт httpOnly secure cookie
// и токен из storage уходит. Не делаем сейчас, потому что цикл «на двоих»
// и так не закрывается; пометка для будущей итерации.

import 'package:shared_preferences/shared_preferences.dart';

class AuthStorage {
  AuthStorage(this._prefs);
  final SharedPreferences _prefs;

  static const _kAccess = 'auth.access_token';
  static const _kRefresh = 'auth.refresh_token';
  static const _kUserId = 'auth.user_id';
  static const _kEmail = 'auth.email';

  static Future<AuthStorage> create() async {
    final prefs = await SharedPreferences.getInstance();
    return AuthStorage(prefs);
  }

  /// `null` если каких-то ключей нет: приложение трактует как unauth.
  PersistedSession? read() {
    final access = _prefs.getString(_kAccess);
    final refresh = _prefs.getString(_kRefresh);
    final userId = _prefs.getString(_kUserId);
    final email = _prefs.getString(_kEmail);
    if (access == null || refresh == null || userId == null || email == null) {
      return null;
    }
    return PersistedSession(
      accessToken: access,
      refreshToken: refresh,
      userId: userId,
      email: email,
    );
  }

  Future<void> save(PersistedSession s) async {
    // Атомарностью SharedPreferences не парится — каждое set отдельно;
    // в read() мы тем не менее не падаем при «частично записанном»
    // состоянии (требуем все 4 ключа).
    await _prefs.setString(_kAccess, s.accessToken);
    await _prefs.setString(_kRefresh, s.refreshToken);
    await _prefs.setString(_kUserId, s.userId);
    await _prefs.setString(_kEmail, s.email);
  }

  /// Обновить только токены (refresh-rotation). userId/email не трогаем —
  /// они привязаны к аккаунту, а не к сессии.
  Future<void> updateTokens({
    required String accessToken,
    required String refreshToken,
  }) async {
    await _prefs.setString(_kAccess, accessToken);
    await _prefs.setString(_kRefresh, refreshToken);
  }

  Future<void> clear() async {
    await _prefs.remove(_kAccess);
    await _prefs.remove(_kRefresh);
    await _prefs.remove(_kUserId);
    await _prefs.remove(_kEmail);
  }
}

class PersistedSession {
  const PersistedSession({
    required this.accessToken,
    required this.refreshToken,
    required this.userId,
    required this.email,
  });

  final String accessToken;
  final String refreshToken;
  final String userId;
  final String email;
}
