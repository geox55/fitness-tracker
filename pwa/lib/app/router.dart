import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../features/analytics/body_screen.dart';
import '../features/analytics/compare_measurements_screen.dart';
import '../features/analytics/exercise_progress_screen.dart';
import '../features/analytics/export_pdf_screen.dart';
import '../features/analytics/workouts_screen.dart';
import '../features/auth/auth_state.dart';
import '../features/auth/login_screen.dart';
import '../features/auth/register_screen.dart';
import '../features/home/home_screen.dart';
import '../features/inbody/inbody_pdf_upload_screen.dart';
import '../features/plan/plan_day_screen.dart';
import '../features/plan/plan_generate_screen.dart';
import '../features/plan/plan_overview_screen.dart';
import '../features/profile/profile_screen.dart';
import '../features/shell/home_shell.dart';
import '../features/stats/stats_screen.dart';
import '../features/workouts/active_workout_screen.dart';
import '../features/workouts/edit_workout_screen.dart';
import '../features/workouts/training_tab_screen.dart';
import '../features/workouts/workout_detail_screen.dart';

final _rootNavigatorKey = GlobalKey<NavigatorState>();

/// Все route'ы используют мгновенный page-transition без анимации —
/// глобальный PortalBackdrop (см. app.dart) лежит под всеми экранами,
/// и любая slide/fade-анимация переходов накладывает старый прозрачный
/// scaffold на новый, давая визуальный "duplicate". NoTransitionPage
/// убирает анимацию полностью: новый экран появляется поверх старого
/// мгновенно, фон под ним непрерывен.
NoTransitionPage<T> _page<T>(LocalKey? key, Widget child) {
  return NoTransitionPage<T>(key: key, child: child);
}

GoRouter createRouter(Ref ref) {
  return GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: '/login',
    refreshListenable: _AuthListenable(ref),
    redirect: (context, state) {
      final session = ref.read(authSessionProvider);
      final goingToAuth = state.matchedLocation == '/login' ||
          state.matchedLocation == '/register';

      if (session.isUnauthenticated && !goingToAuth) {
        return '/login';
      }
      if (session.isAuthenticated && goingToAuth) {
        return '/home';
      }
      return null;
    },
    routes: [
      GoRoute(
        path: '/login',
        pageBuilder: (_, state) => _page(state.pageKey, const LoginScreen()),
      ),
      GoRoute(
        path: '/register',
        pageBuilder: (_, state) =>
            _page(state.pageKey, const RegisterScreen()),
      ),
      // Активная тренировка вне shell — full-screen с собственным AppBar.
      GoRoute(
        path: '/training/active/:id',
        parentNavigatorKey: _rootNavigatorKey,
        pageBuilder: (_, state) => _page(
          state.pageKey,
          ActiveWorkoutScreen(workoutId: state.pathParameters['id']!),
        ),
      ),
      // Редактирование тренировки — full-screen модал поверх shell.
      GoRoute(
        path: '/training/edit/:id',
        parentNavigatorKey: _rootNavigatorKey,
        pageBuilder: (_, state) => _page(
          state.pageKey,
          EditWorkoutScreen(workoutId: state.pathParameters['id']!),
        ),
      ),
      // Read-only детали тренировки — список упражнений с подходами.
      // Тап на карточку из Главной/Тренировки/Статистики ведёт сюда.
      GoRoute(
        path: '/training/view/:id',
        parentNavigatorKey: _rootNavigatorKey,
        pageBuilder: (_, state) => _page(
          state.pageKey,
          WorkoutDetailScreen(workoutId: state.pathParameters['id']!),
        ),
      ),
      // Импорт InBody-PDF — full-screen, вне shell (как модал).
      GoRoute(
        path: '/inbody/upload-pdf',
        parentNavigatorKey: _rootNavigatorKey,
        pageBuilder: (_, state) =>
            _page(state.pageKey, const InBodyPdfUploadScreen()),
      ),
      // Аналитика «Тело» — 3 графика (вес/жир/мышцы) + forecast overlay.
      GoRoute(
        path: '/analytics/body',
        parentNavigatorKey: _rootNavigatorKey,
        pageBuilder: (_, state) =>
            _page(state.pageKey, const BodyAnalyticsScreen()),
      ),
      // Экспорт PDF — full-screen «модал» по spec 010 §3 Sc.5.
      GoRoute(
        path: '/analytics/export-pdf',
        parentNavigatorKey: _rootNavigatorKey,
        pageBuilder: (_, state) =>
            _page(state.pageKey, const ExportPdfScreen()),
      ),
      // Сравнение двух InBody-замеров (spec 010 §3 Sc.2, REQ-04).
      GoRoute(
        path: '/analytics/compare',
        parentNavigatorKey: _rootNavigatorKey,
        pageBuilder: (_, state) =>
            _page(state.pageKey, const CompareMeasurementsScreen()),
      ),
      // Аналитика тренировок: объём + кол-во по неделям (REQ-07/08).
      GoRoute(
        path: '/analytics/workouts',
        parentNavigatorKey: _rootNavigatorKey,
        pageBuilder: (_, state) =>
            _page(state.pageKey, const WorkoutsAnalyticsScreen()),
      ),
      // Прогресс по конкретному упражнению (REQ-09).
      GoRoute(
        path: '/analytics/exercise',
        parentNavigatorKey: _rootNavigatorKey,
        pageBuilder: (_, state) =>
            _page(state.pageKey, const ExerciseProgressScreen()),
      ),
      // План тренировок (spec 006).
      GoRoute(
        path: '/plan',
        parentNavigatorKey: _rootNavigatorKey,
        pageBuilder: (_, state) =>
            _page(state.pageKey, const PlanOverviewScreen()),
        routes: [
          GoRoute(
            path: 'generate',
            pageBuilder: (_, state) =>
                _page(state.pageKey, const PlanGenerateScreen()),
          ),
          GoRoute(
            path: 'day/:id',
            pageBuilder: (_, state) => _page(
              state.pageKey,
              PlanDayScreen(dayId: state.pathParameters['id']!),
            ),
          ),
        ],
      ),
      StatefulShellRoute.indexedStack(
        builder: (_, __, navigationShell) =>
            HomeShell(navigationShell: navigationShell),
        branches: [
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/home',
                pageBuilder: (_, state) =>
                    _page(state.pageKey, const HomeScreen()),
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/training',
                pageBuilder: (_, state) =>
                    _page(state.pageKey, const TrainingTabScreen()),
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/stats',
                pageBuilder: (_, state) =>
                    _page(state.pageKey, const StatsScreen()),
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/profile',
                pageBuilder: (_, state) =>
                    _page(state.pageKey, const ProfileScreen()),
              ),
            ],
          ),
        ],
      ),
    ],
  );
}

/// go_router принимает [Listenable], поэтому оборачиваем Riverpod-провайдер.
class _AuthListenable extends ChangeNotifier {
  _AuthListenable(this._ref) {
    _ref.listen(authSessionProvider, (_, __) => notifyListeners());
  }
  final Ref _ref;
}

final routerProvider = Provider<GoRouter>(createRouter);
