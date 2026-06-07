import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_ru.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'generated/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale)
    : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations)!;
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
        delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
      ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[Locale('ru')];

  /// No description provided for @appName.
  ///
  /// In ru, this message translates to:
  /// **'Portal'**
  String get appName;

  /// No description provided for @appTagline.
  ///
  /// In ru, this message translates to:
  /// **'Прогноз состава тела'**
  String get appTagline;

  /// No description provided for @navHome.
  ///
  /// In ru, this message translates to:
  /// **'Главная'**
  String get navHome;

  /// No description provided for @navTraining.
  ///
  /// In ru, this message translates to:
  /// **'Тренировка'**
  String get navTraining;

  /// No description provided for @navStats.
  ///
  /// In ru, this message translates to:
  /// **'Статистика'**
  String get navStats;

  /// No description provided for @navProfile.
  ///
  /// In ru, this message translates to:
  /// **'Профиль'**
  String get navProfile;

  /// No description provided for @authLoginTitle.
  ///
  /// In ru, this message translates to:
  /// **'Portal'**
  String get authLoginTitle;

  /// No description provided for @authLoginSubtitle.
  ///
  /// In ru, this message translates to:
  /// **'Вход в аккаунт'**
  String get authLoginSubtitle;

  /// No description provided for @authEmailLabel.
  ///
  /// In ru, this message translates to:
  /// **'Email'**
  String get authEmailLabel;

  /// No description provided for @authEmailHint.
  ///
  /// In ru, this message translates to:
  /// **'you@example.com'**
  String get authEmailHint;

  /// No description provided for @authPasswordLabel.
  ///
  /// In ru, this message translates to:
  /// **'Пароль'**
  String get authPasswordLabel;

  /// No description provided for @authPasswordHint.
  ///
  /// In ru, this message translates to:
  /// **'••••••••'**
  String get authPasswordHint;

  /// No description provided for @authLoginCta.
  ///
  /// In ru, this message translates to:
  /// **'Войти'**
  String get authLoginCta;

  /// No description provided for @authForgotPassword.
  ///
  /// In ru, this message translates to:
  /// **'Забыли пароль?'**
  String get authForgotPassword;

  /// No description provided for @authNoAccount.
  ///
  /// In ru, this message translates to:
  /// **'Нет аккаунта?'**
  String get authNoAccount;

  /// No description provided for @authSignUp.
  ///
  /// In ru, this message translates to:
  /// **'Зарегистрироваться'**
  String get authSignUp;

  /// No description provided for @authRegisterTitle.
  ///
  /// In ru, this message translates to:
  /// **'Создание аккаунта'**
  String get authRegisterTitle;

  /// No description provided for @authRegisterSubtitle.
  ///
  /// In ru, this message translates to:
  /// **'Это займёт меньше минуты'**
  String get authRegisterSubtitle;

  /// No description provided for @authNameLabel.
  ///
  /// In ru, this message translates to:
  /// **'Имя'**
  String get authNameLabel;

  /// No description provided for @authNameHint.
  ///
  /// In ru, this message translates to:
  /// **'Ваше имя'**
  String get authNameHint;

  /// No description provided for @authAgreeTermsBefore.
  ///
  /// In ru, this message translates to:
  /// **'Принимаю'**
  String get authAgreeTermsBefore;

  /// No description provided for @authAgreeTermsAnd.
  ///
  /// In ru, this message translates to:
  /// **'и'**
  String get authAgreeTermsAnd;

  /// No description provided for @authTermsLink.
  ///
  /// In ru, this message translates to:
  /// **'условия'**
  String get authTermsLink;

  /// No description provided for @authPrivacyLink.
  ///
  /// In ru, this message translates to:
  /// **'политику конфиденциальности'**
  String get authPrivacyLink;

  /// No description provided for @authRegisterCta.
  ///
  /// In ru, this message translates to:
  /// **'Создать аккаунт'**
  String get authRegisterCta;

  /// No description provided for @authHasAccount.
  ///
  /// In ru, this message translates to:
  /// **'Уже есть аккаунт?'**
  String get authHasAccount;

  /// No description provided for @authLogIn.
  ///
  /// In ru, this message translates to:
  /// **'Войти'**
  String get authLogIn;

  /// No description provided for @homeStubTitle.
  ///
  /// In ru, this message translates to:
  /// **'Главная'**
  String get homeStubTitle;

  /// No description provided for @homeStubSubtitle.
  ///
  /// In ru, this message translates to:
  /// **'Здесь будет обзор: метрики, тренировки, прогресс'**
  String get homeStubSubtitle;

  /// No description provided for @homeTitle.
  ///
  /// In ru, this message translates to:
  /// **'Обзор'**
  String get homeTitle;

  /// No description provided for @homeSectionPerformance.
  ///
  /// In ru, this message translates to:
  /// **'Показатели'**
  String get homeSectionPerformance;

  /// No description provided for @homeSectionStrength.
  ///
  /// In ru, this message translates to:
  /// **'Прогресс в силе'**
  String get homeSectionStrength;

  /// No description provided for @homeSectionRecent.
  ///
  /// In ru, this message translates to:
  /// **'Последние тренировки'**
  String get homeSectionRecent;

  /// No description provided for @homeRecentViewAll.
  ///
  /// In ru, this message translates to:
  /// **'Все'**
  String get homeRecentViewAll;

  /// No description provided for @homeMetricWorkoutsThisMonth.
  ///
  /// In ru, this message translates to:
  /// **'Тренировок за месяц'**
  String get homeMetricWorkoutsThisMonth;

  /// No description provided for @homeMetricTotalWeight.
  ///
  /// In ru, this message translates to:
  /// **'Объём тренировок'**
  String get homeMetricTotalWeight;

  /// No description provided for @homeMetricTotalWeightUnit.
  ///
  /// In ru, this message translates to:
  /// **'кг'**
  String get homeMetricTotalWeightUnit;

  /// No description provided for @homeMetricVsLastMonth.
  ///
  /// In ru, this message translates to:
  /// **'{percent}% к прошлому месяцу'**
  String homeMetricVsLastMonth(String percent);

  /// No description provided for @homeMetricActiveStreak.
  ///
  /// In ru, this message translates to:
  /// **'Серия'**
  String get homeMetricActiveStreak;

  /// No description provided for @homeMetricActiveStreakDays.
  ///
  /// In ru, this message translates to:
  /// **'{count, plural, one{{count} день} few{{count} дня} many{{count} дней} other{{count} дней}}'**
  String homeMetricActiveStreakDays(int count);

  /// No description provided for @planExerciseCount.
  ///
  /// In ru, this message translates to:
  /// **'{count, plural, one{{count} упражнение} few{{count} упражнения} many{{count} упражнений} other{{count} упражнений}}'**
  String planExerciseCount(int count);

  /// No description provided for @planWeekCount.
  ///
  /// In ru, this message translates to:
  /// **'{count, plural, one{{count} неделя} few{{count} недели} many{{count} недель} other{{count} недель}}'**
  String planWeekCount(int count);

  /// No description provided for @homeMetricPersonalBest.
  ///
  /// In ru, this message translates to:
  /// **'Личный рекорд'**
  String get homeMetricPersonalBest;

  /// No description provided for @homeStrengthExercise.
  ///
  /// In ru, this message translates to:
  /// **'Жим лёжа'**
  String get homeStrengthExercise;

  /// No description provided for @homeStrengthLast30Days.
  ///
  /// In ru, this message translates to:
  /// **'За 30 дней'**
  String get homeStrengthLast30Days;

  /// No description provided for @homeStrengthUnit.
  ///
  /// In ru, this message translates to:
  /// **'кг'**
  String get homeStrengthUnit;

  /// No description provided for @homeActivitySetsRepsAt.
  ///
  /// In ru, this message translates to:
  /// **'{sets}×{reps} @ {weight} кг'**
  String homeActivitySetsRepsAt(int sets, int reps, int weight);

  /// No description provided for @trainingStubTitle.
  ///
  /// In ru, this message translates to:
  /// **'Тренировка'**
  String get trainingStubTitle;

  /// No description provided for @trainingStubSubtitle.
  ///
  /// In ru, this message translates to:
  /// **'Здесь появится план и активная тренировка'**
  String get trainingStubSubtitle;

  /// No description provided for @statsStubTitle.
  ///
  /// In ru, this message translates to:
  /// **'Статистика'**
  String get statsStubTitle;

  /// No description provided for @statsStubSubtitle.
  ///
  /// In ru, this message translates to:
  /// **'Графики веса, %% жира, мышечной массы и объёма тренировок'**
  String get statsStubSubtitle;

  /// No description provided for @profileStubTitle.
  ///
  /// In ru, this message translates to:
  /// **'Профиль'**
  String get profileStubTitle;

  /// No description provided for @profileStubSubtitle.
  ///
  /// In ru, this message translates to:
  /// **'Настройки, цели, InBody, выход из аккаунта'**
  String get profileStubSubtitle;
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['ru'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'ru':
      return AppLocalizationsRu();
  }

  throw FlutterError(
    'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
    'an issue with the localizations generation tool. Please file an issue '
    'on GitHub with a reproducible sample app and the gen-l10n configuration '
    'that was used.',
  );
}
