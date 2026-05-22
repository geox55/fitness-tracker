// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'database.dart';

// ignore_for_file: type=lint
class $ProfilesTable extends Profiles with TableInfo<$ProfilesTable, Profile> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $ProfilesTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _userIdMeta = const VerificationMeta('userId');
  @override
  late final GeneratedColumn<String> userId = GeneratedColumn<String>(
    'user_id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _emailMeta = const VerificationMeta('email');
  @override
  late final GeneratedColumn<String> email = GeneratedColumn<String>(
    'email',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _nameMeta = const VerificationMeta('name');
  @override
  late final GeneratedColumn<String> name = GeneratedColumn<String>(
    'name',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _sexMeta = const VerificationMeta('sex');
  @override
  late final GeneratedColumn<String> sex = GeneratedColumn<String>(
    'sex',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _birthDateMeta = const VerificationMeta(
    'birthDate',
  );
  @override
  late final GeneratedColumn<DateTime> birthDate = GeneratedColumn<DateTime>(
    'birth_date',
    aliasedName,
    true,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _heightCmMeta = const VerificationMeta(
    'heightCm',
  );
  @override
  late final GeneratedColumn<double> heightCm = GeneratedColumn<double>(
    'height_cm',
    aliasedName,
    true,
    type: DriftSqlType.double,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _baselineWeightKgMeta = const VerificationMeta(
    'baselineWeightKg',
  );
  @override
  late final GeneratedColumn<double> baselineWeightKg = GeneratedColumn<double>(
    'baseline_weight_kg',
    aliasedName,
    true,
    type: DriftSqlType.double,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _goalMeta = const VerificationMeta('goal');
  @override
  late final GeneratedColumn<String> goal = GeneratedColumn<String>(
    'goal',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _targetWeightKgMeta = const VerificationMeta(
    'targetWeightKg',
  );
  @override
  late final GeneratedColumn<double> targetWeightKg = GeneratedColumn<double>(
    'target_weight_kg',
    aliasedName,
    true,
    type: DriftSqlType.double,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _targetMuscleKgMeta = const VerificationMeta(
    'targetMuscleKg',
  );
  @override
  late final GeneratedColumn<double> targetMuscleKg = GeneratedColumn<double>(
    'target_muscle_kg',
    aliasedName,
    true,
    type: DriftSqlType.double,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _goalStartedAtMeta = const VerificationMeta(
    'goalStartedAt',
  );
  @override
  late final GeneratedColumn<DateTime> goalStartedAt =
      GeneratedColumn<DateTime>(
        'goal_started_at',
        aliasedName,
        true,
        type: DriftSqlType.dateTime,
        requiredDuringInsert: false,
      );
  static const VerificationMeta _trainingLevelMeta = const VerificationMeta(
    'trainingLevel',
  );
  @override
  late final GeneratedColumn<String> trainingLevel = GeneratedColumn<String>(
    'training_level',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _trainingFrequencyMeta = const VerificationMeta(
    'trainingFrequency',
  );
  @override
  late final GeneratedColumn<int> trainingFrequency = GeneratedColumn<int>(
    'training_frequency',
    aliasedName,
    true,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _allergiesJsonMeta = const VerificationMeta(
    'allergiesJson',
  );
  @override
  late final GeneratedColumn<String> allergiesJson = GeneratedColumn<String>(
    'allergies_json',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant('[]'),
  );
  static const VerificationMeta _equipmentAvailableJsonMeta =
      const VerificationMeta('equipmentAvailableJson');
  @override
  late final GeneratedColumn<String> equipmentAvailableJson =
      GeneratedColumn<String>(
        'equipment_available_json',
        aliasedName,
        true,
        type: DriftSqlType.string,
        requiredDuringInsert: false,
      );
  static const VerificationMeta _photoUrlMeta = const VerificationMeta(
    'photoUrl',
  );
  @override
  late final GeneratedColumn<String> photoUrl = GeneratedColumn<String>(
    'photo_url',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _bmrKcalMeta = const VerificationMeta(
    'bmrKcal',
  );
  @override
  late final GeneratedColumn<int> bmrKcal = GeneratedColumn<int>(
    'bmr_kcal',
    aliasedName,
    true,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _onboardingCompletedAtMeta =
      const VerificationMeta('onboardingCompletedAt');
  @override
  late final GeneratedColumn<DateTime> onboardingCompletedAt =
      GeneratedColumn<DateTime>(
        'onboarding_completed_at',
        aliasedName,
        true,
        type: DriftSqlType.dateTime,
        requiredDuringInsert: false,
      );
  static const VerificationMeta _planRebuildRequiredMeta =
      const VerificationMeta('planRebuildRequired');
  @override
  late final GeneratedColumn<bool> planRebuildRequired = GeneratedColumn<bool>(
    'plan_rebuild_required',
    aliasedName,
    false,
    type: DriftSqlType.bool,
    requiredDuringInsert: false,
    defaultConstraints: GeneratedColumn.constraintIsAlways(
      'CHECK ("plan_rebuild_required" IN (0, 1))',
    ),
    defaultValue: const Constant(false),
  );
  static const VerificationMeta _updatedAtMeta = const VerificationMeta(
    'updatedAt',
  );
  @override
  late final GeneratedColumn<DateTime> updatedAt = GeneratedColumn<DateTime>(
    'updated_at',
    aliasedName,
    false,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _dirtyMeta = const VerificationMeta('dirty');
  @override
  late final GeneratedColumn<bool> dirty = GeneratedColumn<bool>(
    'dirty',
    aliasedName,
    false,
    type: DriftSqlType.bool,
    requiredDuringInsert: false,
    defaultConstraints: GeneratedColumn.constraintIsAlways(
      'CHECK ("dirty" IN (0, 1))',
    ),
    defaultValue: const Constant(false),
  );
  @override
  List<GeneratedColumn> get $columns => [
    userId,
    email,
    name,
    sex,
    birthDate,
    heightCm,
    baselineWeightKg,
    goal,
    targetWeightKg,
    targetMuscleKg,
    goalStartedAt,
    trainingLevel,
    trainingFrequency,
    allergiesJson,
    equipmentAvailableJson,
    photoUrl,
    bmrKcal,
    onboardingCompletedAt,
    planRebuildRequired,
    updatedAt,
    dirty,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'profiles';
  @override
  VerificationContext validateIntegrity(
    Insertable<Profile> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('user_id')) {
      context.handle(
        _userIdMeta,
        userId.isAcceptableOrUnknown(data['user_id']!, _userIdMeta),
      );
    } else if (isInserting) {
      context.missing(_userIdMeta);
    }
    if (data.containsKey('email')) {
      context.handle(
        _emailMeta,
        email.isAcceptableOrUnknown(data['email']!, _emailMeta),
      );
    } else if (isInserting) {
      context.missing(_emailMeta);
    }
    if (data.containsKey('name')) {
      context.handle(
        _nameMeta,
        name.isAcceptableOrUnknown(data['name']!, _nameMeta),
      );
    }
    if (data.containsKey('sex')) {
      context.handle(
        _sexMeta,
        sex.isAcceptableOrUnknown(data['sex']!, _sexMeta),
      );
    }
    if (data.containsKey('birth_date')) {
      context.handle(
        _birthDateMeta,
        birthDate.isAcceptableOrUnknown(data['birth_date']!, _birthDateMeta),
      );
    }
    if (data.containsKey('height_cm')) {
      context.handle(
        _heightCmMeta,
        heightCm.isAcceptableOrUnknown(data['height_cm']!, _heightCmMeta),
      );
    }
    if (data.containsKey('baseline_weight_kg')) {
      context.handle(
        _baselineWeightKgMeta,
        baselineWeightKg.isAcceptableOrUnknown(
          data['baseline_weight_kg']!,
          _baselineWeightKgMeta,
        ),
      );
    }
    if (data.containsKey('goal')) {
      context.handle(
        _goalMeta,
        goal.isAcceptableOrUnknown(data['goal']!, _goalMeta),
      );
    }
    if (data.containsKey('target_weight_kg')) {
      context.handle(
        _targetWeightKgMeta,
        targetWeightKg.isAcceptableOrUnknown(
          data['target_weight_kg']!,
          _targetWeightKgMeta,
        ),
      );
    }
    if (data.containsKey('target_muscle_kg')) {
      context.handle(
        _targetMuscleKgMeta,
        targetMuscleKg.isAcceptableOrUnknown(
          data['target_muscle_kg']!,
          _targetMuscleKgMeta,
        ),
      );
    }
    if (data.containsKey('goal_started_at')) {
      context.handle(
        _goalStartedAtMeta,
        goalStartedAt.isAcceptableOrUnknown(
          data['goal_started_at']!,
          _goalStartedAtMeta,
        ),
      );
    }
    if (data.containsKey('training_level')) {
      context.handle(
        _trainingLevelMeta,
        trainingLevel.isAcceptableOrUnknown(
          data['training_level']!,
          _trainingLevelMeta,
        ),
      );
    }
    if (data.containsKey('training_frequency')) {
      context.handle(
        _trainingFrequencyMeta,
        trainingFrequency.isAcceptableOrUnknown(
          data['training_frequency']!,
          _trainingFrequencyMeta,
        ),
      );
    }
    if (data.containsKey('allergies_json')) {
      context.handle(
        _allergiesJsonMeta,
        allergiesJson.isAcceptableOrUnknown(
          data['allergies_json']!,
          _allergiesJsonMeta,
        ),
      );
    }
    if (data.containsKey('equipment_available_json')) {
      context.handle(
        _equipmentAvailableJsonMeta,
        equipmentAvailableJson.isAcceptableOrUnknown(
          data['equipment_available_json']!,
          _equipmentAvailableJsonMeta,
        ),
      );
    }
    if (data.containsKey('photo_url')) {
      context.handle(
        _photoUrlMeta,
        photoUrl.isAcceptableOrUnknown(data['photo_url']!, _photoUrlMeta),
      );
    }
    if (data.containsKey('bmr_kcal')) {
      context.handle(
        _bmrKcalMeta,
        bmrKcal.isAcceptableOrUnknown(data['bmr_kcal']!, _bmrKcalMeta),
      );
    }
    if (data.containsKey('onboarding_completed_at')) {
      context.handle(
        _onboardingCompletedAtMeta,
        onboardingCompletedAt.isAcceptableOrUnknown(
          data['onboarding_completed_at']!,
          _onboardingCompletedAtMeta,
        ),
      );
    }
    if (data.containsKey('plan_rebuild_required')) {
      context.handle(
        _planRebuildRequiredMeta,
        planRebuildRequired.isAcceptableOrUnknown(
          data['plan_rebuild_required']!,
          _planRebuildRequiredMeta,
        ),
      );
    }
    if (data.containsKey('updated_at')) {
      context.handle(
        _updatedAtMeta,
        updatedAt.isAcceptableOrUnknown(data['updated_at']!, _updatedAtMeta),
      );
    } else if (isInserting) {
      context.missing(_updatedAtMeta);
    }
    if (data.containsKey('dirty')) {
      context.handle(
        _dirtyMeta,
        dirty.isAcceptableOrUnknown(data['dirty']!, _dirtyMeta),
      );
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {userId};
  @override
  Profile map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return Profile(
      userId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}user_id'],
      )!,
      email: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}email'],
      )!,
      name: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}name'],
      ),
      sex: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}sex'],
      ),
      birthDate: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}birth_date'],
      ),
      heightCm: attachedDatabase.typeMapping.read(
        DriftSqlType.double,
        data['${effectivePrefix}height_cm'],
      ),
      baselineWeightKg: attachedDatabase.typeMapping.read(
        DriftSqlType.double,
        data['${effectivePrefix}baseline_weight_kg'],
      ),
      goal: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}goal'],
      ),
      targetWeightKg: attachedDatabase.typeMapping.read(
        DriftSqlType.double,
        data['${effectivePrefix}target_weight_kg'],
      ),
      targetMuscleKg: attachedDatabase.typeMapping.read(
        DriftSqlType.double,
        data['${effectivePrefix}target_muscle_kg'],
      ),
      goalStartedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}goal_started_at'],
      ),
      trainingLevel: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}training_level'],
      ),
      trainingFrequency: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}training_frequency'],
      ),
      allergiesJson: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}allergies_json'],
      )!,
      equipmentAvailableJson: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}equipment_available_json'],
      ),
      photoUrl: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}photo_url'],
      ),
      bmrKcal: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}bmr_kcal'],
      ),
      onboardingCompletedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}onboarding_completed_at'],
      ),
      planRebuildRequired: attachedDatabase.typeMapping.read(
        DriftSqlType.bool,
        data['${effectivePrefix}plan_rebuild_required'],
      )!,
      updatedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}updated_at'],
      )!,
      dirty: attachedDatabase.typeMapping.read(
        DriftSqlType.bool,
        data['${effectivePrefix}dirty'],
      )!,
    );
  }

  @override
  $ProfilesTable createAlias(String alias) {
    return $ProfilesTable(attachedDatabase, alias);
  }
}

