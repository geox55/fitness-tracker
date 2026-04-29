import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:fitness_tracker/app/app.dart';

void main() {
  testWidgets('app boots and shows login screen by default', (tester) async {
    await tester.pumpWidget(const ProviderScope(child: FitnessTrackerApp()));
    await tester.pumpAndSettle();

    // На стартовом экране — логин (заголовок «Фитнес-трекер» в шапке).
    expect(find.text('Фитнес-трекер'), findsWidgets);
  });
}
