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

final _rootNavigatorKey = GlobalKey<NavigatorState>();

GoRouter createRouter(Ref ref) {
  return GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: '/login',
    refreshListenable: _AuthListenable(ref),
    redirect: (context, state) {
      final session = ref.read(authSessionProvider);
      final goingToAuth =
          state.matchedLocation == '/login' ||
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
      GoRoute(path: '/login', builder: (_, __) => const LoginScreen()),
      GoRoute(path: '/register', builder: (_, __) => const RegisterScreen()),
      // Активная тренировка вне shell — full-screen с собственным AppBar.
      GoRoute(
        path: '/training/active/:id',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (_, state) =>
            ActiveWorkoutScreen(workoutId: state.pathParameters['id']!),
      ),
      // Редактирование тренировки — full-screen модал поверх shell.
      GoRoute(
        path: '/training/edit/:id',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (_, state) =>
            EditWorkoutScreen(workoutId: state.pathParameters['id']!),
      ),
      // Импорт InBody-PDF — full-screen, вне shell (как модал).
      GoRoute(
        path: '/inbody/upload-pdf',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (_, __) => const InBodyPdfUploadScreen(),
      ),
      // Аналитика «Тело» — 3 графика (вес/жир/мышцы) + forecast overlay.
      // Полноэкранно с back, чтобы StatsScreen не превратился в скроллимое
      // полотно из шести экранов.
      GoRoute(
        path: '/analytics/body',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (_, __) => const BodyAnalyticsScreen(),
      ),
      // Экспорт PDF — full-screen «модал» по spec 010 §3 Sc.5: форма,
      // прогресс job'а, signed-URL для скачивания.
      GoRoute(
        path: '/analytics/export-pdf',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (_, __) => const ExportPdfScreen(),
      ),
      // Сравнение двух InBody-замеров (spec 010 §3 Sc.2, REQ-04).
      GoRoute(
        path: '/analytics/compare',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (_, __) => const CompareMeasurementsScreen(),
      ),
      // Аналитика тренировок: тоннаж + кол-во по неделям (REQ-07/08).
      GoRoute(
        path: '/analytics/workouts',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (_, __) => const WorkoutsAnalyticsScreen(),
      ),
      // Прогресс по конкретному упражнению (REQ-09).
      GoRoute(
        path: '/analytics/exercise',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (_, __) => const ExerciseProgressScreen(),
      ),
      // План тренировок (spec 006). Корневой экран — обзор + 4 вкладки;
      // тап по дню → /plan/day/:id; «Сгенерировать» — full-screen модал.
      GoRoute(
        path: '/plan',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (_, __) => const PlanOverviewScreen(),
        routes: [
          GoRoute(
            path: 'generate',
            builder: (_, __) => const PlanGenerateScreen(),
          ),
          GoRoute(
            path: 'day/:id',
            builder: (_, state) =>
                PlanDayScreen(dayId: state.pathParameters['id']!),
          ),
        ],
      ),
      StatefulShellRoute.indexedStack(
        builder: (_, __, navigationShell) =>
            HomeShell(navigationShell: navigationShell),
        branches: [
          StatefulShellBranch(
            routes: [
              GoRoute(path: '/home', builder: (_, __) => const HomeScreen()),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/training',
                builder: (_, __) => const TrainingTabScreen(),
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/stats',
                builder: (_, __) => const StatsScreen(),
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/profile',
                builder: (_, __) => const ProfileScreen(),
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