class Profile extends DataClass implements Insertable<Profile> {
  final String userId;
  final String email;
  final String? name;
  final String? sex;
  final DateTime? birthDate;
  final double? heightCm;
  final double? baselineWeightKg;
  final String? goal;
  final double? targetWeightKg;
  final double? targetMuscleKg;
  final DateTime? goalStartedAt;
  final String? trainingLevel;
  final int? trainingFrequency;
  final String allergiesJson;
  final String? equipmentAvailableJson;
  final String? photoUrl;
  final int? bmrKcal;
  final DateTime? onboardingCompletedAt;
  final bool planRebuildRequired;
  final DateTime updatedAt;
  final bool dirty;
  const Profile({
    required this.userId,
    required this.email,
    this.name,
    this.sex,
    this.birthDate,
    this.heightCm,
    this.baselineWeightKg,
    this.goal,
    this.targetWeightKg,
    this.targetMuscleKg,
    this.goalStartedAt,
    this.trainingLevel,
    this.trainingFrequency,
    required this.allergiesJson,
    this.equipmentAvailableJson,
    this.photoUrl,
    this.bmrKcal,
    this.onboardingCompletedAt,
    required this.planRebuildRequired,
    required this.updatedAt,
    required this.dirty,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['user_id'] = Variable<String>(userId);
    map['email'] = Variable<String>(email);
    if (!nullToAbsent || name != null) {
      map['name'] = Variable<String>(name);
    }
    if (!nullToAbsent || sex != null) {
      map['sex'] = Variable<String>(sex);
    }
    if (!nullToAbsent || birthDate != null) {
      map['birth_date'] = Variable<DateTime>(birthDate);
    }
    if (!nullToAbsent || heightCm != null) {
      map['height_cm'] = Variable<double>(heightCm);
    }
    if (!nullToAbsent || baselineWeightKg != null) {
      map['baseline_weight_kg'] = Variable<double>(baselineWeightKg);
    }
    if (!nullToAbsent || goal != null) {
      map['goal'] = Variable<String>(goal);
    }
    if (!nullToAbsent || targetWeightKg != null) {
      map['target_weight_kg'] = Variable<double>(targetWeightKg);
    }
    if (!nullToAbsent || targetMuscleKg != null) {
      map['target_muscle_kg'] = Variable<double>(targetMuscleKg);
    }
    if (!nullToAbsent || goalStartedAt != null) {
      map['goal_started_at'] = Variable<DateTime>(goalStartedAt);
    }
    if (!nullToAbsent || trainingLevel != null) {
      map['training_level'] = Variable<String>(trainingLevel);
    }
    if (!nullToAbsent || trainingFrequency != null) {
      map['training_frequency'] = Variable<int>(trainingFrequency);
    }
    map['allergies_json'] = Variable<String>(allergiesJson);
    if (!nullToAbsent || equipmentAvailableJson != null) {
      map['equipment_available_json'] = Variable<String>(
        equipmentAvailableJson,
      );
    }
    if (!nullToAbsent || photoUrl != null) {
      map['photo_url'] = Variable<String>(photoUrl);
    }
    if (!nullToAbsent || bmrKcal != null) {
      map['bmr_kcal'] = Variable<int>(bmrKcal);
    }
    if (!nullToAbsent || onboardingCompletedAt != null) {
      map['onboarding_completed_at'] = Variable<DateTime>(
        onboardingCompletedAt,
      );
    }
    map['plan_rebuild_required'] = Variable<bool>(planRebuildRequired);
    map['updated_at'] = Variable<DateTime>(updatedAt);
    map['dirty'] = Variable<bool>(dirty);
    return map;
  }

  ProfilesCompanion toCompanion(bool nullToAbsent) {
    return ProfilesCompanion(
      userId: Value(userId),
      email: Value(email),
      name: name == null && nullToAbsent ? const Value.absent() : Value(name),
      sex: sex == null && nullToAbsent ? const Value.absent() : Value(sex),
      birthDate: birthDate == null && nullToAbsent
          ? const Value.absent()
          : Value(birthDate),
      heightCm: heightCm == null && nullToAbsent
          ? const Value.absent()
          : Value(heightCm),
      baselineWeightKg: baselineWeightKg == null && nullToAbsent
          ? const Value.absent()
          : Value(baselineWeightKg),
      goal: goal == null && nullToAbsent ? const Value.absent() : Value(goal),
      targetWeightKg: targetWeightKg == null && nullToAbsent
          ? const Value.absent()
          : Value(targetWeightKg),
      targetMuscleKg: targetMuscleKg == null && nullToAbsent
          ? const Value.absent()
          : Value(targetMuscleKg),
      goalStartedAt: goalStartedAt == null && nullToAbsent
          ? const Value.absent()
          : Value(goalStartedAt),
      trainingLevel: trainingLevel == null && nullToAbsent
          ? const Value.absent()
          : Value(trainingLevel),
      trainingFrequency: trainingFrequency == null && nullToAbsent
          ? const Value.absent()
          : Value(trainingFrequency),
      allergiesJson: Value(allergiesJson),
      equipmentAvailableJson: equipmentAvailableJson == null && nullToAbsent
          ? const Value.absent()
          : Value(equipmentAvailableJson),
      photoUrl: photoUrl == null && nullToAbsent
          ? const Value.absent()
          : Value(photoUrl),
      bmrKcal: bmrKcal == null && nullToAbsent
          ? const Value.absent()
          : Value(bmrKcal),
      onboardingCompletedAt: onboardingCompletedAt == null && nullToAbsent
          ? const Value.absent()
          : Value(onboardingCompletedAt),
      planRebuildRequired: Value(planRebuildRequired),
      updatedAt: Value(updatedAt),
      dirty: Value(dirty),
    );
  }

  factory Profile.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return Profile(
      userId: serializer.fromJson<String>(json['userId']),
      email: serializer.fromJson<String>(json['email']),
      name: serializer.fromJson<String?>(json['name']),
      sex: serializer.fromJson<String?>(json['sex']),
      birthDate: serializer.fromJson<DateTime?>(json['birthDate']),
      heightCm: serializer.fromJson<double?>(json['heightCm']),
      baselineWeightKg: serializer.fromJson<double?>(json['baselineWeightKg']),
      goal: serializer.fromJson<String?>(json['goal']),
      targetWeightKg: serializer.fromJson<double?>(json['targetWeightKg']),
      targetMuscleKg: serializer.fromJson<double?>(json['targetMuscleKg']),
      goalStartedAt: serializer.fromJson<DateTime?>(json['goalStartedAt']),
      trainingLevel: serializer.fromJson<String?>(json['trainingLevel']),
      trainingFrequency: serializer.fromJson<int?>(json['trainingFrequency']),
      allergiesJson: serializer.fromJson<String>(json['allergiesJson']),
      equipmentAvailableJson: serializer.fromJson<String?>(
        json['equipmentAvailableJson'],
      ),
      photoUrl: serializer.fromJson<String?>(json['photoUrl']),
      bmrKcal: serializer.fromJson<int?>(json['bmrKcal']),
      onboardingCompletedAt: serializer.fromJson<DateTime?>(
        json['onboardingCompletedAt'],
      ),
      planRebuildRequired: serializer.fromJson<bool>(
        json['planRebuildRequired'],
      ),
      updatedAt: serializer.fromJson<DateTime>(json['updatedAt']),
      dirty: serializer.fromJson<bool>(json['dirty']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'userId': serializer.toJson<String>(userId),
      'email': serializer.toJson<String>(email),
      'name': serializer.toJson<String?>(name),
      'sex': serializer.toJson<String?>(sex),
      'birthDate': serializer.toJson<DateTime?>(birthDate),
      'heightCm': serializer.toJson<double?>(heightCm),
      'baselineWeightKg': serializer.toJson<double?>(baselineWeightKg),
      'goal': serializer.toJson<String?>(goal),
      'targetWeightKg': serializer.toJson<double?>(targetWeightKg),
      'targetMuscleKg': serializer.toJson<double?>(targetMuscleKg),
      'goalStartedAt': serializer.toJson<DateTime?>(goalStartedAt),
      'trainingLevel': serializer.toJson<String?>(trainingLevel),
      'trainingFrequency': serializer.toJson<int?>(trainingFrequency),
      'allergiesJson': serializer.toJson<String>(allergiesJson),
      'equipmentAvailableJson': serializer.toJson<String?>(
        equipmentAvailableJson,
      ),
      'photoUrl': serializer.toJson<String?>(photoUrl),
      'bmrKcal': serializer.toJson<int?>(bmrKcal),
      'onboardingCompletedAt': serializer.toJson<DateTime?>(
        onboardingCompletedAt,
      ),
      'planRebuildRequired': serializer.toJson<bool>(planRebuildRequired),
      'updatedAt': serializer.toJson<DateTime>(updatedAt),
      'dirty': serializer.toJson<bool>(dirty),
    };
  }

  Profile copyWith({
    String? userId,
    String? email,
    Value<String?> name = const Value.absent(),
    Value<String?> sex = const Value.absent(),
    Value<DateTime?> birthDate = const Value.absent(),
    Value<double?> heightCm = const Value.absent(),
    Value<double?> baselineWeightKg = const Value.absent(),
    Value<String?> goal = const Value.absent(),
    Value<double?> targetWeightKg = const Value.absent(),
    Value<double?> targetMuscleKg = const Value.absent(),
    Value<DateTime?> goalStartedAt = const Value.absent(),
    Value<String?> trainingLevel = const Value.absent(),
    Value<int?> trainingFrequency = const Value.absent(),
    String? allergiesJson,
    Value<String?> equipmentAvailableJson = const Value.absent(),
    Value<String?> photoUrl = const Value.absent(),
    Value<int?> bmrKcal = const Value.absent(),
    Value<DateTime?> onboardingCompletedAt = const Value.absent(),
    bool? planRebuildRequired,
    DateTime? updatedAt,
    bool? dirty,
  }) => Profile(
    userId: userId ?? this.userId,
    email: email ?? this.email,
    name: name.present ? name.value : this.name,
    sex: sex.present ? sex.value : this.sex,
    birthDate: birthDate.present ? birthDate.value : this.birthDate,
    heightCm: heightCm.present ? heightCm.value : this.heightCm,
    baselineWeightKg: baselineWeightKg.present
        ? baselineWeightKg.value
        : this.baselineWeightKg,
    goal: goal.present ? goal.value : this.goal,
    targetWeightKg: targetWeightKg.present
        ? targetWeightKg.value
        : this.targetWeightKg,
    targetMuscleKg: targetMuscleKg.present
        ? targetMuscleKg.value
        : this.targetMuscleKg,
    goalStartedAt: goalStartedAt.present
        ? goalStartedAt.value
        : this.goalStartedAt,
    trainingLevel: trainingLevel.present
        ? trainingLevel.value
        : this.trainingLevel,
    trainingFrequency: trainingFrequency.present
        ? trainingFrequency.value
        : this.trainingFrequency,
    allergiesJson: allergiesJson ?? this.allergiesJson,
    equipmentAvailableJson: equipmentAvailableJson.present
        ? equipmentAvailableJson.value
        : this.equipmentAvailableJson,
    photoUrl: photoUrl.present ? photoUrl.value : this.photoUrl,
    bmrKcal: bmrKcal.present ? bmrKcal.value : this.bmrKcal,
    onboardingCompletedAt: onboardingCompletedAt.present
        ? onboardingCompletedAt.value
        : this.onboardingCompletedAt,
    planRebuildRequired: planRebuildRequired ?? this.planRebuildRequired,
    updatedAt: updatedAt ?? this.updatedAt,
    dirty: dirty ?? this.dirty,
  );
  Profile copyWithCompanion(ProfilesCompanion data) {
    return Profile(
      userId: data.userId.present ? data.userId.value : this.userId,
      email: data.email.present ? data.email.value : this.email,
      name: data.name.present ? data.name.value : this.name,
      sex: data.sex.present ? data.sex.value : this.sex,
      birthDate: data.birthDate.present ? data.birthDate.value : this.birthDate,
      heightCm: data.heightCm.present ? data.heightCm.value : this.heightCm,
      baselineWeightKg: data.baselineWeightKg.present
          ? data.baselineWeightKg.value
          : this.baselineWeightKg,
      goal: data.goal.present ? data.goal.value : this.goal,
      targetWeightKg: data.targetWeightKg.present
          ? data.targetWeightKg.value
          : this.targetWeightKg,
      targetMuscleKg: data.targetMuscleKg.present
          ? data.targetMuscleKg.value
          : this.targetMuscleKg,
      goalStartedAt: data.goalStartedAt.present
          ? data.goalStartedAt.value
          : this.goalStartedAt,
      trainingLevel: data.trainingLevel.present
          ? data.trainingLevel.value
          : this.trainingLevel,
      trainingFrequency: data.trainingFrequency.present
          ? data.trainingFrequency.value
          : this.trainingFrequency,
      allergiesJson: data.allergiesJson.present
          ? data.allergiesJson.value
          : this.allergiesJson,
      equipmentAvailableJson: data.equipmentAvailableJson.present
          ? data.equipmentAvailableJson.value
          : this.equipmentAvailableJson,
      photoUrl: data.photoUrl.present ? data.photoUrl.value : this.photoUrl,
      bmrKcal: data.bmrKcal.present ? data.bmrKcal.value : this.bmrKcal,
      onboardingCompletedAt: data.onboardingCompletedAt.present
          ? data.onboardingCompletedAt.value
          : this.onboardingCompletedAt,
      planRebuildRequired: data.planRebuildRequired.present
          ? data.planRebuildRequired.value
          : this.planRebuildRequired,
      updatedAt: data.updatedAt.present ? data.updatedAt.value : this.updatedAt,
      dirty: data.dirty.present ? data.dirty.value : this.dirty,
    );
  }

  @override
  String toString() {
    return (StringBuffer('Profile(')
          ..write('userId: $userId, ')
          ..write('email: $email, ')
          ..write('name: $name, ')
          ..write('sex: $sex, ')
          ..write('birthDate: $birthDate, ')
          ..write('heightCm: $heightCm, ')
          ..write('baselineWeightKg: $baselineWeightKg, ')
          ..write('goal: $goal, ')
          ..write('targetWeightKg: $targetWeightKg, ')
          ..write('targetMuscleKg: $targetMuscleKg, ')
          ..write('goalStartedAt: $goalStartedAt, ')
          ..write('trainingLevel: $trainingLevel, ')
          ..write('trainingFrequency: $trainingFrequency, ')
          ..write('allergiesJson: $allergiesJson, ')
          ..write('equipmentAvailableJson: $equipmentAvailableJson, ')
          ..write('photoUrl: $photoUrl, ')
          ..write('bmrKcal: $bmrKcal, ')
          ..write('onboardingCompletedAt: $onboardingCompletedAt, ')
          ..write('planRebuildRequired: $planRebuildRequired, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('dirty: $dirty')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hashAll([
    userId,
    email,
    name,
    sex,
    birthDate,
    heightCm,
    baselineWeightKg,
    goal,
    targetWeightKg,
    targetMuscleKg,
    goalStartedAt,
    trainingLevel,
    trainingFrequency,
    allergiesJson,
    equipmentAvailableJson,
    photoUrl,
    bmrKcal,
    onboardingCompletedAt,
    planRebuildRequired,
    updatedAt,
    dirty,
  ]);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is Profile &&
          other.userId == this.userId &&
          other.email == this.email &&
          other.name == this.name &&
          other.sex == this.sex &&
          other.birthDate == this.birthDate &&
          other.heightCm == this.heightCm &&
          other.baselineWeightKg == this.baselineWeightKg &&
          other.goal == this.goal &&
          other.targetWeightKg == this.targetWeightKg &&
          other.targetMuscleKg == this.targetMuscleKg &&
          other.goalStartedAt == this.goalStartedAt &&
          other.trainingLevel == this.trainingLevel &&
          other.trainingFrequency == this.trainingFrequency &&
          other.allergiesJson == this.allergiesJson &&
          other.equipmentAvailableJson == this.equipmentAvailableJson &&
          other.photoUrl == this.photoUrl &&
          other.bmrKcal == this.bmrKcal &&
          other.onboardingCompletedAt == this.onboardingCompletedAt &&
          other.planRebuildRequired == this.planRebuildRequired &&
          other.updatedAt == this.updatedAt &&
          other.dirty == this.dirty);
}

class ProfilesCompanion extends UpdateCompanion<Profile> {
  final Value<String> userId;
  final Value<String> email;
  final Value<String?> name;
  final Value<String?> sex;
  final Value<DateTime?> birthDate;
  final Value<double?> heightCm;
  final Value<double?> baselineWeightKg;
  final Value<String?> goal;
  final Value<double?> targetWeightKg;
  final Value<double?> targetMuscleKg;
  final Value<DateTime?> goalStartedAt;
  final Value<String?> trainingLevel;
  final Value<int?> trainingFrequency;
  final Value<String> allergiesJson;
  final Value<String?> equipmentAvailableJson;
  final Value<String?> photoUrl;
  final Value<int?> bmrKcal;
  final Value<DateTime?> onboardingCompletedAt;
  final Value<bool> planRebuildRequired;
  final Value<DateTime> updatedAt;
  final Value<bool> dirty;
  final Value<int> rowid;
  const ProfilesCompanion({
    this.userId = const Value.absent(),
    this.email = const Value.absent(),
    this.name = const Value.absent(),
    this.sex = const Value.absent(),
    this.birthDate = const Value.absent(),
    this.heightCm = const Value.absent(),
    this.baselineWeightKg = const Value.absent(),
    this.goal = const Value.absent(),
    this.targetWeightKg = const Value.absent(),
    this.targetMuscleKg = const Value.absent(),
    this.goalStartedAt = const Value.absent(),
    this.trainingLevel = const Value.absent(),
    this.trainingFrequency = const Value.absent(),
    this.allergiesJson = const Value.absent(),
    this.equipmentAvailableJson = const Value.absent(),
    this.photoUrl = const Value.absent(),
    this.bmrKcal = const Value.absent(),
    this.onboardingCompletedAt = const Value.absent(),
    this.planRebuildRequired = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.dirty = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  ProfilesCompanion.insert({
    required String userId,
    required String email,
    this.name = const Value.absent(),
    this.sex = const Value.absent(),
    this.birthDate = const Value.absent(),
    this.heightCm = const Value.absent(),
    this.baselineWeightKg = const Value.absent(),
    this.goal = const Value.absent(),
    this.targetWeightKg = const Value.absent(),
    this.targetMuscleKg = const Value.absent(),
    this.goalStartedAt = const Value.absent(),
    this.trainingLevel = const Value.absent(),
    this.trainingFrequency = const Value.absent(),
    this.allergiesJson = const Value.absent(),
    this.equipmentAvailableJson = const Value.absent(),
    this.photoUrl = const Value.absent(),
    this.bmrKcal = const Value.absent(),
    this.onboardingCompletedAt = const Value.absent(),
    this.planRebuildRequired = const Value.absent(),
    required DateTime updatedAt,
    this.dirty = const Value.absent(),
    this.rowid = const Value.absent(),
  }) : userId = Value(userId),
       email = Value(email),
       updatedAt = Value(updatedAt);
  static Insertable<Profile> custom({
    Expression<String>? userId,
    Expression<String>? email,
    Expression<String>? name,
    Expression<String>? sex,
    Expression<DateTime>? birthDate,
    Expression<double>? heightCm,
    Expression<double>? baselineWeightKg,
    Expression<String>? goal,
    Expression<double>? targetWeightKg,
    Expression<double>? targetMuscleKg,
    Expression<DateTime>? goalStartedAt,
    Expression<String>? trainingLevel,
    Expression<int>? trainingFrequency,
    Expression<String>? allergiesJson,
    Expression<String>? equipmentAvailableJson,
    Expression<String>? photoUrl,
    Expression<int>? bmrKcal,
    Expression<DateTime>? onboardingCompletedAt,
    Expression<bool>? planRebuildRequired,
    Expression<DateTime>? updatedAt,
    Expression<bool>? dirty,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (userId != null) 'user_id': userId,
      if (email != null) 'email': email,
      if (name != null) 'name': name,
      if (sex != null) 'sex': sex,
      if (birthDate != null) 'birth_date': birthDate,
      if (heightCm != null) 'height_cm': heightCm,
      if (baselineWeightKg != null) 'baseline_weight_kg': baselineWeightKg,
      if (goal != null) 'goal': goal,
      if (targetWeightKg != null) 'target_weight_kg': targetWeightKg,
      if (targetMuscleKg != null) 'target_muscle_kg': targetMuscleKg,
      if (goalStartedAt != null) 'goal_started_at': goalStartedAt,
      if (trainingLevel != null) 'training_level': trainingLevel,
      if (trainingFrequency != null) 'training_frequency': trainingFrequency,
      if (allergiesJson != null) 'allergies_json': allergiesJson,
      if (equipmentAvailableJson != null)
        'equipment_available_json': equipmentAvailableJson,
      if (photoUrl != null) 'photo_url': photoUrl,
      if (bmrKcal != null) 'bmr_kcal': bmrKcal,
      if (onboardingCompletedAt != null)
        'onboarding_completed_at': onboardingCompletedAt,
      if (planRebuildRequired != null)
        'plan_rebuild_required': planRebuildRequired,
      if (updatedAt != null) 'updated_at': updatedAt,
      if (dirty != null) 'dirty': dirty,
      if (rowid != null) 'rowid': rowid,
    });
  }

  ProfilesCompanion copyWith({
    Value<String>? userId,
    Value<String>? email,
    Value<String?>? name,
    Value<String?>? sex,
    Value<DateTime?>? birthDate,
    Value<double?>? heightCm,
    Value<double?>? baselineWeightKg,
    Value<String?>? goal,
    Value<double?>? targetWeightKg,
    Value<double?>? targetMuscleKg,
    Value<DateTime?>? goalStartedAt,
    Value<String?>? trainingLevel,
    Value<int?>? trainingFrequency,
    Value<String>? allergiesJson,
    Value<String?>? equipmentAvailableJson,
    Value<String?>? photoUrl,
    Value<int?>? bmrKcal,
    Value<DateTime?>? onboardingCompletedAt,
    Value<bool>? planRebuildRequired,
    Value<DateTime>? updatedAt,
    Value<bool>? dirty,
    Value<int>? rowid,
  }) {
    return ProfilesCompanion(
      userId: userId ?? this.userId,
      email: email ?? this.email,
      name: name ?? this.name,
      sex: sex ?? this.sex,
      birthDate: birthDate ?? this.birthDate,
      heightCm: heightCm ?? this.heightCm,
      baselineWeightKg: baselineWeightKg ?? this.baselineWeightKg,
      goal: goal ?? this.goal,
      targetWeightKg: targetWeightKg ?? this.targetWeightKg,
      targetMuscleKg: targetMuscleKg ?? this.targetMuscleKg,
      goalStartedAt: goalStartedAt ?? this.goalStartedAt,
      trainingLevel: trainingLevel ?? this.trainingLevel,
      trainingFrequency: trainingFrequency ?? this.trainingFrequency,
      allergiesJson: allergiesJson ?? this.allergiesJson,
      equipmentAvailableJson:
          equipmentAvailableJson ?? this.equipmentAvailableJson,
      photoUrl: photoUrl ?? this.photoUrl,
      bmrKcal: bmrKcal ?? this.bmrKcal,
      onboardingCompletedAt:
          onboardingCompletedAt ?? this.onboardingCompletedAt,
      planRebuildRequired: planRebuildRequired ?? this.planRebuildRequired,
      updatedAt: updatedAt ?? this.updatedAt,
      dirty: dirty ?? this.dirty,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (userId.present) {
      map['user_id'] = Variable<String>(userId.value);
    }
    if (email.present) {
      map['email'] = Variable<String>(email.value);
    }
    if (name.present) {
      map['name'] = Variable<String>(name.value);
    }
    if (sex.present) {
      map['sex'] = Variable<String>(sex.value);
    }
    if (birthDate.present) {
      map['birth_date'] = Variable<DateTime>(birthDate.value);
    }
    if (heightCm.present) {
      map['height_cm'] = Variable<double>(heightCm.value);
    }
    if (baselineWeightKg.present) {
      map['baseline_weight_kg'] = Variable<double>(baselineWeightKg.value);
    }
    if (goal.present) {
      map['goal'] = Variable<String>(goal.value);
    }
    if (targetWeightKg.present) {
      map['target_weight_kg'] = Variable<double>(targetWeightKg.value);
    }
    if (targetMuscleKg.present) {
      map['target_muscle_kg'] = Variable<double>(targetMuscleKg.value);
    }
    if (goalStartedAt.present) {
      map['goal_started_at'] = Variable<DateTime>(goalStartedAt.value);
    }
    if (trainingLevel.present) {
      map['training_level'] = Variable<String>(trainingLevel.value);
    }
    if (trainingFrequency.present) {
      map['training_frequency'] = Variable<int>(trainingFrequency.value);
    }
    if (allergiesJson.present) {
      map['allergies_json'] = Variable<String>(allergiesJson.value);
    }
    if (equipmentAvailableJson.present) {
      map['equipment_available_json'] = Variable<String>(
        equipmentAvailableJson.value,
      );
    }
    if (photoUrl.present) {
      map['photo_url'] = Variable<String>(photoUrl.value);
    }
    if (bmrKcal.present) {
      map['bmr_kcal'] = Variable<int>(bmrKcal.value);
    }
    if (onboardingCompletedAt.present) {
      map['onboarding_completed_at'] = Variable<DateTime>(
        onboardingCompletedAt.value,
      );
    }
    if (planRebuildRequired.present) {
      map['plan_rebuild_required'] = Variable<bool>(planRebuildRequired.value);
    }
    if (updatedAt.present) {
      map['updated_at'] = Variable<DateTime>(updatedAt.value);
    }
    if (dirty.present) {
      map['dirty'] = Variable<bool>(dirty.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('ProfilesCompanion(')
          ..write('userId: $userId, ')
          ..write('email: $email, ')
          ..write('name: $name, ')
          ..write('sex: $sex, ')
          ..write('birthDate: $birthDate, ')
          ..write('heightCm: $heightCm, ')
          ..write('baselineWeightKg: $baselineWeightKg, ')
          ..write('goal: $goal, ')
          ..write('targetWeightKg: $targetWeightKg, ')
          ..write('targetMuscleKg: $targetMuscleKg, ')
          ..write('goalStartedAt: $goalStartedAt, ')
          ..write('trainingLevel: $trainingLevel, ')
          ..write('trainingFrequency: $trainingFrequency, ')
          ..write('allergiesJson: $allergiesJson, ')
          ..write('equipmentAvailableJson: $equipmentAvailableJson, ')
          ..write('photoUrl: $photoUrl, ')
          ..write('bmrKcal: $bmrKcal, ')
          ..write('onboardingCompletedAt: $onboardingCompletedAt, ')
          ..write('planRebuildRequired: $planRebuildRequired, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('dirty: $dirty, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $SyncQueueTable extends SyncQueue
    with TableInfo<$SyncQueueTable, SyncQueueData> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $SyncQueueTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<int> id = GeneratedColumn<int>(
    'id',
    aliasedName,
    false,
    hasAutoIncrement: true,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
    defaultConstraints: GeneratedColumn.constraintIsAlways(
      'PRIMARY KEY AUTOINCREMENT',
    ),
  );
  static const VerificationMeta _clientIdMeta = const VerificationMeta(
    'clientId',
  );
  @override
  late final GeneratedColumn<String> clientId = GeneratedColumn<String>(
    'client_id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _opKindMeta = const VerificationMeta('opKind');
  @override
  late final GeneratedColumn<String> opKind = GeneratedColumn<String>(
    'op_kind',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _endpointMeta = const VerificationMeta(
    'endpoint',
  );
  @override
  late final GeneratedColumn<String> endpoint = GeneratedColumn<String>(
    'endpoint',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _httpMethodMeta = const VerificationMeta(
    'httpMethod',
  );
  @override
  late final GeneratedColumn<String> httpMethod = GeneratedColumn<String>(
    'http_method',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _payloadJsonMeta = const VerificationMeta(
    'payloadJson',
  );
  @override
  late final GeneratedColumn<String> payloadJson = GeneratedColumn<String>(
    'payload_json',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _headersJsonMeta = const VerificationMeta(
    'headersJson',
  );
  @override
  late final GeneratedColumn<String> headersJson = GeneratedColumn<String>(
    'headers_json',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _attemptsMeta = const VerificationMeta(
    'attempts',
  );
  @override
  late final GeneratedColumn<int> attempts = GeneratedColumn<int>(
    'attempts',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
    defaultValue: const Constant(0),
  );
  static const VerificationMeta _lastErrorMeta = const VerificationMeta(
    'lastError',
  );
  @override
  late final GeneratedColumn<String> lastError = GeneratedColumn<String>(
    'last_error',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _statusMeta = const VerificationMeta('status');
  @override
  late final GeneratedColumn<String> status = GeneratedColumn<String>(
    'status',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant('pending'),
  );
  static const VerificationMeta _createdAtMeta = const VerificationMeta(
    'createdAt',
  );
  @override
  late final GeneratedColumn<DateTime> createdAt = GeneratedColumn<DateTime>(
    'created_at',
    aliasedName,
    false,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: false,
    defaultValue: currentDateAndTime,
  );
  static const VerificationMeta _nextRetryAtMeta = const VerificationMeta(
    'nextRetryAt',
  );
  @override
  late final GeneratedColumn<DateTime> nextRetryAt = GeneratedColumn<DateTime>(
    'next_retry_at',
    aliasedName,
    true,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _appliedAtMeta = const VerificationMeta(
    'appliedAt',
  );
  @override
  late final GeneratedColumn<DateTime> appliedAt = GeneratedColumn<DateTime>(
    'applied_at',
    aliasedName,
    true,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: false,
  );
  @override
  List<GeneratedColumn> get $columns => [
    id,
    clientId,
    opKind,
    endpoint,
    httpMethod,
    payloadJson,
    headersJson,
    attempts,
    lastError,
    status,
    createdAt,
    nextRetryAt,
    appliedAt,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'sync_queue';
  @override
  VerificationContext validateIntegrity(
    Insertable<SyncQueueData> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    }
    if (data.containsKey('client_id')) {
      context.handle(
        _clientIdMeta,
        clientId.isAcceptableOrUnknown(data['client_id']!, _clientIdMeta),
      );
    } else if (isInserting) {
      context.missing(_clientIdMeta);
    }
    if (data.containsKey('op_kind')) {
      context.handle(
        _opKindMeta,
        opKind.isAcceptableOrUnknown(data['op_kind']!, _opKindMeta),
      );
    } else if (isInserting) {
      context.missing(_opKindMeta);
    }
    if (data.containsKey('endpoint')) {
      context.handle(
        _endpointMeta,
        endpoint.isAcceptableOrUnknown(data['endpoint']!, _endpointMeta),
      );
    } else if (isInserting) {
      context.missing(_endpointMeta);
    }
    if (data.containsKey('http_method')) {
      context.handle(
        _httpMethodMeta,
        httpMethod.isAcceptableOrUnknown(data['http_method']!, _httpMethodMeta),
      );
    } else if (isInserting) {
      context.missing(_httpMethodMeta);
    }
    if (data.containsKey('payload_json')) {
      context.handle(
        _payloadJsonMeta,
        payloadJson.isAcceptableOrUnknown(
          data['payload_json']!,
          _payloadJsonMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_payloadJsonMeta);
    }
    if (data.containsKey('headers_json')) {
      context.handle(
        _headersJsonMeta,
        headersJson.isAcceptableOrUnknown(
          data['headers_json']!,
          _headersJsonMeta,
        ),
      );
    }
    if (data.containsKey('attempts')) {
      context.handle(
        _attemptsMeta,
        attempts.isAcceptableOrUnknown(data['attempts']!, _attemptsMeta),
      );
    }
    if (data.containsKey('last_error')) {
      context.handle(
        _lastErrorMeta,
        lastError.isAcceptableOrUnknown(data['last_error']!, _lastErrorMeta),
      );
    }
    if (data.containsKey('status')) {
      context.handle(
        _statusMeta,
        status.isAcceptableOrUnknown(data['status']!, _statusMeta),
      );
    }
    if (data.containsKey('created_at')) {
      context.handle(
        _createdAtMeta,
        createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta),
      );
    }
    if (data.containsKey('next_retry_at')) {
      context.handle(
        _nextRetryAtMeta,
        nextRetryAt.isAcceptableOrUnknown(
          data['next_retry_at']!,
          _nextRetryAtMeta,
        ),
      );
    }
    if (data.containsKey('applied_at')) {
      context.handle(
        _appliedAtMeta,
        appliedAt.isAcceptableOrUnknown(data['applied_at']!, _appliedAtMeta),
      );
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  SyncQueueData map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return SyncQueueData(
      id: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}id'],
      )!,
      clientId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}client_id'],
      )!,
      opKind: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}op_kind'],
      )!,
      endpoint: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}endpoint'],
      )!,
      httpMethod: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}http_method'],
      )!,
      payloadJson: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}payload_json'],
      )!,
      headersJson: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}headers_json'],
      ),
      attempts: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}attempts'],
      )!,
      lastError: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}last_error'],
      ),
      status: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}status'],
      )!,
      createdAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}created_at'],
      )!,
      nextRetryAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}next_retry_at'],
      ),
      appliedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}applied_at'],
      ),
    );
  }

  @override
  $SyncQueueTable createAlias(String alias) {
    return $SyncQueueTable(attachedDatabase, alias);
  }
}

