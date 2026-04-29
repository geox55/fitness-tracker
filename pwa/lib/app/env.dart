/// Конфигурация уровня сборки. Перекрывается через --dart-define.
///
/// Пример запуска c кастомным URL:
///   flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8080/api/v1
abstract final class AppEnv {
  static const apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8080/api/v1',
  );
}
