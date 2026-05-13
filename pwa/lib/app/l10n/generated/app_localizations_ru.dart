// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Russian (`ru`).
class AppLocalizationsRu extends AppLocalizations {
  AppLocalizationsRu([String locale = 'ru']) : super(locale);

  @override
  String get appName => 'Фитнес-трекер';

  @override
  String get appTagline => 'Учёт тренировок и состава тела';

  @override
  String get navHome => 'Главная';

  @override
  String get navTraining => 'Тренировка';

  @override
  String get navStats => 'Статистика';

  @override
  String get navProfile => 'Профиль';

  @override
  String get authLoginTitle => 'Фитнес-трекер';

  @override
  String get authLoginSubtitle => 'Вход в аккаунт';

  @override
  String get authEmailLabel => 'Email';

  @override
  String get authEmailHint => 'you@example.com';

  @override
  String get authPasswordLabel => 'Пароль';

  @override
  String get authPasswordHint => '••••••••';

  @override
  String get authLoginCta => 'Войти';

  @override
  String get authForgotPassword => 'Забыли пароль?';

  @override
  String get authNoAccount => 'Нет аккаунта?';

  @override
  String get authSignUp => 'Зарегистрироваться';

  @override
  String get authRegisterTitle => 'Создание аккаунта';

  @override
  String get authRegisterSubtitle => 'Это займёт меньше минуты';

  @override
  String get authNameLabel => 'Имя';

  @override
  String get authNameHint => 'Ваше имя';

  @override
  String get authAgreeTermsBefore => 'Принимаю';

  @override
  String get authAgreeTermsAnd => 'и';

  @override
  String get authTermsLink => 'условия';

  @override
  String get authPrivacyLink => 'политику конфиденциальности';

  @override
  String get authRegisterCta => 'Создать аккаунт';

  @override
  String get authHasAccount => 'Уже есть аккаунт?';

  @override
  String get authLogIn => 'Войти';

  @override
  String get homeStubTitle => 'Главная';

  @override
  String get homeStubSubtitle =>
      'Здесь будет обзор: метрики, тренировки, прогресс';

  @override
  String get homeTitle => 'Обзор';

  @override
  String get homeMonthDecember2025 => 'Декабрь 2025';

  @override
  String get homeSectionPerformance => 'Показатели';

  @override
  String get homeSectionStrength => 'Прогресс в силе';

  @override
  String get homeSectionRecent => 'Последние тренировки';

  @override
  String get homeRecentViewAll => 'Все';

  @override
  String get homeMetricWorkoutsThisMonth => 'Тренировок за месяц';

  @override
  String get homeMetricTotalWeight => 'Общий тоннаж';

  @override
  String get homeMetricTotalWeightUnit => 'кг';

  @override
  String homeMetricVsLastMonth(String percent) {
    return '$percent% к прошлому месяцу';
  }

  @override
  String get homeMetricActiveStreak => 'Серия';

  @override
  String homeMetricActiveStreakDays(int count) {
    final intl.NumberFormat countNumberFormat =
        intl.NumberFormat.decimalPattern(localeName);
    final String countString = countNumberFormat.format(count);

    String _temp0 = intl.Intl.pluralLogic(
      count,
      locale: localeName,
      other: '$countString дней',
      many: '$countString дней',
      few: '$countString дня',
      one: '$countString день',
    );
    return '$_temp0';
  }

  @override
  String get homeMetricPersonalBest => 'Личный рекорд';

  @override
  String get homeStrengthExercise => 'Жим лёжа';

  @override
  String get homeStrengthLast30Days => 'За 30 дней';

  @override
  String get homeStrengthUnit => 'кг';

  @override
  String homeActivitySetsRepsAt(int sets, int reps, int weight) {
    return '$sets×$reps @ $weight кг';
  }

  @override
  String get trainingStubTitle => 'Тренировка';

  @override
  String get trainingStubSubtitle =>
      'Здесь появится план и активная тренировка';

  @override
  String get statsStubTitle => 'Статистика';

  @override
  String get statsStubSubtitle =>
      'Графики веса, %% жира, мышечной массы и тоннажа';

  @override
  String get profileStubTitle => 'Профиль';

  @override
  String get profileStubSubtitle =>
      'Настройки, цели, InBody, выход из аккаунта';
}