class SyncQueueData extends DataClass implements Insertable<SyncQueueData> {
  final int id;

  /// UUID, который клиент кладёт в `client_id` payload'а на сервере.
  /// Server-side UNIQUE-индекс (migration 0021) дедуплицирует ретраи.
  final String clientId;

  /// Тип операции для удобства логирования и debounce-логики.
  /// 'CREATE_WORKOUT' / 'LOG_SET' / 'CREATE_INBODY' / 'PATCH_PROFILE' / ...
  final String opKind;

  /// Полный путь эндпоинта (например, '/api/v1/workouts').
  final String endpoint;

  /// HTTP-метод.
  final String httpMethod;

  /// Body запроса как JSON-string.
  final String payloadJson;

  /// Доп. заголовки (например, If-Unmodified-Since) как JSON {name: value}.
  final String? headersJson;
  final int attempts;
  final String? lastError;

  /// `pending` — ждёт; `in_flight` — отправляется прямо сейчас (защита от
  /// двойного запуска воркера); `applied` — синхронизировано; `failed` —
  /// неуспех (можно ретрайнуть руками).
  final String status;
  final DateTime createdAt;
  final DateTime? nextRetryAt;
  final DateTime? appliedAt;
  const SyncQueueData({
    required this.id,
    required this.clientId,
    required this.opKind,
    required this.endpoint,
    required this.httpMethod,
    required this.payloadJson,
    this.headersJson,
    required this.attempts,
    this.lastError,
    required this.status,
    required this.createdAt,
    this.nextRetryAt,
    this.appliedAt,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<int>(id);
    map['client_id'] = Variable<String>(clientId);
    map['op_kind'] = Variable<String>(opKind);
    map['endpoint'] = Variable<String>(endpoint);
    map['http_method'] = Variable<String>(httpMethod);
    map['payload_json'] = Variable<String>(payloadJson);
    if (!nullToAbsent || headersJson != null) {
      map['headers_json'] = Variable<String>(headersJson);
    }
    map['attempts'] = Variable<int>(attempts);
    if (!nullToAbsent || lastError != null) {
      map['last_error'] = Variable<String>(lastError);
    }
    map['status'] = Variable<String>(status);
    map['created_at'] = Variable<DateTime>(createdAt);
    if (!nullToAbsent || nextRetryAt != null) {
      map['next_retry_at'] = Variable<DateTime>(nextRetryAt);
    }
    if (!nullToAbsent || appliedAt != null) {
      map['applied_at'] = Variable<DateTime>(appliedAt);
    }
    return map;
  }

  SyncQueueCompanion toCompanion(bool nullToAbsent) {
    return SyncQueueCompanion(
      id: Value(id),
      clientId: Value(clientId),
      opKind: Value(opKind),
      endpoint: Value(endpoint),
      httpMethod: Value(httpMethod),
      payloadJson: Value(payloadJson),
      headersJson: headersJson == null && nullToAbsent
          ? const Value.absent()
          : Value(headersJson),
      attempts: Value(attempts),
      lastError: lastError == null && nullToAbsent
          ? const Value.absent()
          : Value(lastError),
      status: Value(status),
      createdAt: Value(createdAt),
      nextRetryAt: nextRetryAt == null && nullToAbsent
          ? const Value.absent()
          : Value(nextRetryAt),
      appliedAt: appliedAt == null && nullToAbsent
          ? const Value.absent()
          : Value(appliedAt),
    );
  }

  factory SyncQueueData.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return SyncQueueData(
      id: serializer.fromJson<int>(json['id']),
      clientId: serializer.fromJson<String>(json['clientId']),
      opKind: serializer.fromJson<String>(json['opKind']),
      endpoint: serializer.fromJson<String>(json['endpoint']),
      httpMethod: serializer.fromJson<String>(json['httpMethod']),
      payloadJson: serializer.fromJson<String>(json['payloadJson']),
      headersJson: serializer.fromJson<String?>(json['headersJson']),
      attempts: serializer.fromJson<int>(json['attempts']),
      lastError: serializer.fromJson<String?>(json['lastError']),
      status: serializer.fromJson<String>(json['status']),
      createdAt: serializer.fromJson<DateTime>(json['createdAt']),
      nextRetryAt: serializer.fromJson<DateTime?>(json['nextRetryAt']),
      appliedAt: serializer.fromJson<DateTime?>(json['appliedAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<int>(id),
      'clientId': serializer.toJson<String>(clientId),
      'opKind': serializer.toJson<String>(opKind),
      'endpoint': serializer.toJson<String>(endpoint),
      'httpMethod': serializer.toJson<String>(httpMethod),
      'payloadJson': serializer.toJson<String>(payloadJson),
      'headersJson': serializer.toJson<String?>(headersJson),
      'attempts': serializer.toJson<int>(attempts),
      'lastError': serializer.toJson<String?>(lastError),
      'status': serializer.toJson<String>(status),
      'createdAt': serializer.toJson<DateTime>(createdAt),
      'nextRetryAt': serializer.toJson<DateTime?>(nextRetryAt),
      'appliedAt': serializer.toJson<DateTime?>(appliedAt),
    };
  }

  SyncQueueData copyWith({
    int? id,
    String? clientId,
    String? opKind,
    String? endpoint,
    String? httpMethod,
    String? payloadJson,
    Value<String?> headersJson = const Value.absent(),
    int? attempts,
    Value<String?> lastError = const Value.absent(),
    String? status,
    DateTime? createdAt,
    Value<DateTime?> nextRetryAt = const Value.absent(),
    Value<DateTime?> appliedAt = const Value.absent(),
  }) => SyncQueueData(
    id: id ?? this.id,
    clientId: clientId ?? this.clientId,
    opKind: opKind ?? this.opKind,
    endpoint: endpoint ?? this.endpoint,
    httpMethod: httpMethod ?? this.httpMethod,
    payloadJson: payloadJson ?? this.payloadJson,
    headersJson: headersJson.present ? headersJson.value : this.headersJson,
    attempts: attempts ?? this.attempts,
    lastError: lastError.present ? lastError.value : this.lastError,
    status: status ?? this.status,
    createdAt: createdAt ?? this.createdAt,
    nextRetryAt: nextRetryAt.present ? nextRetryAt.value : this.nextRetryAt,
    appliedAt: appliedAt.present ? appliedAt.value : this.appliedAt,
  );
  SyncQueueData copyWithCompanion(SyncQueueCompanion data) {
    return SyncQueueData(
      id: data.id.present ? data.id.value : this.id,
      clientId: data.clientId.present ? data.clientId.value : this.clientId,
      opKind: data.opKind.present ? data.opKind.value : this.opKind,
      endpoint: data.endpoint.present ? data.endpoint.value : this.endpoint,
      httpMethod: data.httpMethod.present
          ? data.httpMethod.value
          : this.httpMethod,
      payloadJson: data.payloadJson.present
          ? data.payloadJson.value
          : this.payloadJson,
      headersJson: data.headersJson.present
          ? data.headersJson.value
          : this.headersJson,
      attempts: data.attempts.present ? data.attempts.value : this.attempts,
      lastError: data.lastError.present ? data.lastError.value : this.lastError,
      status: data.status.present ? data.status.value : this.status,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
      nextRetryAt: data.nextRetryAt.present
          ? data.nextRetryAt.value
          : this.nextRetryAt,
      appliedAt: data.appliedAt.present ? data.appliedAt.value : this.appliedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('SyncQueueData(')
          ..write('id: $id, ')
          ..write('clientId: $clientId, ')
          ..write('opKind: $opKind, ')
          ..write('endpoint: $endpoint, ')
          ..write('httpMethod: $httpMethod, ')
          ..write('payloadJson: $payloadJson, ')
          ..write('headersJson: $headersJson, ')
          ..write('attempts: $attempts, ')
          ..write('lastError: $lastError, ')
          ..write('status: $status, ')
          ..write('createdAt: $createdAt, ')
          ..write('nextRetryAt: $nextRetryAt, ')
          ..write('appliedAt: $appliedAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    id,
    clientId,
    opKind,
    endpoint,
    httpMethod,
    payloadJson,
    headersJson,
    attempts,
    lastError,
    status,
    createdAt,
    nextRetryAt,
    appliedAt,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is SyncQueueData &&
          other.id == this.id &&
          other.clientId == this.clientId &&
          other.opKind == this.opKind &&
          other.endpoint == this.endpoint &&
          other.httpMethod == this.httpMethod &&
          other.payloadJson == this.payloadJson &&
          other.headersJson == this.headersJson &&
          other.attempts == this.attempts &&
          other.lastError == this.lastError &&
          other.status == this.status &&
          other.createdAt == this.createdAt &&
          other.nextRetryAt == this.nextRetryAt &&
          other.appliedAt == this.appliedAt);
}

class SyncQueueCompanion extends UpdateCompanion<SyncQueueData> {
  final Value<int> id;
  final Value<String> clientId;
  final Value<String> opKind;
  final Value<String> endpoint;
  final Value<String> httpMethod;
  final Value<String> payloadJson;
  final Value<String?> headersJson;
  final Value<int> attempts;
  final Value<String?> lastError;
  final Value<String> status;
  final Value<DateTime> createdAt;
  final Value<DateTime?> nextRetryAt;
  final Value<DateTime?> appliedAt;
  const SyncQueueCompanion({
    this.id = const Value.absent(),
    this.clientId = const Value.absent(),
    this.opKind = const Value.absent(),
    this.endpoint = const Value.absent(),
    this.httpMethod = const Value.absent(),
    this.payloadJson = const Value.absent(),
    this.headersJson = const Value.absent(),
    this.attempts = const Value.absent(),
    this.lastError = const Value.absent(),
    this.status = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.nextRetryAt = const Value.absent(),
    this.appliedAt = const Value.absent(),
  });
  SyncQueueCompanion.insert({
    this.id = const Value.absent(),
    required String clientId,
    required String opKind,
    required String endpoint,
    required String httpMethod,
    required String payloadJson,
    this.headersJson = const Value.absent(),
    this.attempts = const Value.absent(),
    this.lastError = const Value.absent(),
    this.status = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.nextRetryAt = const Value.absent(),
    this.appliedAt = const Value.absent(),
  }) : clientId = Value(clientId),
       opKind = Value(opKind),
       endpoint = Value(endpoint),
       httpMethod = Value(httpMethod),
       payloadJson = Value(payloadJson);
  static Insertable<SyncQueueData> custom({
    Expression<int>? id,
    Expression<String>? clientId,
    Expression<String>? opKind,
    Expression<String>? endpoint,
    Expression<String>? httpMethod,
    Expression<String>? payloadJson,
    Expression<String>? headersJson,
    Expression<int>? attempts,
    Expression<String>? lastError,
    Expression<String>? status,
    Expression<DateTime>? createdAt,
    Expression<DateTime>? nextRetryAt,
    Expression<DateTime>? appliedAt,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (clientId != null) 'client_id': clientId,
      if (opKind != null) 'op_kind': opKind,
      if (endpoint != null) 'endpoint': endpoint,
      if (httpMethod != null) 'http_method': httpMethod,
      if (payloadJson != null) 'payload_json': payloadJson,
      if (headersJson != null) 'headers_json': headersJson,
      if (attempts != null) 'attempts': attempts,
      if (lastError != null) 'last_error': lastError,
      if (status != null) 'status': status,
      if (createdAt != null) 'created_at': createdAt,
      if (nextRetryAt != null) 'next_retry_at': nextRetryAt,
      if (appliedAt != null) 'applied_at': appliedAt,
    });
  }

  SyncQueueCompanion copyWith({
    Value<int>? id,
    Value<String>? clientId,
    Value<String>? opKind,
    Value<String>? endpoint,
    Value<String>? httpMethod,
    Value<String>? payloadJson,
    Value<String?>? headersJson,
    Value<int>? attempts,
    Value<String?>? lastError,
    Value<String>? status,
    Value<DateTime>? createdAt,
    Value<DateTime?>? nextRetryAt,
    Value<DateTime?>? appliedAt,
  }) {
    return SyncQueueCompanion(
      id: id ?? this.id,
      clientId: clientId ?? this.clientId,
      opKind: opKind ?? this.opKind,
      endpoint: endpoint ?? this.endpoint,
      httpMethod: httpMethod ?? this.httpMethod,
      payloadJson: payloadJson ?? this.payloadJson,
      headersJson: headersJson ?? this.headersJson,
      attempts: attempts ?? this.attempts,
      lastError: lastError ?? this.lastError,
      status: status ?? this.status,
      createdAt: createdAt ?? this.createdAt,
      nextRetryAt: nextRetryAt ?? this.nextRetryAt,
      appliedAt: appliedAt ?? this.appliedAt,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<int>(id.value);
    }
    if (clientId.present) {
      map['client_id'] = Variable<String>(clientId.value);
    }
    if (opKind.present) {
      map['op_kind'] = Variable<String>(opKind.value);
    }
    if (endpoint.present) {
      map['endpoint'] = Variable<String>(endpoint.value);
    }
    if (httpMethod.present) {
      map['http_method'] = Variable<String>(httpMethod.value);
    }
    if (payloadJson.present) {
      map['payload_json'] = Variable<String>(payloadJson.value);
    }
    if (headersJson.present) {
      map['headers_json'] = Variable<String>(headersJson.value);
    }
    if (attempts.present) {
      map['attempts'] = Variable<int>(attempts.value);
    }
    if (lastError.present) {
      map['last_error'] = Variable<String>(lastError.value);
    }
    if (status.present) {
      map['status'] = Variable<String>(status.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    if (nextRetryAt.present) {
      map['next_retry_at'] = Variable<DateTime>(nextRetryAt.value);
    }
    if (appliedAt.present) {
      map['applied_at'] = Variable<DateTime>(appliedAt.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('SyncQueueCompanion(')
          ..write('id: $id, ')
          ..write('clientId: $clientId, ')
          ..write('opKind: $opKind, ')
          ..write('endpoint: $endpoint, ')
          ..write('httpMethod: $httpMethod, ')
          ..write('payloadJson: $payloadJson, ')
          ..write('headersJson: $headersJson, ')
          ..write('attempts: $attempts, ')
          ..write('lastError: $lastError, ')
          ..write('status: $status, ')
          ..write('createdAt: $createdAt, ')
          ..write('nextRetryAt: $nextRetryAt, ')
          ..write('appliedAt: $appliedAt')
          ..write(')'))
        .toString();
  }
}

abstract class _$AppDatabase extends GeneratedDatabase {
  _$AppDatabase(QueryExecutor e) : super(e);
  $AppDatabaseManager get managers => $AppDatabaseManager(this);
  late final $ProfilesTable profiles = $ProfilesTable(this);
  late final $SyncQueueTable syncQueue = $SyncQueueTable(this);
  @override
  Iterable<TableInfo<Table, Object?>> get allTables =>
      allSchemaEntities.whereType<TableInfo<Table, Object?>>();
  @override
  List<DatabaseSchemaEntity> get allSchemaEntities => [profiles, syncQueue];
}

typedef $$ProfilesTableCreateCompanionBuilder =
    ProfilesCompanion Function({
      required String userId,
      required String email,
      Value<String?> name,
      Value<String?> sex,
      Value<DateTime?> birthDate,
      Value<double?> heightCm,
      Value<double?> baselineWeightKg,
      Value<String?> goal,
      Value<double?> targetWeightKg,
      Value<double?> targetMuscleKg,
      Value<DateTime?> goalStartedAt,
      Value<String?> trainingLevel,
      Value<int?> trainingFrequency,
      Value<String> allergiesJson,
      Value<String?> equipmentAvailableJson,
      Value<String?> photoUrl,
      Value<int?> bmrKcal,
      Value<DateTime?> onboardingCompletedAt,
      Value<bool> planRebuildRequired,
      required DateTime updatedAt,
      Value<bool> dirty,
      Value<int> rowid,
    });
typedef $$ProfilesTableUpdateCompanionBuilder =
    ProfilesCompanion Function({
      Value<String> userId,
      Value<String> email,
      Value<String?> name,
      Value<String?> sex,
      Value<DateTime?> birthDate,
      Value<double?> heightCm,
      Value<double?> baselineWeightKg,
      Value<String?> goal,
      Value<double?> targetWeightKg,
      Value<double?> targetMuscleKg,
      Value<DateTime?> goalStartedAt,
      Value<String?> trainingLevel,
      Value<int?> trainingFrequency,
      Value<String> allergiesJson,
      Value<String?> equipmentAvailableJson,
      Value<String?> photoUrl,
      Value<int?> bmrKcal,
      Value<DateTime?> onboardingCompletedAt,
      Value<bool> planRebuildRequired,
      Value<DateTime> updatedAt,
      Value<bool> dirty,
      Value<int> rowid,
    });

class $$ProfilesTableFilterComposer
    extends Composer<_$AppDatabase, $ProfilesTable> {
  $$ProfilesTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get userId => $composableBuilder(
    column: $table.userId,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get email => $composableBuilder(
    column: $table.email,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get name => $composableBuilder(
    column: $table.name,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get sex => $composableBuilder(
    column: $table.sex,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get birthDate => $composableBuilder(
    column: $table.birthDate,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<double> get heightCm => $composableBuilder(
    column: $table.heightCm,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<double> get baselineWeightKg => $composableBuilder(
    column: $table.baselineWeightKg,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get goal => $composableBuilder(
    column: $table.goal,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<double> get targetWeightKg => $composableBuilder(
    column: $table.targetWeightKg,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<double> get targetMuscleKg => $composableBuilder(
    column: $table.targetMuscleKg,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get goalStartedAt => $composableBuilder(
    column: $table.goalStartedAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get trainingLevel => $composableBuilder(
    column: $table.trainingLevel,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get trainingFrequency => $composableBuilder(
    column: $table.trainingFrequency,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get allergiesJson => $composableBuilder(
    column: $table.allergiesJson,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get equipmentAvailableJson => $composableBuilder(
    column: $table.equipmentAvailableJson,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get photoUrl => $composableBuilder(
    column: $table.photoUrl,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get bmrKcal => $composableBuilder(
    column: $table.bmrKcal,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get onboardingCompletedAt => $composableBuilder(
    column: $table.onboardingCompletedAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<bool> get planRebuildRequired => $composableBuilder(
    column: $table.planRebuildRequired,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get updatedAt => $composableBuilder(
    column: $table.updatedAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<bool> get dirty => $composableBuilder(
    column: $table.dirty,
    builder: (column) => ColumnFilters(column),
  );
}

class $$ProfilesTableOrderingComposer
    extends Composer<_$AppDatabase, $ProfilesTable> {
  $$ProfilesTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get userId => $composableBuilder(
    column: $table.userId,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get email => $composableBuilder(
    column: $table.email,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get name => $composableBuilder(
    column: $table.name,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get sex => $composableBuilder(
    column: $table.sex,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get birthDate => $composableBuilder(
    column: $table.birthDate,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<double> get heightCm => $composableBuilder(
    column: $table.heightCm,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<double> get baselineWeightKg => $composableBuilder(
    column: $table.baselineWeightKg,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get goal => $composableBuilder(
    column: $table.goal,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<double> get targetWeightKg => $composableBuilder(
    column: $table.targetWeightKg,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<double> get targetMuscleKg => $composableBuilder(
    column: $table.targetMuscleKg,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get goalStartedAt => $composableBuilder(
    column: $table.goalStartedAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get trainingLevel => $composableBuilder(
    column: $table.trainingLevel,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get trainingFrequency => $composableBuilder(
    column: $table.trainingFrequency,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get allergiesJson => $composableBuilder(
    column: $table.allergiesJson,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get equipmentAvailableJson => $composableBuilder(
    column: $table.equipmentAvailableJson,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get photoUrl => $composableBuilder(
    column: $table.photoUrl,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get bmrKcal => $composableBuilder(
    column: $table.bmrKcal,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get onboardingCompletedAt => $composableBuilder(
    column: $table.onboardingCompletedAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<bool> get planRebuildRequired => $composableBuilder(
    column: $table.planRebuildRequired,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get updatedAt => $composableBuilder(
    column: $table.updatedAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<bool> get dirty => $composableBuilder(
    column: $table.dirty,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$ProfilesTableAnnotationComposer
    extends Composer<_$AppDatabase, $ProfilesTable> {
  $$ProfilesTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get userId =>
      $composableBuilder(column: $table.userId, builder: (column) => column);

  GeneratedColumn<String> get email =>
      $composableBuilder(column: $table.email, builder: (column) => column);

  GeneratedColumn<String> get name =>
      $composableBuilder(column: $table.name, builder: (column) => column);

  GeneratedColumn<String> get sex =>
      $composableBuilder(column: $table.sex, builder: (column) => column);

  GeneratedColumn<DateTime> get birthDate =>
      $composableBuilder(column: $table.birthDate, builder: (column) => column);

  GeneratedColumn<double> get heightCm =>
      $composableBuilder(column: $table.heightCm, builder: (column) => column);

  GeneratedColumn<double> get baselineWeightKg => $composableBuilder(
    column: $table.baselineWeightKg,
    builder: (column) => column,
  );

  GeneratedColumn<String> get goal =>
      $composableBuilder(column: $table.goal, builder: (column) => column);

  GeneratedColumn<double> get targetWeightKg => $composableBuilder(
    column: $table.targetWeightKg,
    builder: (column) => column,
  );

  GeneratedColumn<double> get targetMuscleKg => $composableBuilder(
    column: $table.targetMuscleKg,
    builder: (column) => column,
  );

  GeneratedColumn<DateTime> get goalStartedAt => $composableBuilder(
    column: $table.goalStartedAt,
    builder: (column) => column,
  );

  GeneratedColumn<String> get trainingLevel => $composableBuilder(
    column: $table.trainingLevel,
    builder: (column) => column,
  );

  GeneratedColumn<int> get trainingFrequency => $composableBuilder(
    column: $table.trainingFrequency,
    builder: (column) => column,
  );

  GeneratedColumn<String> get allergiesJson => $composableBuilder(
    column: $table.allergiesJson,
    builder: (column) => column,
  );

  GeneratedColumn<String> get equipmentAvailableJson => $composableBuilder(
    column: $table.equipmentAvailableJson,
    builder: (column) => column,
  );

  GeneratedColumn<String> get photoUrl =>
      $composableBuilder(column: $table.photoUrl, builder: (column) => column);

  GeneratedColumn<int> get bmrKcal =>
      $composableBuilder(column: $table.bmrKcal, builder: (column) => column);

  GeneratedColumn<DateTime> get onboardingCompletedAt => $composableBuilder(
    column: $table.onboardingCompletedAt,
    builder: (column) => column,
  );

  GeneratedColumn<bool> get planRebuildRequired => $composableBuilder(
    column: $table.planRebuildRequired,
    builder: (column) => column,
  );

  GeneratedColumn<DateTime> get updatedAt =>
      $composableBuilder(column: $table.updatedAt, builder: (column) => column);

  GeneratedColumn<bool> get dirty =>
      $composableBuilder(column: $table.dirty, builder: (column) => column);
}

class $$ProfilesTableTableManager
    extends
        RootTableManager<
          _$AppDatabase,
          $ProfilesTable,
          Profile,
          $$ProfilesTableFilterComposer,
          $$ProfilesTableOrderingComposer,
          $$ProfilesTableAnnotationComposer,
          $$ProfilesTableCreateCompanionBuilder,
          $$ProfilesTableUpdateCompanionBuilder,
          (Profile, BaseReferences<_$AppDatabase, $ProfilesTable, Profile>),
          Profile,
          PrefetchHooks Function()
        > {
  $$ProfilesTableTableManager(_$AppDatabase db, $ProfilesTable table)
    : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$ProfilesTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$ProfilesTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$ProfilesTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback:
              ({
                Value<String> userId = const Value.absent(),
                Value<String> email = const Value.absent(),
                Value<String?> name = const Value.absent(),
                Value<String?> sex = const Value.absent(),
                Value<DateTime?> birthDate = const Value.absent(),
                Value<double?> heightCm = const Value.absent(),
                Value<double?> baselineWeightKg = const Value.absent(),
                Value<String?> goal = const Value.absent(),
                Value<double?> targetWeightKg = const Value.absent(),
                Value<double?> targetMuscleKg = const Value.absent(),
                Value<DateTime?> goalStartedAt = const Value.absent(),
                Value<String?> trainingLevel = const Value.absent(),
                Value<int?> trainingFrequency = const Value.absent(),
                Value<String> allergiesJson = const Value.absent(),
                Value<String?> equipmentAvailableJson = const Value.absent(),
                Value<String?> photoUrl = const Value.absent(),
                Value<int?> bmrKcal = const Value.absent(),
                Value<DateTime?> onboardingCompletedAt = const Value.absent(),
                Value<bool> planRebuildRequired = const Value.absent(),
                Value<DateTime> updatedAt = const Value.absent(),
                Value<bool> dirty = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => ProfilesCompanion(
                userId: userId,
                email: email,
                name: name,
                sex: sex,
                birthDate: birthDate,
                heightCm: heightCm,
                baselineWeightKg: baselineWeightKg,
                goal: goal,
                targetWeightKg: targetWeightKg,
                targetMuscleKg: targetMuscleKg,
                goalStartedAt: goalStartedAt,
                trainingLevel: trainingLevel,
                trainingFrequency: trainingFrequency,
                allergiesJson: allergiesJson,
                equipmentAvailableJson: equipmentAvailableJson,
                photoUrl: photoUrl,
                bmrKcal: bmrKcal,
                onboardingCompletedAt: onboardingCompletedAt,
                planRebuildRequired: planRebuildRequired,
                updatedAt: updatedAt,
                dirty: dirty,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String userId,
                required String email,
                Value<String?> name = const Value.absent(),
                Value<String?> sex = const Value.absent(),
                Value<DateTime?> birthDate = const Value.absent(),
                Value<double?> heightCm = const Value.absent(),
                Value<double?> baselineWeightKg = const Value.absent(),
                Value<String?> goal = const Value.absent(),
                Value<double?> targetWeightKg = const Value.absent(),
                Value<double?> targetMuscleKg = const Value.absent(),
                Value<DateTime?> goalStartedAt = const Value.absent(),
                Value<String?> trainingLevel = const Value.absent(),
                Value<int?> trainingFrequency = const Value.absent(),
                Value<String> allergiesJson = const Value.absent(),
                Value<String?> equipmentAvailableJson = const Value.absent(),
                Value<String?> photoUrl = const Value.absent(),
                Value<int?> bmrKcal = const Value.absent(),
                Value<DateTime?> onboardingCompletedAt = const Value.absent(),
                Value<bool> planRebuildRequired = const Value.absent(),
                required DateTime updatedAt,
                Value<bool> dirty = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => ProfilesCompanion.insert(
                userId: userId,
                email: email,
                name: name,
                sex: sex,
                birthDate: birthDate,
                heightCm: heightCm,
                baselineWeightKg: baselineWeightKg,
                goal: goal,
                targetWeightKg: targetWeightKg,
                targetMuscleKg: targetMuscleKg,
                goalStartedAt: goalStartedAt,
                trainingLevel: trainingLevel,
                trainingFrequency: trainingFrequency,
                allergiesJson: allergiesJson,
                equipmentAvailableJson: equipmentAvailableJson,
                photoUrl: photoUrl,
                bmrKcal: bmrKcal,
                onboardingCompletedAt: onboardingCompletedAt,
                planRebuildRequired: planRebuildRequired,
                updatedAt: updatedAt,
                dirty: dirty,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$ProfilesTableProcessedTableManager =
    ProcessedTableManager<
      _$AppDatabase,
      $ProfilesTable,
      Profile,
      $$ProfilesTableFilterComposer,
      $$ProfilesTableOrderingComposer,
      $$ProfilesTableAnnotationComposer,
      $$ProfilesTableCreateCompanionBuilder,
      $$ProfilesTableUpdateCompanionBuilder,
      (Profile, BaseReferences<_$AppDatabase, $ProfilesTable, Profile>),
      Profile,
      PrefetchHooks Function()
    >;
typedef $$SyncQueueTableCreateCompanionBuilder =
    SyncQueueCompanion Function({
      Value<int> id,
      required String clientId,
      required String opKind,
      required String endpoint,
      required String httpMethod,
      required String payloadJson,
      Value<String?> headersJson,
      Value<int> attempts,
      Value<String?> lastError,
      Value<String> status,
      Value<DateTime> createdAt,
      Value<DateTime?> nextRetryAt,
      Value<DateTime?> appliedAt,
    });
typedef $$SyncQueueTableUpdateCompanionBuilder =
    SyncQueueCompanion Function({
      Value<int> id,
      Value<String> clientId,
      Value<String> opKind,
      Value<String> endpoint,
      Value<String> httpMethod,
      Value<String> payloadJson,
      Value<String?> headersJson,
      Value<int> attempts,
      Value<String?> lastError,
      Value<String> status,
      Value<DateTime> createdAt,
      Value<DateTime?> nextRetryAt,
      Value<DateTime?> appliedAt,
    });

class $$SyncQueueTableFilterComposer
    extends Composer<_$AppDatabase, $SyncQueueTable> {
  $$SyncQueueTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<int> get id => $composableBuilder(
    column: $table.id,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get clientId => $composableBuilder(
    column: $table.clientId,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get opKind => $composableBuilder(
    column: $table.opKind,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get endpoint => $composableBuilder(
    column: $table.endpoint,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get httpMethod => $composableBuilder(
    column: $table.httpMethod,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get payloadJson => $composableBuilder(
    column: $table.payloadJson,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get headersJson => $composableBuilder(
    column: $table.headersJson,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get attempts => $composableBuilder(
    column: $table.attempts,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get lastError => $composableBuilder(
    column: $table.lastError,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get status => $composableBuilder(
    column: $table.status,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
    column: $table.createdAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get nextRetryAt => $composableBuilder(
    column: $table.nextRetryAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get appliedAt => $composableBuilder(
    column: $table.appliedAt,
    builder: (column) => ColumnFilters(column),
  );
}

class $$SyncQueueTableOrderingComposer
    extends Composer<_$AppDatabase, $SyncQueueTable> {
  $$SyncQueueTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<int> get id => $composableBuilder(
    column: $table.id,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get clientId => $composableBuilder(
    column: $table.clientId,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get opKind => $composableBuilder(
    column: $table.opKind,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get endpoint => $composableBuilder(
    column: $table.endpoint,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get httpMethod => $composableBuilder(
    column: $table.httpMethod,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get payloadJson => $composableBuilder(
    column: $table.payloadJson,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get headersJson => $composableBuilder(
    column: $table.headersJson,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get attempts => $composableBuilder(
    column: $table.attempts,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get lastError => $composableBuilder(
    column: $table.lastError,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get status => $composableBuilder(
    column: $table.status,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
    column: $table.createdAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get nextRetryAt => $composableBuilder(
    column: $table.nextRetryAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get appliedAt => $composableBuilder(
    column: $table.appliedAt,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$SyncQueueTableAnnotationComposer
    extends Composer<_$AppDatabase, $SyncQueueTable> {
  $$SyncQueueTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<int> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get clientId =>
      $composableBuilder(column: $table.clientId, builder: (column) => column);

  GeneratedColumn<String> get opKind =>
      $composableBuilder(column: $table.opKind, builder: (column) => column);

  GeneratedColumn<String> get endpoint =>
      $composableBuilder(column: $table.endpoint, builder: (column) => column);

  GeneratedColumn<String> get httpMethod => $composableBuilder(
    column: $table.httpMethod,
    builder: (column) => column,
  );

  GeneratedColumn<String> get payloadJson => $composableBuilder(
    column: $table.payloadJson,
    builder: (column) => column,
  );

  GeneratedColumn<String> get headersJson => $composableBuilder(
    column: $table.headersJson,
    builder: (column) => column,
  );

  GeneratedColumn<int> get attempts =>
      $composableBuilder(column: $table.attempts, builder: (column) => column);

  GeneratedColumn<String> get lastError =>
      $composableBuilder(column: $table.lastError, builder: (column) => column);

  GeneratedColumn<String> get status =>
      $composableBuilder(column: $table.status, builder: (column) => column);

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);

  GeneratedColumn<DateTime> get nextRetryAt => $composableBuilder(
    column: $table.nextRetryAt,
    builder: (column) => column,
  );

  GeneratedColumn<DateTime> get appliedAt =>
      $composableBuilder(column: $table.appliedAt, builder: (column) => column);
}

class $$SyncQueueTableTableManager
    extends
        RootTableManager<
          _$AppDatabase,
          $SyncQueueTable,
          SyncQueueData,
          $$SyncQueueTableFilterComposer,
          $$SyncQueueTableOrderingComposer,
          $$SyncQueueTableAnnotationComposer,
          $$SyncQueueTableCreateCompanionBuilder,
          $$SyncQueueTableUpdateCompanionBuilder,
          (
            SyncQueueData,
            BaseReferences<_$AppDatabase, $SyncQueueTable, SyncQueueData>,
          ),
          SyncQueueData,
          PrefetchHooks Function()
        > {
  $$SyncQueueTableTableManager(_$AppDatabase db, $SyncQueueTable table)
    : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$SyncQueueTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$SyncQueueTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$SyncQueueTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback:
              ({
                Value<int> id = const Value.absent(),
                Value<String> clientId = const Value.absent(),
                Value<String> opKind = const Value.absent(),
                Value<String> endpoint = const Value.absent(),
                Value<String> httpMethod = const Value.absent(),
                Value<String> payloadJson = const Value.absent(),
                Value<String?> headersJson = const Value.absent(),
                Value<int> attempts = const Value.absent(),
                Value<String?> lastError = const Value.absent(),
                Value<String> status = const Value.absent(),
                Value<DateTime> createdAt = const Value.absent(),
                Value<DateTime?> nextRetryAt = const Value.absent(),
                Value<DateTime?> appliedAt = const Value.absent(),
              }) => SyncQueueCompanion(
                id: id,
                clientId: clientId,
                opKind: opKind,
                endpoint: endpoint,
                httpMethod: httpMethod,
                payloadJson: payloadJson,
                headersJson: headersJson,
                attempts: attempts,
                lastError: lastError,
                status: status,
                createdAt: createdAt,
                nextRetryAt: nextRetryAt,
                appliedAt: appliedAt,
              ),
          createCompanionCallback:
              ({
                Value<int> id = const Value.absent(),
                required String clientId,
                required String opKind,
                required String endpoint,
                required String httpMethod,
                required String payloadJson,
                Value<String?> headersJson = const Value.absent(),
                Value<int> attempts = const Value.absent(),
                Value<String?> lastError = const Value.absent(),
                Value<String> status = const Value.absent(),
                Value<DateTime> createdAt = const Value.absent(),
                Value<DateTime?> nextRetryAt = const Value.absent(),
                Value<DateTime?> appliedAt = const Value.absent(),
              }) => SyncQueueCompanion.insert(
                id: id,
                clientId: clientId,
                opKind: opKind,
                endpoint: endpoint,
                httpMethod: httpMethod,
                payloadJson: payloadJson,
                headersJson: headersJson,
                attempts: attempts,
                lastError: lastError,
                status: status,
                createdAt: createdAt,
                nextRetryAt: nextRetryAt,
                appliedAt: appliedAt,
              ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$SyncQueueTableProcessedTableManager =
    ProcessedTableManager<
      _$AppDatabase,
      $SyncQueueTable,
      SyncQueueData,
      $$SyncQueueTableFilterComposer,
      $$SyncQueueTableOrderingComposer,
      $$SyncQueueTableAnnotationComposer,
      $$SyncQueueTableCreateCompanionBuilder,
      $$SyncQueueTableUpdateCompanionBuilder,
      (
        SyncQueueData,
        BaseReferences<_$AppDatabase, $SyncQueueTable, SyncQueueData>,
      ),
      SyncQueueData,
      PrefetchHooks Function()
    >;

class $AppDatabaseManager {
  final _$AppDatabase _db;
  $AppDatabaseManager(this._db);
  $$ProfilesTableTableManager get profiles =>
      $$ProfilesTableTableManager(_db, _db.profiles);
  $$SyncQueueTableTableManager get syncQueue =>
      $$SyncQueueTableTableManager(_db, _db.syncQueue);
}
