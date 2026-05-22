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

class $LocalWorkoutsTable extends LocalWorkouts
    with TableInfo<$LocalWorkoutsTable, LocalWorkout> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $LocalWorkoutsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
    'id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _userIdMeta = const VerificationMeta('userId');
  @override
  late final GeneratedColumn<String> userId = GeneratedColumn<String>(
    'user_id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _clientIdMeta = const VerificationMeta(
    'clientId',
  );
  @override
  late final GeneratedColumn<String> clientId = GeneratedColumn<String>(
    'client_id',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _performedAtMeta = const VerificationMeta(
    'performedAt',
  );
  @override
  late final GeneratedColumn<DateTime> performedAt = GeneratedColumn<DateTime>(
    'performed_at',
    aliasedName,
    false,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _finishedAtMeta = const VerificationMeta(
    'finishedAt',
  );
  @override
  late final GeneratedColumn<DateTime> finishedAt = GeneratedColumn<DateTime>(
    'finished_at',
    aliasedName,
    true,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _statusMeta = const VerificationMeta('status');
  @override
  late final GeneratedColumn<String> status = GeneratedColumn<String>(
    'status',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _originMeta = const VerificationMeta('origin');
  @override
  late final GeneratedColumn<String> origin = GeneratedColumn<String>(
    'origin',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _planDayIdMeta = const VerificationMeta(
    'planDayId',
  );
  @override
  late final GeneratedColumn<String> planDayId = GeneratedColumn<String>(
    'plan_day_id',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _notesMeta = const VerificationMeta('notes');
  @override
  late final GeneratedColumn<String> notes = GeneratedColumn<String>(
    'notes',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _syncStatusMeta = const VerificationMeta(
    'syncStatus',
  );
  @override
  late final GeneratedColumn<String> syncStatus = GeneratedColumn<String>(
    'sync_status',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant('synced'),
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
  @override
  List<GeneratedColumn> get $columns => [
    id,
    userId,
    clientId,
    performedAt,
    finishedAt,
    status,
    origin,
    planDayId,
    notes,
    syncStatus,
    createdAt,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'workouts';
  @override
  VerificationContext validateIntegrity(
    Insertable<LocalWorkout> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    } else if (isInserting) {
      context.missing(_idMeta);
    }
    if (data.containsKey('user_id')) {
      context.handle(
        _userIdMeta,
        userId.isAcceptableOrUnknown(data['user_id']!, _userIdMeta),
      );
    } else if (isInserting) {
      context.missing(_userIdMeta);
    }
    if (data.containsKey('client_id')) {
      context.handle(
        _clientIdMeta,
        clientId.isAcceptableOrUnknown(data['client_id']!, _clientIdMeta),
      );
    }
    if (data.containsKey('performed_at')) {
      context.handle(
        _performedAtMeta,
        performedAt.isAcceptableOrUnknown(
          data['performed_at']!,
          _performedAtMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_performedAtMeta);
    }
    if (data.containsKey('finished_at')) {
      context.handle(
        _finishedAtMeta,
        finishedAt.isAcceptableOrUnknown(data['finished_at']!, _finishedAtMeta),
      );
    }
    if (data.containsKey('status')) {
      context.handle(
        _statusMeta,
        status.isAcceptableOrUnknown(data['status']!, _statusMeta),
      );
    } else if (isInserting) {
      context.missing(_statusMeta);
    }
    if (data.containsKey('origin')) {
      context.handle(
        _originMeta,
        origin.isAcceptableOrUnknown(data['origin']!, _originMeta),
      );
    } else if (isInserting) {
      context.missing(_originMeta);
    }
    if (data.containsKey('plan_day_id')) {
      context.handle(
        _planDayIdMeta,
        planDayId.isAcceptableOrUnknown(data['plan_day_id']!, _planDayIdMeta),
      );
    }
    if (data.containsKey('notes')) {
      context.handle(
        _notesMeta,
        notes.isAcceptableOrUnknown(data['notes']!, _notesMeta),
      );
    }
    if (data.containsKey('sync_status')) {
      context.handle(
        _syncStatusMeta,
        syncStatus.isAcceptableOrUnknown(data['sync_status']!, _syncStatusMeta),
      );
    }
    if (data.containsKey('created_at')) {
      context.handle(
        _createdAtMeta,
        createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta),
      );
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  LocalWorkout map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return LocalWorkout(
      id: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}id'],
      )!,
      userId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}user_id'],
      )!,
      clientId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}client_id'],
      ),
      performedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}performed_at'],
      )!,
      finishedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}finished_at'],
      ),
      status: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}status'],
      )!,
      origin: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}origin'],
      )!,
      planDayId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}plan_day_id'],
      ),
      notes: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}notes'],
      ),
      syncStatus: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}sync_status'],
      )!,
      createdAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}created_at'],
      )!,
    );
  }

  @override
  $LocalWorkoutsTable createAlias(String alias) {
    return $LocalWorkoutsTable(attachedDatabase, alias);
  }
}

class LocalWorkout extends DataClass implements Insertable<LocalWorkout> {
  final String id;
  final String userId;
  final String? clientId;
  final DateTime performedAt;
  final DateTime? finishedAt;
  final String status;
  final String origin;
  final String? planDayId;
  final String? notes;
  final String syncStatus;
  final DateTime createdAt;
  const LocalWorkout({
    required this.id,
    required this.userId,
    this.clientId,
    required this.performedAt,
    this.finishedAt,
    required this.status,
    required this.origin,
    this.planDayId,
    this.notes,
    required this.syncStatus,
    required this.createdAt,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    map['user_id'] = Variable<String>(userId);
    if (!nullToAbsent || clientId != null) {
      map['client_id'] = Variable<String>(clientId);
    }
    map['performed_at'] = Variable<DateTime>(performedAt);
    if (!nullToAbsent || finishedAt != null) {
      map['finished_at'] = Variable<DateTime>(finishedAt);
    }
    map['status'] = Variable<String>(status);
    map['origin'] = Variable<String>(origin);
    if (!nullToAbsent || planDayId != null) {
      map['plan_day_id'] = Variable<String>(planDayId);
    }
    if (!nullToAbsent || notes != null) {
      map['notes'] = Variable<String>(notes);
    }
    map['sync_status'] = Variable<String>(syncStatus);
    map['created_at'] = Variable<DateTime>(createdAt);
    return map;
  }

  LocalWorkoutsCompanion toCompanion(bool nullToAbsent) {
    return LocalWorkoutsCompanion(
      id: Value(id),
      userId: Value(userId),
      clientId: clientId == null && nullToAbsent
          ? const Value.absent()
          : Value(clientId),
      performedAt: Value(performedAt),
      finishedAt: finishedAt == null && nullToAbsent
          ? const Value.absent()
          : Value(finishedAt),
      status: Value(status),
      origin: Value(origin),
      planDayId: planDayId == null && nullToAbsent
          ? const Value.absent()
          : Value(planDayId),
      notes: notes == null && nullToAbsent
          ? const Value.absent()
          : Value(notes),
      syncStatus: Value(syncStatus),
      createdAt: Value(createdAt),
    );
  }

  factory LocalWorkout.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return LocalWorkout(
      id: serializer.fromJson<String>(json['id']),
      userId: serializer.fromJson<String>(json['userId']),
      clientId: serializer.fromJson<String?>(json['clientId']),
      performedAt: serializer.fromJson<DateTime>(json['performedAt']),
      finishedAt: serializer.fromJson<DateTime?>(json['finishedAt']),
      status: serializer.fromJson<String>(json['status']),
      origin: serializer.fromJson<String>(json['origin']),
      planDayId: serializer.fromJson<String?>(json['planDayId']),
      notes: serializer.fromJson<String?>(json['notes']),
      syncStatus: serializer.fromJson<String>(json['syncStatus']),
      createdAt: serializer.fromJson<DateTime>(json['createdAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'userId': serializer.toJson<String>(userId),
      'clientId': serializer.toJson<String?>(clientId),
      'performedAt': serializer.toJson<DateTime>(performedAt),
      'finishedAt': serializer.toJson<DateTime?>(finishedAt),
      'status': serializer.toJson<String>(status),
      'origin': serializer.toJson<String>(origin),
      'planDayId': serializer.toJson<String?>(planDayId),
      'notes': serializer.toJson<String?>(notes),
      'syncStatus': serializer.toJson<String>(syncStatus),
      'createdAt': serializer.toJson<DateTime>(createdAt),
    };
  }

  LocalWorkout copyWith({
    String? id,
    String? userId,
    Value<String?> clientId = const Value.absent(),
    DateTime? performedAt,
    Value<DateTime?> finishedAt = const Value.absent(),
    String? status,
    String? origin,
    Value<String?> planDayId = const Value.absent(),
    Value<String?> notes = const Value.absent(),
    String? syncStatus,
    DateTime? createdAt,
  }) => LocalWorkout(
    id: id ?? this.id,
    userId: userId ?? this.userId,
    clientId: clientId.present ? clientId.value : this.clientId,
    performedAt: performedAt ?? this.performedAt,
    finishedAt: finishedAt.present ? finishedAt.value : this.finishedAt,
    status: status ?? this.status,
    origin: origin ?? this.origin,
    planDayId: planDayId.present ? planDayId.value : this.planDayId,
    notes: notes.present ? notes.value : this.notes,
    syncStatus: syncStatus ?? this.syncStatus,
    createdAt: createdAt ?? this.createdAt,
  );
  LocalWorkout copyWithCompanion(LocalWorkoutsCompanion data) {
    return LocalWorkout(
      id: data.id.present ? data.id.value : this.id,
      userId: data.userId.present ? data.userId.value : this.userId,
      clientId: data.clientId.present ? data.clientId.value : this.clientId,
      performedAt: data.performedAt.present
          ? data.performedAt.value
          : this.performedAt,
      finishedAt: data.finishedAt.present
          ? data.finishedAt.value
          : this.finishedAt,
      status: data.status.present ? data.status.value : this.status,
      origin: data.origin.present ? data.origin.value : this.origin,
      planDayId: data.planDayId.present ? data.planDayId.value : this.planDayId,
      notes: data.notes.present ? data.notes.value : this.notes,
      syncStatus: data.syncStatus.present
          ? data.syncStatus.value
          : this.syncStatus,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('LocalWorkout(')
          ..write('id: $id, ')
          ..write('userId: $userId, ')
          ..write('clientId: $clientId, ')
          ..write('performedAt: $performedAt, ')
          ..write('finishedAt: $finishedAt, ')
          ..write('status: $status, ')
          ..write('origin: $origin, ')
          ..write('planDayId: $planDayId, ')
          ..write('notes: $notes, ')
          ..write('syncStatus: $syncStatus, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    id,
    userId,
    clientId,
    performedAt,
    finishedAt,
    status,
    origin,
    planDayId,
    notes,
    syncStatus,
    createdAt,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is LocalWorkout &&
          other.id == this.id &&
          other.userId == this.userId &&
          other.clientId == this.clientId &&
          other.performedAt == this.performedAt &&
          other.finishedAt == this.finishedAt &&
          other.status == this.status &&
          other.origin == this.origin &&
          other.planDayId == this.planDayId &&
          other.notes == this.notes &&
          other.syncStatus == this.syncStatus &&
          other.createdAt == this.createdAt);
}

class LocalWorkoutsCompanion extends UpdateCompanion<LocalWorkout> {
  final Value<String> id;
  final Value<String> userId;
  final Value<String?> clientId;
  final Value<DateTime> performedAt;
  final Value<DateTime?> finishedAt;
  final Value<String> status;
  final Value<String> origin;
  final Value<String?> planDayId;
  final Value<String?> notes;
  final Value<String> syncStatus;
  final Value<DateTime> createdAt;
  final Value<int> rowid;
  const LocalWorkoutsCompanion({
    this.id = const Value.absent(),
    this.userId = const Value.absent(),
    this.clientId = const Value.absent(),
    this.performedAt = const Value.absent(),
    this.finishedAt = const Value.absent(),
    this.status = const Value.absent(),
    this.origin = const Value.absent(),
    this.planDayId = const Value.absent(),
    this.notes = const Value.absent(),
    this.syncStatus = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  LocalWorkoutsCompanion.insert({
    required String id,
    required String userId,
    this.clientId = const Value.absent(),
    required DateTime performedAt,
    this.finishedAt = const Value.absent(),
    required String status,
    required String origin,
    this.planDayId = const Value.absent(),
    this.notes = const Value.absent(),
    this.syncStatus = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.rowid = const Value.absent(),
  }) : id = Value(id),
       userId = Value(userId),
       performedAt = Value(performedAt),
       status = Value(status),
       origin = Value(origin);
  static Insertable<LocalWorkout> custom({
    Expression<String>? id,
    Expression<String>? userId,
    Expression<String>? clientId,
    Expression<DateTime>? performedAt,
    Expression<DateTime>? finishedAt,
    Expression<String>? status,
    Expression<String>? origin,
    Expression<String>? planDayId,
    Expression<String>? notes,
    Expression<String>? syncStatus,
    Expression<DateTime>? createdAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (userId != null) 'user_id': userId,
      if (clientId != null) 'client_id': clientId,
      if (performedAt != null) 'performed_at': performedAt,
      if (finishedAt != null) 'finished_at': finishedAt,
      if (status != null) 'status': status,
      if (origin != null) 'origin': origin,
      if (planDayId != null) 'plan_day_id': planDayId,
      if (notes != null) 'notes': notes,
      if (syncStatus != null) 'sync_status': syncStatus,
      if (createdAt != null) 'created_at': createdAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  LocalWorkoutsCompanion copyWith({
    Value<String>? id,
    Value<String>? userId,
    Value<String?>? clientId,
    Value<DateTime>? performedAt,
    Value<DateTime?>? finishedAt,
    Value<String>? status,
    Value<String>? origin,
    Value<String?>? planDayId,
    Value<String?>? notes,
    Value<String>? syncStatus,
    Value<DateTime>? createdAt,
    Value<int>? rowid,
  }) {
    return LocalWorkoutsCompanion(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      clientId: clientId ?? this.clientId,
      performedAt: performedAt ?? this.performedAt,
      finishedAt: finishedAt ?? this.finishedAt,
      status: status ?? this.status,
      origin: origin ?? this.origin,
      planDayId: planDayId ?? this.planDayId,
      notes: notes ?? this.notes,
      syncStatus: syncStatus ?? this.syncStatus,
      createdAt: createdAt ?? this.createdAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<String>(id.value);
    }
    if (userId.present) {
      map['user_id'] = Variable<String>(userId.value);
    }
    if (clientId.present) {
      map['client_id'] = Variable<String>(clientId.value);
    }
    if (performedAt.present) {
      map['performed_at'] = Variable<DateTime>(performedAt.value);
    }
    if (finishedAt.present) {
      map['finished_at'] = Variable<DateTime>(finishedAt.value);
    }
    if (status.present) {
      map['status'] = Variable<String>(status.value);
    }
    if (origin.present) {
      map['origin'] = Variable<String>(origin.value);
    }
    if (planDayId.present) {
      map['plan_day_id'] = Variable<String>(planDayId.value);
    }
    if (notes.present) {
      map['notes'] = Variable<String>(notes.value);
    }
    if (syncStatus.present) {
      map['sync_status'] = Variable<String>(syncStatus.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('LocalWorkoutsCompanion(')
          ..write('id: $id, ')
          ..write('userId: $userId, ')
          ..write('clientId: $clientId, ')
          ..write('performedAt: $performedAt, ')
          ..write('finishedAt: $finishedAt, ')
          ..write('status: $status, ')
          ..write('origin: $origin, ')
          ..write('planDayId: $planDayId, ')
          ..write('notes: $notes, ')
          ..write('syncStatus: $syncStatus, ')
          ..write('createdAt: $createdAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $LocalExerciseLogsTable extends LocalExerciseLogs
    with TableInfo<$LocalExerciseLogsTable, LocalExerciseLog> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $LocalExerciseLogsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
    'id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _workoutIdMeta = const VerificationMeta(
    'workoutId',
  );
  @override
  late final GeneratedColumn<String> workoutId = GeneratedColumn<String>(
    'workout_id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _exerciseIdMeta = const VerificationMeta(
    'exerciseId',
  );
  @override
  late final GeneratedColumn<String> exerciseId = GeneratedColumn<String>(
    'exercise_id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _clientIdMeta = const VerificationMeta(
    'clientId',
  );
  @override
  late final GeneratedColumn<String> clientId = GeneratedColumn<String>(
    'client_id',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _setNumberMeta = const VerificationMeta(
    'setNumber',
  );
  @override
  late final GeneratedColumn<int> setNumber = GeneratedColumn<int>(
    'set_number',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _repsMeta = const VerificationMeta('reps');
  @override
  late final GeneratedColumn<int> reps = GeneratedColumn<int>(
    'reps',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _weightKgMeta = const VerificationMeta(
    'weightKg',
  );
  @override
  late final GeneratedColumn<double> weightKg = GeneratedColumn<double>(
    'weight_kg',
    aliasedName,
    false,
    type: DriftSqlType.double,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _rpeMeta = const VerificationMeta('rpe');
  @override
  late final GeneratedColumn<int> rpe = GeneratedColumn<int>(
    'rpe',
    aliasedName,
    true,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _restSecondsMeta = const VerificationMeta(
    'restSeconds',
  );
  @override
  late final GeneratedColumn<int> restSeconds = GeneratedColumn<int>(
    'rest_seconds',
    aliasedName,
    true,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _skippedMeta = const VerificationMeta(
    'skipped',
  );
  @override
  late final GeneratedColumn<bool> skipped = GeneratedColumn<bool>(
    'skipped',
    aliasedName,
    false,
    type: DriftSqlType.bool,
    requiredDuringInsert: false,
    defaultConstraints: GeneratedColumn.constraintIsAlways(
      'CHECK ("skipped" IN (0, 1))',
    ),
    defaultValue: const Constant(false),
  );
  static const VerificationMeta _loggedAtMeta = const VerificationMeta(
    'loggedAt',
  );
  @override
  late final GeneratedColumn<DateTime> loggedAt = GeneratedColumn<DateTime>(
    'logged_at',
    aliasedName,
    false,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _syncStatusMeta = const VerificationMeta(
    'syncStatus',
  );
  @override
  late final GeneratedColumn<String> syncStatus = GeneratedColumn<String>(
    'sync_status',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant('synced'),
  );
  @override
  List<GeneratedColumn> get $columns => [
    id,
    workoutId,
    exerciseId,
    clientId,
    setNumber,
    reps,
    weightKg,
    rpe,
    restSeconds,
    skipped,
    loggedAt,
    syncStatus,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'exercise_logs';
  @override
  VerificationContext validateIntegrity(
    Insertable<LocalExerciseLog> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    } else if (isInserting) {
      context.missing(_idMeta);
    }
    if (data.containsKey('workout_id')) {
      context.handle(
        _workoutIdMeta,
        workoutId.isAcceptableOrUnknown(data['workout_id']!, _workoutIdMeta),
      );
    } else if (isInserting) {
      context.missing(_workoutIdMeta);
    }
    if (data.containsKey('exercise_id')) {
      context.handle(
        _exerciseIdMeta,
        exerciseId.isAcceptableOrUnknown(data['exercise_id']!, _exerciseIdMeta),
      );
    } else if (isInserting) {
      context.missing(_exerciseIdMeta);
    }
    if (data.containsKey('client_id')) {
      context.handle(
        _clientIdMeta,
        clientId.isAcceptableOrUnknown(data['client_id']!, _clientIdMeta),
      );
    }
    if (data.containsKey('set_number')) {
      context.handle(
        _setNumberMeta,
        setNumber.isAcceptableOrUnknown(data['set_number']!, _setNumberMeta),
      );
    } else if (isInserting) {
      context.missing(_setNumberMeta);
    }
    if (data.containsKey('reps')) {
      context.handle(
        _repsMeta,
        reps.isAcceptableOrUnknown(data['reps']!, _repsMeta),
      );
    } else if (isInserting) {
      context.missing(_repsMeta);
    }
    if (data.containsKey('weight_kg')) {
      context.handle(
        _weightKgMeta,
        weightKg.isAcceptableOrUnknown(data['weight_kg']!, _weightKgMeta),
      );
    } else if (isInserting) {
      context.missing(_weightKgMeta);
    }
    if (data.containsKey('rpe')) {
      context.handle(
        _rpeMeta,
        rpe.isAcceptableOrUnknown(data['rpe']!, _rpeMeta),
      );
    }
    if (data.containsKey('rest_seconds')) {
      context.handle(
        _restSecondsMeta,
        restSeconds.isAcceptableOrUnknown(
          data['rest_seconds']!,
          _restSecondsMeta,
        ),
      );
    }
    if (data.containsKey('skipped')) {
      context.handle(
        _skippedMeta,
        skipped.isAcceptableOrUnknown(data['skipped']!, _skippedMeta),
      );
    }
    if (data.containsKey('logged_at')) {
      context.handle(
        _loggedAtMeta,
        loggedAt.isAcceptableOrUnknown(data['logged_at']!, _loggedAtMeta),
      );
    } else if (isInserting) {
      context.missing(_loggedAtMeta);
    }
    if (data.containsKey('sync_status')) {
      context.handle(
        _syncStatusMeta,
        syncStatus.isAcceptableOrUnknown(data['sync_status']!, _syncStatusMeta),
      );
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  LocalExerciseLog map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return LocalExerciseLog(
      id: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}id'],
      )!,
      workoutId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}workout_id'],
      )!,
      exerciseId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}exercise_id'],
      )!,
      clientId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}client_id'],
      ),
      setNumber: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}set_number'],
      )!,
      reps: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}reps'],
      )!,
      weightKg: attachedDatabase.typeMapping.read(
        DriftSqlType.double,
        data['${effectivePrefix}weight_kg'],
      )!,
      rpe: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}rpe'],
      ),
      restSeconds: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}rest_seconds'],
      ),
      skipped: attachedDatabase.typeMapping.read(
        DriftSqlType.bool,
        data['${effectivePrefix}skipped'],
      )!,
      loggedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}logged_at'],
      )!,
      syncStatus: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}sync_status'],
      )!,
    );
  }

  @override
  $LocalExerciseLogsTable createAlias(String alias) {
    return $LocalExerciseLogsTable(attachedDatabase, alias);
  }
}

class LocalExerciseLog extends DataClass
    implements Insertable<LocalExerciseLog> {
  final String id;
  final String workoutId;
  final String exerciseId;
  final String? clientId;
  final int setNumber;
  final int reps;
  final double weightKg;
  final int? rpe;
  final int? restSeconds;
  final bool skipped;
  final DateTime loggedAt;
  final String syncStatus;
  const LocalExerciseLog({
    required this.id,
    required this.workoutId,
    required this.exerciseId,
    this.clientId,
    required this.setNumber,
    required this.reps,
    required this.weightKg,
    this.rpe,
    this.restSeconds,
    required this.skipped,
    required this.loggedAt,
    required this.syncStatus,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    map['workout_id'] = Variable<String>(workoutId);
    map['exercise_id'] = Variable<String>(exerciseId);
    if (!nullToAbsent || clientId != null) {
      map['client_id'] = Variable<String>(clientId);
    }
    map['set_number'] = Variable<int>(setNumber);
    map['reps'] = Variable<int>(reps);
    map['weight_kg'] = Variable<double>(weightKg);
    if (!nullToAbsent || rpe != null) {
      map['rpe'] = Variable<int>(rpe);
    }
    if (!nullToAbsent || restSeconds != null) {
      map['rest_seconds'] = Variable<int>(restSeconds);
    }
    map['skipped'] = Variable<bool>(skipped);
    map['logged_at'] = Variable<DateTime>(loggedAt);
    map['sync_status'] = Variable<String>(syncStatus);
    return map;
  }

  LocalExerciseLogsCompanion toCompanion(bool nullToAbsent) {
    return LocalExerciseLogsCompanion(
      id: Value(id),
      workoutId: Value(workoutId),
      exerciseId: Value(exerciseId),
      clientId: clientId == null && nullToAbsent
          ? const Value.absent()
          : Value(clientId),
      setNumber: Value(setNumber),
      reps: Value(reps),
      weightKg: Value(weightKg),
      rpe: rpe == null && nullToAbsent ? const Value.absent() : Value(rpe),
      restSeconds: restSeconds == null && nullToAbsent
          ? const Value.absent()
          : Value(restSeconds),
      skipped: Value(skipped),
      loggedAt: Value(loggedAt),
      syncStatus: Value(syncStatus),
    );
  }

  factory LocalExerciseLog.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return LocalExerciseLog(
      id: serializer.fromJson<String>(json['id']),
      workoutId: serializer.fromJson<String>(json['workoutId']),
      exerciseId: serializer.fromJson<String>(json['exerciseId']),
      clientId: serializer.fromJson<String?>(json['clientId']),
      setNumber: serializer.fromJson<int>(json['setNumber']),
      reps: serializer.fromJson<int>(json['reps']),
      weightKg: serializer.fromJson<double>(json['weightKg']),
      rpe: serializer.fromJson<int?>(json['rpe']),
      restSeconds: serializer.fromJson<int?>(json['restSeconds']),
      skipped: serializer.fromJson<bool>(json['skipped']),
      loggedAt: serializer.fromJson<DateTime>(json['loggedAt']),
      syncStatus: serializer.fromJson<String>(json['syncStatus']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'workoutId': serializer.toJson<String>(workoutId),
      'exerciseId': serializer.toJson<String>(exerciseId),
      'clientId': serializer.toJson<String?>(clientId),
      'setNumber': serializer.toJson<int>(setNumber),
      'reps': serializer.toJson<int>(reps),
      'weightKg': serializer.toJson<double>(weightKg),
      'rpe': serializer.toJson<int?>(rpe),
      'restSeconds': serializer.toJson<int?>(restSeconds),
      'skipped': serializer.toJson<bool>(skipped),
      'loggedAt': serializer.toJson<DateTime>(loggedAt),
      'syncStatus': serializer.toJson<String>(syncStatus),
    };
  }

  LocalExerciseLog copyWith({
    String? id,
    String? workoutId,
    String? exerciseId,
    Value<String?> clientId = const Value.absent(),
    int? setNumber,
    int? reps,
    double? weightKg,
    Value<int?> rpe = const Value.absent(),
    Value<int?> restSeconds = const Value.absent(),
    bool? skipped,
    DateTime? loggedAt,
    String? syncStatus,
  }) => LocalExerciseLog(
    id: id ?? this.id,
    workoutId: workoutId ?? this.workoutId,
    exerciseId: exerciseId ?? this.exerciseId,
    clientId: clientId.present ? clientId.value : this.clientId,
    setNumber: setNumber ?? this.setNumber,
    reps: reps ?? this.reps,
    weightKg: weightKg ?? this.weightKg,
    rpe: rpe.present ? rpe.value : this.rpe,
    restSeconds: restSeconds.present ? restSeconds.value : this.restSeconds,
    skipped: skipped ?? this.skipped,
    loggedAt: loggedAt ?? this.loggedAt,
    syncStatus: syncStatus ?? this.syncStatus,
  );
  LocalExerciseLog copyWithCompanion(LocalExerciseLogsCompanion data) {
    return LocalExerciseLog(
      id: data.id.present ? data.id.value : this.id,
      workoutId: data.workoutId.present ? data.workoutId.value : this.workoutId,
      exerciseId: data.exerciseId.present
          ? data.exerciseId.value
          : this.exerciseId,
      clientId: data.clientId.present ? data.clientId.value : this.clientId,
      setNumber: data.setNumber.present ? data.setNumber.value : this.setNumber,
      reps: data.reps.present ? data.reps.value : this.reps,
      weightKg: data.weightKg.present ? data.weightKg.value : this.weightKg,
      rpe: data.rpe.present ? data.rpe.value : this.rpe,
      restSeconds: data.restSeconds.present
          ? data.restSeconds.value
          : this.restSeconds,
      skipped: data.skipped.present ? data.skipped.value : this.skipped,
      loggedAt: data.loggedAt.present ? data.loggedAt.value : this.loggedAt,
      syncStatus: data.syncStatus.present
          ? data.syncStatus.value
          : this.syncStatus,
    );
  }

  @override
  String toString() {
    return (StringBuffer('LocalExerciseLog(')
          ..write('id: $id, ')
          ..write('workoutId: $workoutId, ')
          ..write('exerciseId: $exerciseId, ')
          ..write('clientId: $clientId, ')
          ..write('setNumber: $setNumber, ')
          ..write('reps: $reps, ')
          ..write('weightKg: $weightKg, ')
          ..write('rpe: $rpe, ')
          ..write('restSeconds: $restSeconds, ')
          ..write('skipped: $skipped, ')
          ..write('loggedAt: $loggedAt, ')
          ..write('syncStatus: $syncStatus')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    id,
    workoutId,
    exerciseId,
    clientId,
    setNumber,
    reps,
    weightKg,
    rpe,
    restSeconds,
    skipped,
    loggedAt,
    syncStatus,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is LocalExerciseLog &&
          other.id == this.id &&
          other.workoutId == this.workoutId &&
          other.exerciseId == this.exerciseId &&
          other.clientId == this.clientId &&
          other.setNumber == this.setNumber &&
          other.reps == this.reps &&
          other.weightKg == this.weightKg &&
          other.rpe == this.rpe &&
          other.restSeconds == this.restSeconds &&
          other.skipped == this.skipped &&
          other.loggedAt == this.loggedAt &&
          other.syncStatus == this.syncStatus);
}

class LocalExerciseLogsCompanion extends UpdateCompanion<LocalExerciseLog> {
  final Value<String> id;
  final Value<String> workoutId;
  final Value<String> exerciseId;
  final Value<String?> clientId;
  final Value<int> setNumber;
  final Value<int> reps;
  final Value<double> weightKg;
  final Value<int?> rpe;
  final Value<int?> restSeconds;
  final Value<bool> skipped;
  final Value<DateTime> loggedAt;
  final Value<String> syncStatus;
  final Value<int> rowid;
  const LocalExerciseLogsCompanion({
    this.id = const Value.absent(),
    this.workoutId = const Value.absent(),
    this.exerciseId = const Value.absent(),
    this.clientId = const Value.absent(),
    this.setNumber = const Value.absent(),
    this.reps = const Value.absent(),
    this.weightKg = const Value.absent(),
    this.rpe = const Value.absent(),
    this.restSeconds = const Value.absent(),
    this.skipped = const Value.absent(),
    this.loggedAt = const Value.absent(),
    this.syncStatus = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  LocalExerciseLogsCompanion.insert({
    required String id,
    required String workoutId,
    required String exerciseId,
    this.clientId = const Value.absent(),
    required int setNumber,
    required int reps,
    required double weightKg,
    this.rpe = const Value.absent(),
    this.restSeconds = const Value.absent(),
    this.skipped = const Value.absent(),
    required DateTime loggedAt,
    this.syncStatus = const Value.absent(),
    this.rowid = const Value.absent(),
  }) : id = Value(id),
       workoutId = Value(workoutId),
       exerciseId = Value(exerciseId),
       setNumber = Value(setNumber),
       reps = Value(reps),
       weightKg = Value(weightKg),
       loggedAt = Value(loggedAt);
  static Insertable<LocalExerciseLog> custom({
    Expression<String>? id,
    Expression<String>? workoutId,
    Expression<String>? exerciseId,
    Expression<String>? clientId,
    Expression<int>? setNumber,
    Expression<int>? reps,
    Expression<double>? weightKg,
    Expression<int>? rpe,
    Expression<int>? restSeconds,
    Expression<bool>? skipped,
    Expression<DateTime>? loggedAt,
    Expression<String>? syncStatus,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (workoutId != null) 'workout_id': workoutId,
      if (exerciseId != null) 'exercise_id': exerciseId,
      if (clientId != null) 'client_id': clientId,
      if (setNumber != null) 'set_number': setNumber,
      if (reps != null) 'reps': reps,
      if (weightKg != null) 'weight_kg': weightKg,
      if (rpe != null) 'rpe': rpe,
      if (restSeconds != null) 'rest_seconds': restSeconds,
      if (skipped != null) 'skipped': skipped,
      if (loggedAt != null) 'logged_at': loggedAt,
      if (syncStatus != null) 'sync_status': syncStatus,
      if (rowid != null) 'rowid': rowid,
    });
  }

  LocalExerciseLogsCompanion copyWith({
    Value<String>? id,
    Value<String>? workoutId,
    Value<String>? exerciseId,
    Value<String?>? clientId,
    Value<int>? setNumber,
    Value<int>? reps,
    Value<double>? weightKg,
    Value<int?>? rpe,
    Value<int?>? restSeconds,
    Value<bool>? skipped,
    Value<DateTime>? loggedAt,
    Value<String>? syncStatus,
    Value<int>? rowid,
  }) {
    return LocalExerciseLogsCompanion(
      id: id ?? this.id,
      workoutId: workoutId ?? this.workoutId,
      exerciseId: exerciseId ?? this.exerciseId,
      clientId: clientId ?? this.clientId,
      setNumber: setNumber ?? this.setNumber,
      reps: reps ?? this.reps,
      weightKg: weightKg ?? this.weightKg,
      rpe: rpe ?? this.rpe,
      restSeconds: restSeconds ?? this.restSeconds,
      skipped: skipped ?? this.skipped,
      loggedAt: loggedAt ?? this.loggedAt,
      syncStatus: syncStatus ?? this.syncStatus,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<String>(id.value);
    }
    if (workoutId.present) {
      map['workout_id'] = Variable<String>(workoutId.value);
    }
    if (exerciseId.present) {
      map['exercise_id'] = Variable<String>(exerciseId.value);
    }
    if (clientId.present) {
      map['client_id'] = Variable<String>(clientId.value);
    }
    if (setNumber.present) {
      map['set_number'] = Variable<int>(setNumber.value);
    }
    if (reps.present) {
      map['reps'] = Variable<int>(reps.value);
    }
    if (weightKg.present) {
      map['weight_kg'] = Variable<double>(weightKg.value);
    }
    if (rpe.present) {
      map['rpe'] = Variable<int>(rpe.value);
    }
    if (restSeconds.present) {
      map['rest_seconds'] = Variable<int>(restSeconds.value);
    }
    if (skipped.present) {
      map['skipped'] = Variable<bool>(skipped.value);
    }
    if (loggedAt.present) {
      map['logged_at'] = Variable<DateTime>(loggedAt.value);
    }
    if (syncStatus.present) {
      map['sync_status'] = Variable<String>(syncStatus.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('LocalExerciseLogsCompanion(')
          ..write('id: $id, ')
          ..write('workoutId: $workoutId, ')
          ..write('exerciseId: $exerciseId, ')
          ..write('clientId: $clientId, ')
          ..write('setNumber: $setNumber, ')
          ..write('reps: $reps, ')
          ..write('weightKg: $weightKg, ')
          ..write('rpe: $rpe, ')
          ..write('restSeconds: $restSeconds, ')
          ..write('skipped: $skipped, ')
          ..write('loggedAt: $loggedAt, ')
          ..write('syncStatus: $syncStatus, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $LocalInBodyMeasurementsTable extends LocalInBodyMeasurements
    with TableInfo<$LocalInBodyMeasurementsTable, LocalInBodyMeasurement> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $LocalInBodyMeasurementsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
    'id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _userIdMeta = const VerificationMeta('userId');
  @override
  late final GeneratedColumn<String> userId = GeneratedColumn<String>(
    'user_id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _clientIdMeta = const VerificationMeta(
    'clientId',
  );
  @override
  late final GeneratedColumn<String> clientId = GeneratedColumn<String>(
    'client_id',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _measuredAtMeta = const VerificationMeta(
    'measuredAt',
  );
  @override
  late final GeneratedColumn<DateTime> measuredAt = GeneratedColumn<DateTime>(
    'measured_at',
    aliasedName,
    false,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _weightKgMeta = const VerificationMeta(
    'weightKg',
  );
  @override
  late final GeneratedColumn<double> weightKg = GeneratedColumn<double>(
    'weight_kg',
    aliasedName,
    false,
    type: DriftSqlType.double,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _heightCmMeta = const VerificationMeta(
    'heightCm',
  );
  @override
  late final GeneratedColumn<double> heightCm = GeneratedColumn<double>(
    'height_cm',
    aliasedName,
    false,
    type: DriftSqlType.double,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _sexMeta = const VerificationMeta('sex');
  @override
  late final GeneratedColumn<String> sex = GeneratedColumn<String>(
    'sex',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _bodyFatPercentMeta = const VerificationMeta(
    'bodyFatPercent',
  );
  @override
  late final GeneratedColumn<double> bodyFatPercent = GeneratedColumn<double>(
    'body_fat_percent',
    aliasedName,
    false,
    type: DriftSqlType.double,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _muscleMassKgMeta = const VerificationMeta(
    'muscleMassKg',
  );
  @override
  late final GeneratedColumn<double> muscleMassKg = GeneratedColumn<double>(
    'muscle_mass_kg',
    aliasedName,
    true,
    type: DriftSqlType.double,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _bodyWaterPercentMeta = const VerificationMeta(
    'bodyWaterPercent',
  );
  @override
  late final GeneratedColumn<double> bodyWaterPercent = GeneratedColumn<double>(
    'body_water_percent',
    aliasedName,
    true,
    type: DriftSqlType.double,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _proteinKgMeta = const VerificationMeta(
    'proteinKg',
  );
  @override
  late final GeneratedColumn<double> proteinKg = GeneratedColumn<double>(
    'protein_kg',
    aliasedName,
    true,
    type: DriftSqlType.double,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _mineralsKgMeta = const VerificationMeta(
    'mineralsKg',
  );
  @override
  late final GeneratedColumn<double> mineralsKg = GeneratedColumn<double>(
    'minerals_kg',
    aliasedName,
    true,
    type: DriftSqlType.double,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _visceralFatLevelMeta = const VerificationMeta(
    'visceralFatLevel',
  );
  @override
  late final GeneratedColumn<int> visceralFatLevel = GeneratedColumn<int>(
    'visceral_fat_level',
    aliasedName,
    true,
    type: DriftSqlType.int,
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
  static const VerificationMeta _fatFreeMassKgMeta = const VerificationMeta(
    'fatFreeMassKg',
  );
  @override
  late final GeneratedColumn<double> fatFreeMassKg = GeneratedColumn<double>(
    'fat_free_mass_kg',
    aliasedName,
    true,
    type: DriftSqlType.double,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _bmiMeta = const VerificationMeta('bmi');
  @override
  late final GeneratedColumn<double> bmi = GeneratedColumn<double>(
    'bmi',
    aliasedName,
    false,
    type: DriftSqlType.double,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _sourceMeta = const VerificationMeta('source');
  @override
  late final GeneratedColumn<String> source = GeneratedColumn<String>(
    'source',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _originalPdfKeyMeta = const VerificationMeta(
    'originalPdfKey',
  );
  @override
  late final GeneratedColumn<String> originalPdfKey = GeneratedColumn<String>(
    'original_pdf_key',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _syncStatusMeta = const VerificationMeta(
    'syncStatus',
  );
  @override
  late final GeneratedColumn<String> syncStatus = GeneratedColumn<String>(
    'sync_status',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant('synced'),
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
    requiredDuringInsert: true,
  );
  @override
  List<GeneratedColumn> get $columns => [
    id,
    userId,
    clientId,
    measuredAt,
    weightKg,
    heightCm,
    sex,
    bodyFatPercent,
    muscleMassKg,
    bodyWaterPercent,
    proteinKg,
    mineralsKg,
    visceralFatLevel,
    bmrKcal,
    fatFreeMassKg,
    bmi,
    source,
    originalPdfKey,
    syncStatus,
    createdAt,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'inbody_measurements';
  @override
  VerificationContext validateIntegrity(
    Insertable<LocalInBodyMeasurement> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    } else if (isInserting) {
      context.missing(_idMeta);
    }
    if (data.containsKey('user_id')) {
      context.handle(
        _userIdMeta,
        userId.isAcceptableOrUnknown(data['user_id']!, _userIdMeta),
      );
    } else if (isInserting) {
      context.missing(_userIdMeta);
    }
    if (data.containsKey('client_id')) {
      context.handle(
        _clientIdMeta,
        clientId.isAcceptableOrUnknown(data['client_id']!, _clientIdMeta),
      );
    }
    if (data.containsKey('measured_at')) {
      context.handle(
        _measuredAtMeta,
        measuredAt.isAcceptableOrUnknown(data['measured_at']!, _measuredAtMeta),
      );
    } else if (isInserting) {
      context.missing(_measuredAtMeta);
    }
    if (data.containsKey('weight_kg')) {
      context.handle(
        _weightKgMeta,
        weightKg.isAcceptableOrUnknown(data['weight_kg']!, _weightKgMeta),
      );
    } else if (isInserting) {
      context.missing(_weightKgMeta);
    }
    if (data.containsKey('height_cm')) {
      context.handle(
        _heightCmMeta,
        heightCm.isAcceptableOrUnknown(data['height_cm']!, _heightCmMeta),
      );
    } else if (isInserting) {
      context.missing(_heightCmMeta);
    }
    if (data.containsKey('sex')) {
      context.handle(
        _sexMeta,
        sex.isAcceptableOrUnknown(data['sex']!, _sexMeta),
      );
    } else if (isInserting) {
      context.missing(_sexMeta);
    }
    if (data.containsKey('body_fat_percent')) {
      context.handle(
        _bodyFatPercentMeta,
        bodyFatPercent.isAcceptableOrUnknown(
          data['body_fat_percent']!,
          _bodyFatPercentMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_bodyFatPercentMeta);
    }
    if (data.containsKey('muscle_mass_kg')) {
      context.handle(
        _muscleMassKgMeta,
        muscleMassKg.isAcceptableOrUnknown(
          data['muscle_mass_kg']!,
          _muscleMassKgMeta,
        ),
      );
    }
    if (data.containsKey('body_water_percent')) {
      context.handle(
        _bodyWaterPercentMeta,
        bodyWaterPercent.isAcceptableOrUnknown(
          data['body_water_percent']!,
          _bodyWaterPercentMeta,
        ),
      );
    }
    if (data.containsKey('protein_kg')) {
      context.handle(
        _proteinKgMeta,
        proteinKg.isAcceptableOrUnknown(data['protein_kg']!, _proteinKgMeta),
      );
    }
    if (data.containsKey('minerals_kg')) {
      context.handle(
        _mineralsKgMeta,
        mineralsKg.isAcceptableOrUnknown(data['minerals_kg']!, _mineralsKgMeta),
      );
    }
    if (data.containsKey('visceral_fat_level')) {
      context.handle(
        _visceralFatLevelMeta,
        visceralFatLevel.isAcceptableOrUnknown(
          data['visceral_fat_level']!,
          _visceralFatLevelMeta,
        ),
      );
    }
    if (data.containsKey('bmr_kcal')) {
      context.handle(
        _bmrKcalMeta,
        bmrKcal.isAcceptableOrUnknown(data['bmr_kcal']!, _bmrKcalMeta),
      );
    }
    if (data.containsKey('fat_free_mass_kg')) {
      context.handle(
        _fatFreeMassKgMeta,
        fatFreeMassKg.isAcceptableOrUnknown(
          data['fat_free_mass_kg']!,
          _fatFreeMassKgMeta,
        ),
      );
    }
    if (data.containsKey('bmi')) {
      context.handle(
        _bmiMeta,
        bmi.isAcceptableOrUnknown(data['bmi']!, _bmiMeta),
      );
    } else if (isInserting) {
      context.missing(_bmiMeta);
    }
    if (data.containsKey('source')) {
      context.handle(
        _sourceMeta,
        source.isAcceptableOrUnknown(data['source']!, _sourceMeta),
      );
    } else if (isInserting) {
      context.missing(_sourceMeta);
    }
    if (data.containsKey('original_pdf_key')) {
      context.handle(
        _originalPdfKeyMeta,
        originalPdfKey.isAcceptableOrUnknown(
          data['original_pdf_key']!,
          _originalPdfKeyMeta,
        ),
      );
    }
    if (data.containsKey('sync_status')) {
      context.handle(
        _syncStatusMeta,
        syncStatus.isAcceptableOrUnknown(data['sync_status']!, _syncStatusMeta),
      );
    }
    if (data.containsKey('created_at')) {
      context.handle(
        _createdAtMeta,
        createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta),
      );
    } else if (isInserting) {
      context.missing(_createdAtMeta);
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  LocalInBodyMeasurement map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return LocalInBodyMeasurement(
      id: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}id'],
      )!,
      userId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}user_id'],
      )!,
      clientId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}client_id'],
      ),
      measuredAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}measured_at'],
      )!,
      weightKg: attachedDatabase.typeMapping.read(
        DriftSqlType.double,
        data['${effectivePrefix}weight_kg'],
      )!,
      heightCm: attachedDatabase.typeMapping.read(
        DriftSqlType.double,
        data['${effectivePrefix}height_cm'],
      )!,
      sex: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}sex'],
      )!,
      bodyFatPercent: attachedDatabase.typeMapping.read(
        DriftSqlType.double,
        data['${effectivePrefix}body_fat_percent'],
      )!,
      muscleMassKg: attachedDatabase.typeMapping.read(
        DriftSqlType.double,
        data['${effectivePrefix}muscle_mass_kg'],
      ),
      bodyWaterPercent: attachedDatabase.typeMapping.read(
        DriftSqlType.double,
        data['${effectivePrefix}body_water_percent'],
      ),
      proteinKg: attachedDatabase.typeMapping.read(
        DriftSqlType.double,
        data['${effectivePrefix}protein_kg'],
      ),
      mineralsKg: attachedDatabase.typeMapping.read(
        DriftSqlType.double,
        data['${effectivePrefix}minerals_kg'],
      ),
      visceralFatLevel: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}visceral_fat_level'],
      ),
      bmrKcal: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}bmr_kcal'],
      ),
      fatFreeMassKg: attachedDatabase.typeMapping.read(
        DriftSqlType.double,
        data['${effectivePrefix}fat_free_mass_kg'],
      ),
      bmi: attachedDatabase.typeMapping.read(
        DriftSqlType.double,
        data['${effectivePrefix}bmi'],
      )!,
      source: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}source'],
      )!,
      originalPdfKey: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}original_pdf_key'],
      ),
      syncStatus: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}sync_status'],
      )!,
      createdAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}created_at'],
      )!,
    );
  }

  @override
  $LocalInBodyMeasurementsTable createAlias(String alias) {
    return $LocalInBodyMeasurementsTable(attachedDatabase, alias);
  }
}

class LocalInBodyMeasurement extends DataClass
    implements Insertable<LocalInBodyMeasurement> {
  final String id;
  final String userId;
  final String? clientId;
  final DateTime measuredAt;
  final double weightKg;
  final double heightCm;
  final String sex;
  final double bodyFatPercent;
  final double? muscleMassKg;
  final double? bodyWaterPercent;
  final double? proteinKg;
  final double? mineralsKg;
  final int? visceralFatLevel;
  final int? bmrKcal;
  final double? fatFreeMassKg;
  final double bmi;
  final String source;
  final String? originalPdfKey;
  final String syncStatus;
  final DateTime createdAt;
  const LocalInBodyMeasurement({
    required this.id,
    required this.userId,
    this.clientId,
    required this.measuredAt,
    required this.weightKg,
    required this.heightCm,
    required this.sex,
    required this.bodyFatPercent,
    this.muscleMassKg,
    this.bodyWaterPercent,
    this.proteinKg,
    this.mineralsKg,
    this.visceralFatLevel,
    this.bmrKcal,
    this.fatFreeMassKg,
    required this.bmi,
    required this.source,
    this.originalPdfKey,
    required this.syncStatus,
    required this.createdAt,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    map['user_id'] = Variable<String>(userId);
    if (!nullToAbsent || clientId != null) {
      map['client_id'] = Variable<String>(clientId);
    }
    map['measured_at'] = Variable<DateTime>(measuredAt);
    map['weight_kg'] = Variable<double>(weightKg);
    map['height_cm'] = Variable<double>(heightCm);
    map['sex'] = Variable<String>(sex);
    map['body_fat_percent'] = Variable<double>(bodyFatPercent);
    if (!nullToAbsent || muscleMassKg != null) {
      map['muscle_mass_kg'] = Variable<double>(muscleMassKg);
    }
    if (!nullToAbsent || bodyWaterPercent != null) {
      map['body_water_percent'] = Variable<double>(bodyWaterPercent);
    }
    if (!nullToAbsent || proteinKg != null) {
      map['protein_kg'] = Variable<double>(proteinKg);
    }
    if (!nullToAbsent || mineralsKg != null) {
      map['minerals_kg'] = Variable<double>(mineralsKg);
    }
    if (!nullToAbsent || visceralFatLevel != null) {
      map['visceral_fat_level'] = Variable<int>(visceralFatLevel);
    }
    if (!nullToAbsent || bmrKcal != null) {
      map['bmr_kcal'] = Variable<int>(bmrKcal);
    }
    if (!nullToAbsent || fatFreeMassKg != null) {
      map['fat_free_mass_kg'] = Variable<double>(fatFreeMassKg);
    }
    map['bmi'] = Variable<double>(bmi);
    map['source'] = Variable<String>(source);
    if (!nullToAbsent || originalPdfKey != null) {
      map['original_pdf_key'] = Variable<String>(originalPdfKey);
    }
    map['sync_status'] = Variable<String>(syncStatus);
    map['created_at'] = Variable<DateTime>(createdAt);
    return map;
  }

  LocalInBodyMeasurementsCompanion toCompanion(bool nullToAbsent) {
    return LocalInBodyMeasurementsCompanion(
      id: Value(id),
      userId: Value(userId),
      clientId: clientId == null && nullToAbsent
          ? const Value.absent()
          : Value(clientId),
      measuredAt: Value(measuredAt),
      weightKg: Value(weightKg),
      heightCm: Value(heightCm),
      sex: Value(sex),
      bodyFatPercent: Value(bodyFatPercent),
      muscleMassKg: muscleMassKg == null && nullToAbsent
          ? const Value.absent()
          : Value(muscleMassKg),
      bodyWaterPercent: bodyWaterPercent == null && nullToAbsent
          ? const Value.absent()
          : Value(bodyWaterPercent),
      proteinKg: proteinKg == null && nullToAbsent
          ? const Value.absent()
          : Value(proteinKg),
      mineralsKg: mineralsKg == null && nullToAbsent
          ? const Value.absent()
          : Value(mineralsKg),
      visceralFatLevel: visceralFatLevel == null && nullToAbsent
          ? const Value.absent()
          : Value(visceralFatLevel),
      bmrKcal: bmrKcal == null && nullToAbsent
          ? const Value.absent()
          : Value(bmrKcal),
      fatFreeMassKg: fatFreeMassKg == null && nullToAbsent
          ? const Value.absent()
          : Value(fatFreeMassKg),
      bmi: Value(bmi),
      source: Value(source),
      originalPdfKey: originalPdfKey == null && nullToAbsent
          ? const Value.absent()
          : Value(originalPdfKey),
      syncStatus: Value(syncStatus),
      createdAt: Value(createdAt),
    );
  }

  factory LocalInBodyMeasurement.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return LocalInBodyMeasurement(
      id: serializer.fromJson<String>(json['id']),
      userId: serializer.fromJson<String>(json['userId']),
      clientId: serializer.fromJson<String?>(json['clientId']),
      measuredAt: serializer.fromJson<DateTime>(json['measuredAt']),
      weightKg: serializer.fromJson<double>(json['weightKg']),
      heightCm: serializer.fromJson<double>(json['heightCm']),
      sex: serializer.fromJson<String>(json['sex']),
      bodyFatPercent: serializer.fromJson<double>(json['bodyFatPercent']),
      muscleMassKg: serializer.fromJson<double?>(json['muscleMassKg']),
      bodyWaterPercent: serializer.fromJson<double?>(json['bodyWaterPercent']),
      proteinKg: serializer.fromJson<double?>(json['proteinKg']),
      mineralsKg: serializer.fromJson<double?>(json['mineralsKg']),
      visceralFatLevel: serializer.fromJson<int?>(json['visceralFatLevel']),
      bmrKcal: serializer.fromJson<int?>(json['bmrKcal']),
      fatFreeMassKg: serializer.fromJson<double?>(json['fatFreeMassKg']),
      bmi: serializer.fromJson<double>(json['bmi']),
      source: serializer.fromJson<String>(json['source']),
      originalPdfKey: serializer.fromJson<String?>(json['originalPdfKey']),
      syncStatus: serializer.fromJson<String>(json['syncStatus']),
      createdAt: serializer.fromJson<DateTime>(json['createdAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'userId': serializer.toJson<String>(userId),
      'clientId': serializer.toJson<String?>(clientId),
      'measuredAt': serializer.toJson<DateTime>(measuredAt),
      'weightKg': serializer.toJson<double>(weightKg),
      'heightCm': serializer.toJson<double>(heightCm),
      'sex': serializer.toJson<String>(sex),
      'bodyFatPercent': serializer.toJson<double>(bodyFatPercent),
      'muscleMassKg': serializer.toJson<double?>(muscleMassKg),
      'bodyWaterPercent': serializer.toJson<double?>(bodyWaterPercent),
      'proteinKg': serializer.toJson<double?>(proteinKg),
      'mineralsKg': serializer.toJson<double?>(mineralsKg),
      'visceralFatLevel': serializer.toJson<int?>(visceralFatLevel),
      'bmrKcal': serializer.toJson<int?>(bmrKcal),
      'fatFreeMassKg': serializer.toJson<double?>(fatFreeMassKg),
      'bmi': serializer.toJson<double>(bmi),
      'source': serializer.toJson<String>(source),
      'originalPdfKey': serializer.toJson<String?>(originalPdfKey),
      'syncStatus': serializer.toJson<String>(syncStatus),
      'createdAt': serializer.toJson<DateTime>(createdAt),
    };
  }

  LocalInBodyMeasurement copyWith({
    String? id,
    String? userId,
    Value<String?> clientId = const Value.absent(),
    DateTime? measuredAt,
    double? weightKg,
    double? heightCm,
    String? sex,
    double? bodyFatPercent,
    Value<double?> muscleMassKg = const Value.absent(),
    Value<double?> bodyWaterPercent = const Value.absent(),
    Value<double?> proteinKg = const Value.absent(),
    Value<double?> mineralsKg = const Value.absent(),
    Value<int?> visceralFatLevel = const Value.absent(),
    Value<int?> bmrKcal = const Value.absent(),
    Value<double?> fatFreeMassKg = const Value.absent(),
    double? bmi,
    String? source,
    Value<String?> originalPdfKey = const Value.absent(),
    String? syncStatus,
    DateTime? createdAt,
  }) => LocalInBodyMeasurement(
    id: id ?? this.id,
    userId: userId ?? this.userId,
    clientId: clientId.present ? clientId.value : this.clientId,
    measuredAt: measuredAt ?? this.measuredAt,
    weightKg: weightKg ?? this.weightKg,
    heightCm: heightCm ?? this.heightCm,
    sex: sex ?? this.sex,
    bodyFatPercent: bodyFatPercent ?? this.bodyFatPercent,
    muscleMassKg: muscleMassKg.present ? muscleMassKg.value : this.muscleMassKg,
    bodyWaterPercent: bodyWaterPercent.present
        ? bodyWaterPercent.value
        : this.bodyWaterPercent,
    proteinKg: proteinKg.present ? proteinKg.value : this.proteinKg,
    mineralsKg: mineralsKg.present ? mineralsKg.value : this.mineralsKg,
    visceralFatLevel: visceralFatLevel.present
        ? visceralFatLevel.value
        : this.visceralFatLevel,
    bmrKcal: bmrKcal.present ? bmrKcal.value : this.bmrKcal,
    fatFreeMassKg: fatFreeMassKg.present
        ? fatFreeMassKg.value
        : this.fatFreeMassKg,
    bmi: bmi ?? this.bmi,
    source: source ?? this.source,
    originalPdfKey: originalPdfKey.present
        ? originalPdfKey.value
        : this.originalPdfKey,
    syncStatus: syncStatus ?? this.syncStatus,
    createdAt: createdAt ?? this.createdAt,
  );
  LocalInBodyMeasurement copyWithCompanion(
    LocalInBodyMeasurementsCompanion data,
  ) {
    return LocalInBodyMeasurement(
      id: data.id.present ? data.id.value : this.id,
      userId: data.userId.present ? data.userId.value : this.userId,
      clientId: data.clientId.present ? data.clientId.value : this.clientId,
      measuredAt: data.measuredAt.present
          ? data.measuredAt.value
          : this.measuredAt,
      weightKg: data.weightKg.present ? data.weightKg.value : this.weightKg,
      heightCm: data.heightCm.present ? data.heightCm.value : this.heightCm,
      sex: data.sex.present ? data.sex.value : this.sex,
      bodyFatPercent: data.bodyFatPercent.present
          ? data.bodyFatPercent.value
          : this.bodyFatPercent,
      muscleMassKg: data.muscleMassKg.present
          ? data.muscleMassKg.value
          : this.muscleMassKg,
      bodyWaterPercent: data.bodyWaterPercent.present
          ? data.bodyWaterPercent.value
          : this.bodyWaterPercent,
      proteinKg: data.proteinKg.present ? data.proteinKg.value : this.proteinKg,
      mineralsKg: data.mineralsKg.present
          ? data.mineralsKg.value
          : this.mineralsKg,
      visceralFatLevel: data.visceralFatLevel.present
          ? data.visceralFatLevel.value
          : this.visceralFatLevel,
      bmrKcal: data.bmrKcal.present ? data.bmrKcal.value : this.bmrKcal,
      fatFreeMassKg: data.fatFreeMassKg.present
          ? data.fatFreeMassKg.value
          : this.fatFreeMassKg,
      bmi: data.bmi.present ? data.bmi.value : this.bmi,
      source: data.source.present ? data.source.value : this.source,
      originalPdfKey: data.originalPdfKey.present
          ? data.originalPdfKey.value
          : this.originalPdfKey,
      syncStatus: data.syncStatus.present
          ? data.syncStatus.value
          : this.syncStatus,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('LocalInBodyMeasurement(')
          ..write('id: $id, ')
          ..write('userId: $userId, ')
          ..write('clientId: $clientId, ')
          ..write('measuredAt: $measuredAt, ')
          ..write('weightKg: $weightKg, ')
          ..write('heightCm: $heightCm, ')
          ..write('sex: $sex, ')
          ..write('bodyFatPercent: $bodyFatPercent, ')
          ..write('muscleMassKg: $muscleMassKg, ')
          ..write('bodyWaterPercent: $bodyWaterPercent, ')
          ..write('proteinKg: $proteinKg, ')
          ..write('mineralsKg: $mineralsKg, ')
          ..write('visceralFatLevel: $visceralFatLevel, ')
          ..write('bmrKcal: $bmrKcal, ')
          ..write('fatFreeMassKg: $fatFreeMassKg, ')
          ..write('bmi: $bmi, ')
          ..write('source: $source, ')
          ..write('originalPdfKey: $originalPdfKey, ')
          ..write('syncStatus: $syncStatus, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    id,
    userId,
    clientId,
    measuredAt,
    weightKg,
    heightCm,
    sex,
    bodyFatPercent,
    muscleMassKg,
    bodyWaterPercent,
    proteinKg,
    mineralsKg,
    visceralFatLevel,
    bmrKcal,
    fatFreeMassKg,
    bmi,
    source,
    originalPdfKey,
    syncStatus,
    createdAt,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is LocalInBodyMeasurement &&
          other.id == this.id &&
          other.userId == this.userId &&
          other.clientId == this.clientId &&
          other.measuredAt == this.measuredAt &&
          other.weightKg == this.weightKg &&
          other.heightCm == this.heightCm &&
          other.sex == this.sex &&
          other.bodyFatPercent == this.bodyFatPercent &&
          other.muscleMassKg == this.muscleMassKg &&
          other.bodyWaterPercent == this.bodyWaterPercent &&
          other.proteinKg == this.proteinKg &&
          other.mineralsKg == this.mineralsKg &&
          other.visceralFatLevel == this.visceralFatLevel &&
          other.bmrKcal == this.bmrKcal &&
          other.fatFreeMassKg == this.fatFreeMassKg &&
          other.bmi == this.bmi &&
          other.source == this.source &&
          other.originalPdfKey == this.originalPdfKey &&
          other.syncStatus == this.syncStatus &&
          other.createdAt == this.createdAt);
}

class LocalInBodyMeasurementsCompanion
    extends UpdateCompanion<LocalInBodyMeasurement> {
  final Value<String> id;
  final Value<String> userId;
  final Value<String?> clientId;
  final Value<DateTime> measuredAt;
  final Value<double> weightKg;
  final Value<double> heightCm;
  final Value<String> sex;
  final Value<double> bodyFatPercent;
  final Value<double?> muscleMassKg;
  final Value<double?> bodyWaterPercent;
  final Value<double?> proteinKg;
  final Value<double?> mineralsKg;
  final Value<int?> visceralFatLevel;
  final Value<int?> bmrKcal;
  final Value<double?> fatFreeMassKg;
  final Value<double> bmi;
  final Value<String> source;
  final Value<String?> originalPdfKey;
  final Value<String> syncStatus;
  final Value<DateTime> createdAt;
  final Value<int> rowid;
  const LocalInBodyMeasurementsCompanion({
    this.id = const Value.absent(),
    this.userId = const Value.absent(),
    this.clientId = const Value.absent(),
    this.measuredAt = const Value.absent(),
    this.weightKg = const Value.absent(),
    this.heightCm = const Value.absent(),
    this.sex = const Value.absent(),
    this.bodyFatPercent = const Value.absent(),
    this.muscleMassKg = const Value.absent(),
    this.bodyWaterPercent = const Value.absent(),
    this.proteinKg = const Value.absent(),
    this.mineralsKg = const Value.absent(),
    this.visceralFatLevel = const Value.absent(),
    this.bmrKcal = const Value.absent(),
    this.fatFreeMassKg = const Value.absent(),
    this.bmi = const Value.absent(),
    this.source = const Value.absent(),
    this.originalPdfKey = const Value.absent(),
    this.syncStatus = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  LocalInBodyMeasurementsCompanion.insert({
    required String id,
    required String userId,
    this.clientId = const Value.absent(),
    required DateTime measuredAt,
    required double weightKg,
    required double heightCm,
    required String sex,
    required double bodyFatPercent,
    this.muscleMassKg = const Value.absent(),
    this.bodyWaterPercent = const Value.absent(),
    this.proteinKg = const Value.absent(),
    this.mineralsKg = const Value.absent(),
    this.visceralFatLevel = const Value.absent(),
    this.bmrKcal = const Value.absent(),
    this.fatFreeMassKg = const Value.absent(),
    required double bmi,
    required String source,
    this.originalPdfKey = const Value.absent(),
    this.syncStatus = const Value.absent(),
    required DateTime createdAt,
    this.rowid = const Value.absent(),
  }) : id = Value(id),
       userId = Value(userId),
       measuredAt = Value(measuredAt),
       weightKg = Value(weightKg),
       heightCm = Value(heightCm),
       sex = Value(sex),
       bodyFatPercent = Value(bodyFatPercent),
       bmi = Value(bmi),
       source = Value(source),
       createdAt = Value(createdAt);
  static Insertable<LocalInBodyMeasurement> custom({
    Expression<String>? id,
    Expression<String>? userId,
    Expression<String>? clientId,
    Expression<DateTime>? measuredAt,
    Expression<double>? weightKg,
    Expression<double>? heightCm,
    Expression<String>? sex,
    Expression<double>? bodyFatPercent,
    Expression<double>? muscleMassKg,
    Expression<double>? bodyWaterPercent,
    Expression<double>? proteinKg,
    Expression<double>? mineralsKg,
    Expression<int>? visceralFatLevel,
    Expression<int>? bmrKcal,
    Expression<double>? fatFreeMassKg,
    Expression<double>? bmi,
    Expression<String>? source,
    Expression<String>? originalPdfKey,
    Expression<String>? syncStatus,
    Expression<DateTime>? createdAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (userId != null) 'user_id': userId,
      if (clientId != null) 'client_id': clientId,
      if (measuredAt != null) 'measured_at': measuredAt,
      if (weightKg != null) 'weight_kg': weightKg,
      if (heightCm != null) 'height_cm': heightCm,
      if (sex != null) 'sex': sex,
      if (bodyFatPercent != null) 'body_fat_percent': bodyFatPercent,
      if (muscleMassKg != null) 'muscle_mass_kg': muscleMassKg,
      if (bodyWaterPercent != null) 'body_water_percent': bodyWaterPercent,
      if (proteinKg != null) 'protein_kg': proteinKg,
      if (mineralsKg != null) 'minerals_kg': mineralsKg,
      if (visceralFatLevel != null) 'visceral_fat_level': visceralFatLevel,
      if (bmrKcal != null) 'bmr_kcal': bmrKcal,
      if (fatFreeMassKg != null) 'fat_free_mass_kg': fatFreeMassKg,
      if (bmi != null) 'bmi': bmi,
      if (source != null) 'source': source,
      if (originalPdfKey != null) 'original_pdf_key': originalPdfKey,
      if (syncStatus != null) 'sync_status': syncStatus,
      if (createdAt != null) 'created_at': createdAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  LocalInBodyMeasurementsCompanion copyWith({
    Value<String>? id,
    Value<String>? userId,
    Value<String?>? clientId,
    Value<DateTime>? measuredAt,
    Value<double>? weightKg,
    Value<double>? heightCm,
    Value<String>? sex,
    Value<double>? bodyFatPercent,
    Value<double?>? muscleMassKg,
    Value<double?>? bodyWaterPercent,
    Value<double?>? proteinKg,
    Value<double?>? mineralsKg,
    Value<int?>? visceralFatLevel,
    Value<int?>? bmrKcal,
    Value<double?>? fatFreeMassKg,
    Value<double>? bmi,
    Value<String>? source,
    Value<String?>? originalPdfKey,
    Value<String>? syncStatus,
    Value<DateTime>? createdAt,
    Value<int>? rowid,
  }) {
    return LocalInBodyMeasurementsCompanion(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      clientId: clientId ?? this.clientId,
      measuredAt: measuredAt ?? this.measuredAt,
      weightKg: weightKg ?? this.weightKg,
      heightCm: heightCm ?? this.heightCm,
      sex: sex ?? this.sex,
      bodyFatPercent: bodyFatPercent ?? this.bodyFatPercent,
      muscleMassKg: muscleMassKg ?? this.muscleMassKg,
      bodyWaterPercent: bodyWaterPercent ?? this.bodyWaterPercent,
      proteinKg: proteinKg ?? this.proteinKg,
      mineralsKg: mineralsKg ?? this.mineralsKg,
      visceralFatLevel: visceralFatLevel ?? this.visceralFatLevel,
      bmrKcal: bmrKcal ?? this.bmrKcal,
      fatFreeMassKg: fatFreeMassKg ?? this.fatFreeMassKg,
      bmi: bmi ?? this.bmi,
      source: source ?? this.source,
      originalPdfKey: originalPdfKey ?? this.originalPdfKey,
      syncStatus: syncStatus ?? this.syncStatus,
      createdAt: createdAt ?? this.createdAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<String>(id.value);
    }
    if (userId.present) {
      map['user_id'] = Variable<String>(userId.value);
    }
    if (clientId.present) {
      map['client_id'] = Variable<String>(clientId.value);
    }
    if (measuredAt.present) {
      map['measured_at'] = Variable<DateTime>(measuredAt.value);
    }
    if (weightKg.present) {
      map['weight_kg'] = Variable<double>(weightKg.value);
    }
    if (heightCm.present) {
      map['height_cm'] = Variable<double>(heightCm.value);
    }
    if (sex.present) {
      map['sex'] = Variable<String>(sex.value);
    }
    if (bodyFatPercent.present) {
      map['body_fat_percent'] = Variable<double>(bodyFatPercent.value);
    }
    if (muscleMassKg.present) {
      map['muscle_mass_kg'] = Variable<double>(muscleMassKg.value);
    }
    if (bodyWaterPercent.present) {
      map['body_water_percent'] = Variable<double>(bodyWaterPercent.value);
    }
    if (proteinKg.present) {
      map['protein_kg'] = Variable<double>(proteinKg.value);
    }
    if (mineralsKg.present) {
      map['minerals_kg'] = Variable<double>(mineralsKg.value);
    }
    if (visceralFatLevel.present) {
      map['visceral_fat_level'] = Variable<int>(visceralFatLevel.value);
    }
    if (bmrKcal.present) {
      map['bmr_kcal'] = Variable<int>(bmrKcal.value);
    }
    if (fatFreeMassKg.present) {
      map['fat_free_mass_kg'] = Variable<double>(fatFreeMassKg.value);
    }
    if (bmi.present) {
      map['bmi'] = Variable<double>(bmi.value);
    }
    if (source.present) {
      map['source'] = Variable<String>(source.value);
    }
    if (originalPdfKey.present) {
      map['original_pdf_key'] = Variable<String>(originalPdfKey.value);
    }
    if (syncStatus.present) {
      map['sync_status'] = Variable<String>(syncStatus.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('LocalInBodyMeasurementsCompanion(')
          ..write('id: $id, ')
          ..write('userId: $userId, ')
          ..write('clientId: $clientId, ')
          ..write('measuredAt: $measuredAt, ')
          ..write('weightKg: $weightKg, ')
          ..write('heightCm: $heightCm, ')
          ..write('sex: $sex, ')
          ..write('bodyFatPercent: $bodyFatPercent, ')
          ..write('muscleMassKg: $muscleMassKg, ')
          ..write('bodyWaterPercent: $bodyWaterPercent, ')
          ..write('proteinKg: $proteinKg, ')
          ..write('mineralsKg: $mineralsKg, ')
          ..write('visceralFatLevel: $visceralFatLevel, ')
          ..write('bmrKcal: $bmrKcal, ')
          ..write('fatFreeMassKg: $fatFreeMassKg, ')
          ..write('bmi: $bmi, ')
          ..write('source: $source, ')
          ..write('originalPdfKey: $originalPdfKey, ')
          ..write('syncStatus: $syncStatus, ')
          ..write('createdAt: $createdAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $LocalPlansTable extends LocalPlans
    with TableInfo<$LocalPlansTable, LocalPlan> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $LocalPlansTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
    'id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _userIdMeta = const VerificationMeta('userId');
  @override
  late final GeneratedColumn<String> userId = GeneratedColumn<String>(
    'user_id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _statusMeta = const VerificationMeta('status');
  @override
  late final GeneratedColumn<String> status = GeneratedColumn<String>(
    'status',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _goalMeta = const VerificationMeta('goal');
  @override
  late final GeneratedColumn<String> goal = GeneratedColumn<String>(
    'goal',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
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
  static const VerificationMeta _validFromMeta = const VerificationMeta(
    'validFrom',
  );
  @override
  late final GeneratedColumn<DateTime> validFrom = GeneratedColumn<DateTime>(
    'valid_from',
    aliasedName,
    false,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _validUntilMeta = const VerificationMeta(
    'validUntil',
  );
  @override
  late final GeneratedColumn<DateTime> validUntil = GeneratedColumn<DateTime>(
    'valid_until',
    aliasedName,
    false,
    type: DriftSqlType.dateTime,
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
  static const VerificationMeta _fetchedAtMeta = const VerificationMeta(
    'fetchedAt',
  );
  @override
  late final GeneratedColumn<DateTime> fetchedAt = GeneratedColumn<DateTime>(
    'fetched_at',
    aliasedName,
    false,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: false,
    defaultValue: currentDateAndTime,
  );
  @override
  List<GeneratedColumn> get $columns => [
    id,
    userId,
    status,
    goal,
    trainingFrequency,
    validFrom,
    validUntil,
    payloadJson,
    fetchedAt,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'plans';
  @override
  VerificationContext validateIntegrity(
    Insertable<LocalPlan> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    } else if (isInserting) {
      context.missing(_idMeta);
    }
    if (data.containsKey('user_id')) {
      context.handle(
        _userIdMeta,
        userId.isAcceptableOrUnknown(data['user_id']!, _userIdMeta),
      );
    } else if (isInserting) {
      context.missing(_userIdMeta);
    }
    if (data.containsKey('status')) {
      context.handle(
        _statusMeta,
        status.isAcceptableOrUnknown(data['status']!, _statusMeta),
      );
    } else if (isInserting) {
      context.missing(_statusMeta);
    }
    if (data.containsKey('goal')) {
      context.handle(
        _goalMeta,
        goal.isAcceptableOrUnknown(data['goal']!, _goalMeta),
      );
    } else if (isInserting) {
      context.missing(_goalMeta);
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
    if (data.containsKey('valid_from')) {
      context.handle(
        _validFromMeta,
        validFrom.isAcceptableOrUnknown(data['valid_from']!, _validFromMeta),
      );
    } else if (isInserting) {
      context.missing(_validFromMeta);
    }
    if (data.containsKey('valid_until')) {
      context.handle(
        _validUntilMeta,
        validUntil.isAcceptableOrUnknown(data['valid_until']!, _validUntilMeta),
      );
    } else if (isInserting) {
      context.missing(_validUntilMeta);
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
    if (data.containsKey('fetched_at')) {
      context.handle(
        _fetchedAtMeta,
        fetchedAt.isAcceptableOrUnknown(data['fetched_at']!, _fetchedAtMeta),
      );
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  LocalPlan map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return LocalPlan(
      id: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}id'],
      )!,
      userId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}user_id'],
      )!,
      status: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}status'],
      )!,
      goal: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}goal'],
      )!,
      trainingFrequency: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}training_frequency'],
      ),
      validFrom: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}valid_from'],
      )!,
      validUntil: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}valid_until'],
      )!,
      payloadJson: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}payload_json'],
      )!,
      fetchedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}fetched_at'],
      )!,
    );
  }

  @override
  $LocalPlansTable createAlias(String alias) {
    return $LocalPlansTable(attachedDatabase, alias);
  }
}

class LocalPlan extends DataClass implements Insertable<LocalPlan> {
  final String id;
  final String userId;
  final String status;
  final String goal;
  final int? trainingFrequency;
  final DateTime validFrom;
  final DateTime validUntil;
  final String payloadJson;
  final DateTime fetchedAt;
  const LocalPlan({
    required this.id,
    required this.userId,
    required this.status,
    required this.goal,
    this.trainingFrequency,
    required this.validFrom,
    required this.validUntil,
    required this.payloadJson,
    required this.fetchedAt,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    map['user_id'] = Variable<String>(userId);
    map['status'] = Variable<String>(status);
    map['goal'] = Variable<String>(goal);
    if (!nullToAbsent || trainingFrequency != null) {
      map['training_frequency'] = Variable<int>(trainingFrequency);
    }
    map['valid_from'] = Variable<DateTime>(validFrom);
    map['valid_until'] = Variable<DateTime>(validUntil);
    map['payload_json'] = Variable<String>(payloadJson);
    map['fetched_at'] = Variable<DateTime>(fetchedAt);
    return map;
  }

  LocalPlansCompanion toCompanion(bool nullToAbsent) {
    return LocalPlansCompanion(
      id: Value(id),
      userId: Value(userId),
      status: Value(status),
      goal: Value(goal),
      trainingFrequency: trainingFrequency == null && nullToAbsent
          ? const Value.absent()
          : Value(trainingFrequency),
      validFrom: Value(validFrom),
      validUntil: Value(validUntil),
      payloadJson: Value(payloadJson),
      fetchedAt: Value(fetchedAt),
    );
  }

  factory LocalPlan.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return LocalPlan(
      id: serializer.fromJson<String>(json['id']),
      userId: serializer.fromJson<String>(json['userId']),
      status: serializer.fromJson<String>(json['status']),
      goal: serializer.fromJson<String>(json['goal']),
      trainingFrequency: serializer.fromJson<int?>(json['trainingFrequency']),
      validFrom: serializer.fromJson<DateTime>(json['validFrom']),
      validUntil: serializer.fromJson<DateTime>(json['validUntil']),
      payloadJson: serializer.fromJson<String>(json['payloadJson']),
      fetchedAt: serializer.fromJson<DateTime>(json['fetchedAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'userId': serializer.toJson<String>(userId),
      'status': serializer.toJson<String>(status),
      'goal': serializer.toJson<String>(goal),
      'trainingFrequency': serializer.toJson<int?>(trainingFrequency),
      'validFrom': serializer.toJson<DateTime>(validFrom),
      'validUntil': serializer.toJson<DateTime>(validUntil),
      'payloadJson': serializer.toJson<String>(payloadJson),
      'fetchedAt': serializer.toJson<DateTime>(fetchedAt),
    };
  }

  LocalPlan copyWith({
    String? id,
    String? userId,
    String? status,
    String? goal,
    Value<int?> trainingFrequency = const Value.absent(),
    DateTime? validFrom,
    DateTime? validUntil,
    String? payloadJson,
    DateTime? fetchedAt,
  }) => LocalPlan(
    id: id ?? this.id,
    userId: userId ?? this.userId,
    status: status ?? this.status,
    goal: goal ?? this.goal,
    trainingFrequency: trainingFrequency.present
        ? trainingFrequency.value
        : this.trainingFrequency,
    validFrom: validFrom ?? this.validFrom,
    validUntil: validUntil ?? this.validUntil,
    payloadJson: payloadJson ?? this.payloadJson,
    fetchedAt: fetchedAt ?? this.fetchedAt,
  );
  LocalPlan copyWithCompanion(LocalPlansCompanion data) {
    return LocalPlan(
      id: data.id.present ? data.id.value : this.id,
      userId: data.userId.present ? data.userId.value : this.userId,
      status: data.status.present ? data.status.value : this.status,
      goal: data.goal.present ? data.goal.value : this.goal,
      trainingFrequency: data.trainingFrequency.present
          ? data.trainingFrequency.value
          : this.trainingFrequency,
      validFrom: data.validFrom.present ? data.validFrom.value : this.validFrom,
      validUntil: data.validUntil.present
          ? data.validUntil.value
          : this.validUntil,
      payloadJson: data.payloadJson.present
          ? data.payloadJson.value
          : this.payloadJson,
      fetchedAt: data.fetchedAt.present ? data.fetchedAt.value : this.fetchedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('LocalPlan(')
          ..write('id: $id, ')
          ..write('userId: $userId, ')
          ..write('status: $status, ')
          ..write('goal: $goal, ')
          ..write('trainingFrequency: $trainingFrequency, ')
          ..write('validFrom: $validFrom, ')
          ..write('validUntil: $validUntil, ')
          ..write('payloadJson: $payloadJson, ')
          ..write('fetchedAt: $fetchedAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    id,
    userId,
    status,
    goal,
    trainingFrequency,
    validFrom,
    validUntil,
    payloadJson,
    fetchedAt,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is LocalPlan &&
          other.id == this.id &&
          other.userId == this.userId &&
          other.status == this.status &&
          other.goal == this.goal &&
          other.trainingFrequency == this.trainingFrequency &&
          other.validFrom == this.validFrom &&
          other.validUntil == this.validUntil &&
          other.payloadJson == this.payloadJson &&
          other.fetchedAt == this.fetchedAt);
}

class LocalPlansCompanion extends UpdateCompanion<LocalPlan> {
  final Value<String> id;
  final Value<String> userId;
  final Value<String> status;
  final Value<String> goal;
  final Value<int?> trainingFrequency;
  final Value<DateTime> validFrom;
  final Value<DateTime> validUntil;
  final Value<String> payloadJson;
  final Value<DateTime> fetchedAt;
  final Value<int> rowid;
  const LocalPlansCompanion({
    this.id = const Value.absent(),
    this.userId = const Value.absent(),
    this.status = const Value.absent(),
    this.goal = const Value.absent(),
    this.trainingFrequency = const Value.absent(),
    this.validFrom = const Value.absent(),
    this.validUntil = const Value.absent(),
    this.payloadJson = const Value.absent(),
    this.fetchedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  LocalPlansCompanion.insert({
    required String id,
    required String userId,
    required String status,
    required String goal,
    this.trainingFrequency = const Value.absent(),
    required DateTime validFrom,
    required DateTime validUntil,
    required String payloadJson,
    this.fetchedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  }) : id = Value(id),
       userId = Value(userId),
       status = Value(status),
       goal = Value(goal),
       validFrom = Value(validFrom),
       validUntil = Value(validUntil),
       payloadJson = Value(payloadJson);
  static Insertable<LocalPlan> custom({
    Expression<String>? id,
    Expression<String>? userId,
    Expression<String>? status,
    Expression<String>? goal,
    Expression<int>? trainingFrequency,
    Expression<DateTime>? validFrom,
    Expression<DateTime>? validUntil,
    Expression<String>? payloadJson,
    Expression<DateTime>? fetchedAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (userId != null) 'user_id': userId,
      if (status != null) 'status': status,
      if (goal != null) 'goal': goal,
      if (trainingFrequency != null) 'training_frequency': trainingFrequency,
      if (validFrom != null) 'valid_from': validFrom,
      if (validUntil != null) 'valid_until': validUntil,
      if (payloadJson != null) 'payload_json': payloadJson,
      if (fetchedAt != null) 'fetched_at': fetchedAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  LocalPlansCompanion copyWith({
    Value<String>? id,
    Value<String>? userId,
    Value<String>? status,
    Value<String>? goal,
    Value<int?>? trainingFrequency,
    Value<DateTime>? validFrom,
    Value<DateTime>? validUntil,
    Value<String>? payloadJson,
    Value<DateTime>? fetchedAt,
    Value<int>? rowid,
  }) {
    return LocalPlansCompanion(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      status: status ?? this.status,
      goal: goal ?? this.goal,
      trainingFrequency: trainingFrequency ?? this.trainingFrequency,
      validFrom: validFrom ?? this.validFrom,
      validUntil: validUntil ?? this.validUntil,
      payloadJson: payloadJson ?? this.payloadJson,
      fetchedAt: fetchedAt ?? this.fetchedAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<String>(id.value);
    }
    if (userId.present) {
      map['user_id'] = Variable<String>(userId.value);
    }
    if (status.present) {
      map['status'] = Variable<String>(status.value);
    }
    if (goal.present) {
      map['goal'] = Variable<String>(goal.value);
    }
    if (trainingFrequency.present) {
      map['training_frequency'] = Variable<int>(trainingFrequency.value);
    }
    if (validFrom.present) {
      map['valid_from'] = Variable<DateTime>(validFrom.value);
    }
    if (validUntil.present) {
      map['valid_until'] = Variable<DateTime>(validUntil.value);
    }
    if (payloadJson.present) {
      map['payload_json'] = Variable<String>(payloadJson.value);
    }
    if (fetchedAt.present) {
      map['fetched_at'] = Variable<DateTime>(fetchedAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('LocalPlansCompanion(')
          ..write('id: $id, ')
          ..write('userId: $userId, ')
          ..write('status: $status, ')
          ..write('goal: $goal, ')
          ..write('trainingFrequency: $trainingFrequency, ')
          ..write('validFrom: $validFrom, ')
          ..write('validUntil: $validUntil, ')
          ..write('payloadJson: $payloadJson, ')
          ..write('fetchedAt: $fetchedAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $LocalForecastsTable extends LocalForecasts
    with TableInfo<$LocalForecastsTable, LocalForecast> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $LocalForecastsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _userIdMeta = const VerificationMeta('userId');
  @override
  late final GeneratedColumn<String> userId = GeneratedColumn<String>(
    'user_id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _modelVersionMeta = const VerificationMeta(
    'modelVersion',
  );
  @override
  late final GeneratedColumn<String> modelVersion = GeneratedColumn<String>(
    'model_version',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _confidenceMeta = const VerificationMeta(
    'confidence',
  );
  @override
  late final GeneratedColumn<String> confidence = GeneratedColumn<String>(
    'confidence',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _fallbackMeta = const VerificationMeta(
    'fallback',
  );
  @override
  late final GeneratedColumn<bool> fallback = GeneratedColumn<bool>(
    'fallback',
    aliasedName,
    false,
    type: DriftSqlType.bool,
    requiredDuringInsert: true,
    defaultConstraints: GeneratedColumn.constraintIsAlways(
      'CHECK ("fallback" IN (0, 1))',
    ),
  );
  static const VerificationMeta _generatedAtMeta = const VerificationMeta(
    'generatedAt',
  );
  @override
  late final GeneratedColumn<DateTime> generatedAt = GeneratedColumn<DateTime>(
    'generated_at',
    aliasedName,
    false,
    type: DriftSqlType.dateTime,
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
  static const VerificationMeta _fetchedAtMeta = const VerificationMeta(
    'fetchedAt',
  );
  @override
  late final GeneratedColumn<DateTime> fetchedAt = GeneratedColumn<DateTime>(
    'fetched_at',
    aliasedName,
    false,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: false,
    defaultValue: currentDateAndTime,
  );
  @override
  List<GeneratedColumn> get $columns => [
    userId,
    modelVersion,
    confidence,
    fallback,
    generatedAt,
    payloadJson,
    fetchedAt,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'forecasts';
  @override
  VerificationContext validateIntegrity(
    Insertable<LocalForecast> instance, {
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
    if (data.containsKey('model_version')) {
      context.handle(
        _modelVersionMeta,
        modelVersion.isAcceptableOrUnknown(
          data['model_version']!,
          _modelVersionMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_modelVersionMeta);
    }
    if (data.containsKey('confidence')) {
      context.handle(
        _confidenceMeta,
        confidence.isAcceptableOrUnknown(data['confidence']!, _confidenceMeta),
      );
    } else if (isInserting) {
      context.missing(_confidenceMeta);
    }
    if (data.containsKey('fallback')) {
      context.handle(
        _fallbackMeta,
        fallback.isAcceptableOrUnknown(data['fallback']!, _fallbackMeta),
      );
    } else if (isInserting) {
      context.missing(_fallbackMeta);
    }
    if (data.containsKey('generated_at')) {
      context.handle(
        _generatedAtMeta,
        generatedAt.isAcceptableOrUnknown(
          data['generated_at']!,
          _generatedAtMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_generatedAtMeta);
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
    if (data.containsKey('fetched_at')) {
      context.handle(
        _fetchedAtMeta,
        fetchedAt.isAcceptableOrUnknown(data['fetched_at']!, _fetchedAtMeta),
      );
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {userId};
  @override
  LocalForecast map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return LocalForecast(
      userId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}user_id'],
      )!,
      modelVersion: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}model_version'],
      )!,
      confidence: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}confidence'],
      )!,
      fallback: attachedDatabase.typeMapping.read(
        DriftSqlType.bool,
        data['${effectivePrefix}fallback'],
      )!,
      generatedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}generated_at'],
      )!,
      payloadJson: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}payload_json'],
      )!,
      fetchedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}fetched_at'],
      )!,
    );
  }

  @override
  $LocalForecastsTable createAlias(String alias) {
    return $LocalForecastsTable(attachedDatabase, alias);
  }
}

class LocalForecast extends DataClass implements Insertable<LocalForecast> {
  final String userId;
  final String modelVersion;
  final String confidence;
  final bool fallback;
  final DateTime generatedAt;
  final String payloadJson;
  final DateTime fetchedAt;
  const LocalForecast({
    required this.userId,
    required this.modelVersion,
    required this.confidence,
    required this.fallback,
    required this.generatedAt,
    required this.payloadJson,
    required this.fetchedAt,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['user_id'] = Variable<String>(userId);
    map['model_version'] = Variable<String>(modelVersion);
    map['confidence'] = Variable<String>(confidence);
    map['fallback'] = Variable<bool>(fallback);
    map['generated_at'] = Variable<DateTime>(generatedAt);
    map['payload_json'] = Variable<String>(payloadJson);
    map['fetched_at'] = Variable<DateTime>(fetchedAt);
    return map;
  }

  LocalForecastsCompanion toCompanion(bool nullToAbsent) {
    return LocalForecastsCompanion(
      userId: Value(userId),
      modelVersion: Value(modelVersion),
      confidence: Value(confidence),
      fallback: Value(fallback),
      generatedAt: Value(generatedAt),
      payloadJson: Value(payloadJson),
      fetchedAt: Value(fetchedAt),
    );
  }

  factory LocalForecast.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return LocalForecast(
      userId: serializer.fromJson<String>(json['userId']),
      modelVersion: serializer.fromJson<String>(json['modelVersion']),
      confidence: serializer.fromJson<String>(json['confidence']),
      fallback: serializer.fromJson<bool>(json['fallback']),
      generatedAt: serializer.fromJson<DateTime>(json['generatedAt']),
      payloadJson: serializer.fromJson<String>(json['payloadJson']),
      fetchedAt: serializer.fromJson<DateTime>(json['fetchedAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'userId': serializer.toJson<String>(userId),
      'modelVersion': serializer.toJson<String>(modelVersion),
      'confidence': serializer.toJson<String>(confidence),
      'fallback': serializer.toJson<bool>(fallback),
      'generatedAt': serializer.toJson<DateTime>(generatedAt),
      'payloadJson': serializer.toJson<String>(payloadJson),
      'fetchedAt': serializer.toJson<DateTime>(fetchedAt),
    };
  }

  LocalForecast copyWith({
    String? userId,
    String? modelVersion,
    String? confidence,
    bool? fallback,
    DateTime? generatedAt,
    String? payloadJson,
    DateTime? fetchedAt,
  }) => LocalForecast(
    userId: userId ?? this.userId,
    modelVersion: modelVersion ?? this.modelVersion,
    confidence: confidence ?? this.confidence,
    fallback: fallback ?? this.fallback,
    generatedAt: generatedAt ?? this.generatedAt,
    payloadJson: payloadJson ?? this.payloadJson,
    fetchedAt: fetchedAt ?? this.fetchedAt,
  );
  LocalForecast copyWithCompanion(LocalForecastsCompanion data) {
    return LocalForecast(
      userId: data.userId.present ? data.userId.value : this.userId,
      modelVersion: data.modelVersion.present
          ? data.modelVersion.value
          : this.modelVersion,
      confidence: data.confidence.present
          ? data.confidence.value
          : this.confidence,
      fallback: data.fallback.present ? data.fallback.value : this.fallback,
      generatedAt: data.generatedAt.present
          ? data.generatedAt.value
          : this.generatedAt,
      payloadJson: data.payloadJson.present
          ? data.payloadJson.value
          : this.payloadJson,
      fetchedAt: data.fetchedAt.present ? data.fetchedAt.value : this.fetchedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('LocalForecast(')
          ..write('userId: $userId, ')
          ..write('modelVersion: $modelVersion, ')
          ..write('confidence: $confidence, ')
          ..write('fallback: $fallback, ')
          ..write('generatedAt: $generatedAt, ')
          ..write('payloadJson: $payloadJson, ')
          ..write('fetchedAt: $fetchedAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    userId,
    modelVersion,
    confidence,
    fallback,
    generatedAt,
    payloadJson,
    fetchedAt,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is LocalForecast &&
          other.userId == this.userId &&
          other.modelVersion == this.modelVersion &&
          other.confidence == this.confidence &&
          other.fallback == this.fallback &&
          other.generatedAt == this.generatedAt &&
          other.payloadJson == this.payloadJson &&
          other.fetchedAt == this.fetchedAt);
}

class LocalForecastsCompanion extends UpdateCompanion<LocalForecast> {
  final Value<String> userId;
  final Value<String> modelVersion;
  final Value<String> confidence;
  final Value<bool> fallback;
  final Value<DateTime> generatedAt;
  final Value<String> payloadJson;
  final Value<DateTime> fetchedAt;
  final Value<int> rowid;
  const LocalForecastsCompanion({
    this.userId = const Value.absent(),
    this.modelVersion = const Value.absent(),
    this.confidence = const Value.absent(),
    this.fallback = const Value.absent(),
    this.generatedAt = const Value.absent(),
    this.payloadJson = const Value.absent(),
    this.fetchedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  LocalForecastsCompanion.insert({
    required String userId,
    required String modelVersion,
    required String confidence,
    required bool fallback,
    required DateTime generatedAt,
    required String payloadJson,
    this.fetchedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  }) : userId = Value(userId),
       modelVersion = Value(modelVersion),
       confidence = Value(confidence),
       fallback = Value(fallback),
       generatedAt = Value(generatedAt),
       payloadJson = Value(payloadJson);
  static Insertable<LocalForecast> custom({
    Expression<String>? userId,
    Expression<String>? modelVersion,
    Expression<String>? confidence,
    Expression<bool>? fallback,
    Expression<DateTime>? generatedAt,
    Expression<String>? payloadJson,
    Expression<DateTime>? fetchedAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (userId != null) 'user_id': userId,
      if (modelVersion != null) 'model_version': modelVersion,
      if (confidence != null) 'confidence': confidence,
      if (fallback != null) 'fallback': fallback,
      if (generatedAt != null) 'generated_at': generatedAt,
      if (payloadJson != null) 'payload_json': payloadJson,
      if (fetchedAt != null) 'fetched_at': fetchedAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  LocalForecastsCompanion copyWith({
    Value<String>? userId,
    Value<String>? modelVersion,
    Value<String>? confidence,
    Value<bool>? fallback,
    Value<DateTime>? generatedAt,
    Value<String>? payloadJson,
    Value<DateTime>? fetchedAt,
    Value<int>? rowid,
  }) {
    return LocalForecastsCompanion(
      userId: userId ?? this.userId,
      modelVersion: modelVersion ?? this.modelVersion,
      confidence: confidence ?? this.confidence,
      fallback: fallback ?? this.fallback,
      generatedAt: generatedAt ?? this.generatedAt,
      payloadJson: payloadJson ?? this.payloadJson,
      fetchedAt: fetchedAt ?? this.fetchedAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (userId.present) {
      map['user_id'] = Variable<String>(userId.value);
    }
    if (modelVersion.present) {
      map['model_version'] = Variable<String>(modelVersion.value);
    }
    if (confidence.present) {
      map['confidence'] = Variable<String>(confidence.value);
    }
    if (fallback.present) {
      map['fallback'] = Variable<bool>(fallback.value);
    }
    if (generatedAt.present) {
      map['generated_at'] = Variable<DateTime>(generatedAt.value);
    }
    if (payloadJson.present) {
      map['payload_json'] = Variable<String>(payloadJson.value);
    }
    if (fetchedAt.present) {
      map['fetched_at'] = Variable<DateTime>(fetchedAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('LocalForecastsCompanion(')
          ..write('userId: $userId, ')
          ..write('modelVersion: $modelVersion, ')
          ..write('confidence: $confidence, ')
          ..write('fallback: $fallback, ')
          ..write('generatedAt: $generatedAt, ')
          ..write('payloadJson: $payloadJson, ')
          ..write('fetchedAt: $fetchedAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $LocalExercisesTable extends LocalExercises
    with TableInfo<$LocalExercisesTable, LocalExercise> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $LocalExercisesTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
    'id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _exerciseIdMeta = const VerificationMeta(
    'exerciseId',
  );
  @override
  late final GeneratedColumn<String> exerciseId = GeneratedColumn<String>(
    'exercise_id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _exerciseNameMeta = const VerificationMeta(
    'exerciseName',
  );
  @override
  late final GeneratedColumn<String> exerciseName = GeneratedColumn<String>(
    'exercise_name',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _exerciseNameRuMeta = const VerificationMeta(
    'exerciseNameRu',
  );
  @override
  late final GeneratedColumn<String> exerciseNameRu = GeneratedColumn<String>(
    'exercise_name_ru',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _primaryMuscleGroupMeta =
      const VerificationMeta('primaryMuscleGroup');
  @override
  late final GeneratedColumn<String> primaryMuscleGroup =
      GeneratedColumn<String>(
        'primary_muscle_group',
        aliasedName,
        false,
        type: DriftSqlType.string,
        requiredDuringInsert: true,
      );
  static const VerificationMeta _secondaryMuscleGroupJsonMeta =
      const VerificationMeta('secondaryMuscleGroupJson');
  @override
  late final GeneratedColumn<String> secondaryMuscleGroupJson =
      GeneratedColumn<String>(
        'secondary_muscle_group_json',
        aliasedName,
        false,
        type: DriftSqlType.string,
        requiredDuringInsert: false,
        defaultValue: const Constant('[]'),
      );
  static const VerificationMeta _equipmentJsonMeta = const VerificationMeta(
    'equipmentJson',
  );
  @override
  late final GeneratedColumn<String> equipmentJson = GeneratedColumn<String>(
    'equipment_json',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant('[]'),
  );
  static const VerificationMeta _bodyRegionMeta = const VerificationMeta(
    'bodyRegion',
  );
  @override
  late final GeneratedColumn<String> bodyRegion = GeneratedColumn<String>(
    'body_region',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _versionMeta = const VerificationMeta(
    'version',
  );
  @override
  late final GeneratedColumn<int> version = GeneratedColumn<int>(
    'version',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
    defaultValue: const Constant(1),
  );
  static const VerificationMeta _fetchedAtMeta = const VerificationMeta(
    'fetchedAt',
  );
  @override
  late final GeneratedColumn<DateTime> fetchedAt = GeneratedColumn<DateTime>(
    'fetched_at',
    aliasedName,
    false,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: false,
    defaultValue: currentDateAndTime,
  );
  @override
  List<GeneratedColumn> get $columns => [
    id,
    exerciseId,
    exerciseName,
    exerciseNameRu,
    primaryMuscleGroup,
    secondaryMuscleGroupJson,
    equipmentJson,
    bodyRegion,
    version,
    fetchedAt,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'exercises_catalog';
  @override
  VerificationContext validateIntegrity(
    Insertable<LocalExercise> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    } else if (isInserting) {
      context.missing(_idMeta);
    }
    if (data.containsKey('exercise_id')) {
      context.handle(
        _exerciseIdMeta,
        exerciseId.isAcceptableOrUnknown(data['exercise_id']!, _exerciseIdMeta),
      );
    } else if (isInserting) {
      context.missing(_exerciseIdMeta);
    }
    if (data.containsKey('exercise_name')) {
      context.handle(
        _exerciseNameMeta,
        exerciseName.isAcceptableOrUnknown(
          data['exercise_name']!,
          _exerciseNameMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_exerciseNameMeta);
    }
    if (data.containsKey('exercise_name_ru')) {
      context.handle(
        _exerciseNameRuMeta,
        exerciseNameRu.isAcceptableOrUnknown(
          data['exercise_name_ru']!,
          _exerciseNameRuMeta,
        ),
      );
    }
    if (data.containsKey('primary_muscle_group')) {
      context.handle(
        _primaryMuscleGroupMeta,
        primaryMuscleGroup.isAcceptableOrUnknown(
          data['primary_muscle_group']!,
          _primaryMuscleGroupMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_primaryMuscleGroupMeta);
    }
    if (data.containsKey('secondary_muscle_group_json')) {
      context.handle(
        _secondaryMuscleGroupJsonMeta,
        secondaryMuscleGroupJson.isAcceptableOrUnknown(
          data['secondary_muscle_group_json']!,
          _secondaryMuscleGroupJsonMeta,
        ),
      );
    }
    if (data.containsKey('equipment_json')) {
      context.handle(
        _equipmentJsonMeta,
        equipmentJson.isAcceptableOrUnknown(
          data['equipment_json']!,
          _equipmentJsonMeta,
        ),
      );
    }
    if (data.containsKey('body_region')) {
      context.handle(
        _bodyRegionMeta,
        bodyRegion.isAcceptableOrUnknown(data['body_region']!, _bodyRegionMeta),
      );
    } else if (isInserting) {
      context.missing(_bodyRegionMeta);
    }
    if (data.containsKey('version')) {
      context.handle(
        _versionMeta,
        version.isAcceptableOrUnknown(data['version']!, _versionMeta),
      );
    }
    if (data.containsKey('fetched_at')) {
      context.handle(
        _fetchedAtMeta,
        fetchedAt.isAcceptableOrUnknown(data['fetched_at']!, _fetchedAtMeta),
      );
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  LocalExercise map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return LocalExercise(
      id: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}id'],
      )!,
      exerciseId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}exercise_id'],
      )!,
      exerciseName: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}exercise_name'],
      )!,
      exerciseNameRu: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}exercise_name_ru'],
      ),
      primaryMuscleGroup: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}primary_muscle_group'],
      )!,
      secondaryMuscleGroupJson: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}secondary_muscle_group_json'],
      )!,
      equipmentJson: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}equipment_json'],
      )!,
      bodyRegion: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}body_region'],
      )!,
      version: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}version'],
      )!,
      fetchedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}fetched_at'],
      )!,
    );
  }

  @override
  $LocalExercisesTable createAlias(String alias) {
    return $LocalExercisesTable(attachedDatabase, alias);
  }
}

class LocalExercise extends DataClass implements Insertable<LocalExercise> {
  final String id;
  final String exerciseId;
  final String exerciseName;
  final String? exerciseNameRu;
  final String primaryMuscleGroup;
  final String secondaryMuscleGroupJson;
  final String equipmentJson;
  final String bodyRegion;
  final int version;
  final DateTime fetchedAt;
  const LocalExercise({
    required this.id,
    required this.exerciseId,
    required this.exerciseName,
    this.exerciseNameRu,
    required this.primaryMuscleGroup,
    required this.secondaryMuscleGroupJson,
    required this.equipmentJson,
    required this.bodyRegion,
    required this.version,
    required this.fetchedAt,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    map['exercise_id'] = Variable<String>(exerciseId);
    map['exercise_name'] = Variable<String>(exerciseName);
    if (!nullToAbsent || exerciseNameRu != null) {
      map['exercise_name_ru'] = Variable<String>(exerciseNameRu);
    }
    map['primary_muscle_group'] = Variable<String>(primaryMuscleGroup);
    map['secondary_muscle_group_json'] = Variable<String>(
      secondaryMuscleGroupJson,
    );
    map['equipment_json'] = Variable<String>(equipmentJson);
    map['body_region'] = Variable<String>(bodyRegion);
    map['version'] = Variable<int>(version);
    map['fetched_at'] = Variable<DateTime>(fetchedAt);
    return map;
  }

  LocalExercisesCompanion toCompanion(bool nullToAbsent) {
    return LocalExercisesCompanion(
      id: Value(id),
      exerciseId: Value(exerciseId),
      exerciseName: Value(exerciseName),
      exerciseNameRu: exerciseNameRu == null && nullToAbsent
          ? const Value.absent()
          : Value(exerciseNameRu),
      primaryMuscleGroup: Value(primaryMuscleGroup),
      secondaryMuscleGroupJson: Value(secondaryMuscleGroupJson),
      equipmentJson: Value(equipmentJson),
      bodyRegion: Value(bodyRegion),
      version: Value(version),
      fetchedAt: Value(fetchedAt),
    );
  }

  factory LocalExercise.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return LocalExercise(
      id: serializer.fromJson<String>(json['id']),
      exerciseId: serializer.fromJson<String>(json['exerciseId']),
      exerciseName: serializer.fromJson<String>(json['exerciseName']),
      exerciseNameRu: serializer.fromJson<String?>(json['exerciseNameRu']),
      primaryMuscleGroup: serializer.fromJson<String>(
        json['primaryMuscleGroup'],
      ),
      secondaryMuscleGroupJson: serializer.fromJson<String>(
        json['secondaryMuscleGroupJson'],
      ),
      equipmentJson: serializer.fromJson<String>(json['equipmentJson']),
      bodyRegion: serializer.fromJson<String>(json['bodyRegion']),
      version: serializer.fromJson<int>(json['version']),
      fetchedAt: serializer.fromJson<DateTime>(json['fetchedAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'exerciseId': serializer.toJson<String>(exerciseId),
      'exerciseName': serializer.toJson<String>(exerciseName),
      'exerciseNameRu': serializer.toJson<String?>(exerciseNameRu),
      'primaryMuscleGroup': serializer.toJson<String>(primaryMuscleGroup),
      'secondaryMuscleGroupJson': serializer.toJson<String>(
        secondaryMuscleGroupJson,
      ),
      'equipmentJson': serializer.toJson<String>(equipmentJson),
      'bodyRegion': serializer.toJson<String>(bodyRegion),
      'version': serializer.toJson<int>(version),
      'fetchedAt': serializer.toJson<DateTime>(fetchedAt),
    };
  }

  LocalExercise copyWith({
    String? id,
    String? exerciseId,
    String? exerciseName,
    Value<String?> exerciseNameRu = const Value.absent(),
    String? primaryMuscleGroup,
    String? secondaryMuscleGroupJson,
    String? equipmentJson,
    String? bodyRegion,
    int? version,
    DateTime? fetchedAt,
  }) => LocalExercise(
    id: id ?? this.id,
    exerciseId: exerciseId ?? this.exerciseId,
    exerciseName: exerciseName ?? this.exerciseName,
    exerciseNameRu: exerciseNameRu.present
        ? exerciseNameRu.value
        : this.exerciseNameRu,
    primaryMuscleGroup: primaryMuscleGroup ?? this.primaryMuscleGroup,
    secondaryMuscleGroupJson:
        secondaryMuscleGroupJson ?? this.secondaryMuscleGroupJson,
    equipmentJson: equipmentJson ?? this.equipmentJson,
    bodyRegion: bodyRegion ?? this.bodyRegion,
    version: version ?? this.version,
    fetchedAt: fetchedAt ?? this.fetchedAt,
  );
  LocalExercise copyWithCompanion(LocalExercisesCompanion data) {
    return LocalExercise(
      id: data.id.present ? data.id.value : this.id,
      exerciseId: data.exerciseId.present
          ? data.exerciseId.value
          : this.exerciseId,
      exerciseName: data.exerciseName.present
          ? data.exerciseName.value
          : this.exerciseName,
      exerciseNameRu: data.exerciseNameRu.present
          ? data.exerciseNameRu.value
          : this.exerciseNameRu,
      primaryMuscleGroup: data.primaryMuscleGroup.present
          ? data.primaryMuscleGroup.value
          : this.primaryMuscleGroup,
      secondaryMuscleGroupJson: data.secondaryMuscleGroupJson.present
          ? data.secondaryMuscleGroupJson.value
          : this.secondaryMuscleGroupJson,
      equipmentJson: data.equipmentJson.present
          ? data.equipmentJson.value
          : this.equipmentJson,
      bodyRegion: data.bodyRegion.present
          ? data.bodyRegion.value
          : this.bodyRegion,
      version: data.version.present ? data.version.value : this.version,
      fetchedAt: data.fetchedAt.present ? data.fetchedAt.value : this.fetchedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('LocalExercise(')
          ..write('id: $id, ')
          ..write('exerciseId: $exerciseId, ')
          ..write('exerciseName: $exerciseName, ')
          ..write('exerciseNameRu: $exerciseNameRu, ')
          ..write('primaryMuscleGroup: $primaryMuscleGroup, ')
          ..write('secondaryMuscleGroupJson: $secondaryMuscleGroupJson, ')
          ..write('equipmentJson: $equipmentJson, ')
          ..write('bodyRegion: $bodyRegion, ')
          ..write('version: $version, ')
          ..write('fetchedAt: $fetchedAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    id,
    exerciseId,
    exerciseName,
    exerciseNameRu,
    primaryMuscleGroup,
    secondaryMuscleGroupJson,
    equipmentJson,
    bodyRegion,
    version,
    fetchedAt,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is LocalExercise &&
          other.id == this.id &&
          other.exerciseId == this.exerciseId &&
          other.exerciseName == this.exerciseName &&
          other.exerciseNameRu == this.exerciseNameRu &&
          other.primaryMuscleGroup == this.primaryMuscleGroup &&
          other.secondaryMuscleGroupJson == this.secondaryMuscleGroupJson &&
          other.equipmentJson == this.equipmentJson &&
          other.bodyRegion == this.bodyRegion &&
          other.version == this.version &&
          other.fetchedAt == this.fetchedAt);
}

class LocalExercisesCompanion extends UpdateCompanion<LocalExercise> {
  final Value<String> id;
  final Value<String> exerciseId;
  final Value<String> exerciseName;
  final Value<String?> exerciseNameRu;
  final Value<String> primaryMuscleGroup;
  final Value<String> secondaryMuscleGroupJson;
  final Value<String> equipmentJson;
  final Value<String> bodyRegion;
  final Value<int> version;
  final Value<DateTime> fetchedAt;
  final Value<int> rowid;
  const LocalExercisesCompanion({
    this.id = const Value.absent(),
    this.exerciseId = const Value.absent(),
    this.exerciseName = const Value.absent(),
    this.exerciseNameRu = const Value.absent(),
    this.primaryMuscleGroup = const Value.absent(),
    this.secondaryMuscleGroupJson = const Value.absent(),
    this.equipmentJson = const Value.absent(),
    this.bodyRegion = const Value.absent(),
    this.version = const Value.absent(),
    this.fetchedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  LocalExercisesCompanion.insert({
    required String id,
    required String exerciseId,
    required String exerciseName,
    this.exerciseNameRu = const Value.absent(),
    required String primaryMuscleGroup,
    this.secondaryMuscleGroupJson = const Value.absent(),
    this.equipmentJson = const Value.absent(),
    required String bodyRegion,
    this.version = const Value.absent(),
    this.fetchedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  }) : id = Value(id),
       exerciseId = Value(exerciseId),
       exerciseName = Value(exerciseName),
       primaryMuscleGroup = Value(primaryMuscleGroup),
       bodyRegion = Value(bodyRegion);
  static Insertable<LocalExercise> custom({
    Expression<String>? id,
    Expression<String>? exerciseId,
    Expression<String>? exerciseName,
    Expression<String>? exerciseNameRu,
    Expression<String>? primaryMuscleGroup,
    Expression<String>? secondaryMuscleGroupJson,
    Expression<String>? equipmentJson,
    Expression<String>? bodyRegion,
    Expression<int>? version,
    Expression<DateTime>? fetchedAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (exerciseId != null) 'exercise_id': exerciseId,
      if (exerciseName != null) 'exercise_name': exerciseName,
      if (exerciseNameRu != null) 'exercise_name_ru': exerciseNameRu,
      if (primaryMuscleGroup != null)
        'primary_muscle_group': primaryMuscleGroup,
      if (secondaryMuscleGroupJson != null)
        'secondary_muscle_group_json': secondaryMuscleGroupJson,
      if (equipmentJson != null) 'equipment_json': equipmentJson,
      if (bodyRegion != null) 'body_region': bodyRegion,
      if (version != null) 'version': version,
      if (fetchedAt != null) 'fetched_at': fetchedAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  LocalExercisesCompanion copyWith({
    Value<String>? id,
    Value<String>? exerciseId,
    Value<String>? exerciseName,
    Value<String?>? exerciseNameRu,
    Value<String>? primaryMuscleGroup,
    Value<String>? secondaryMuscleGroupJson,
    Value<String>? equipmentJson,
    Value<String>? bodyRegion,
    Value<int>? version,
    Value<DateTime>? fetchedAt,
    Value<int>? rowid,
  }) {
    return LocalExercisesCompanion(
      id: id ?? this.id,
      exerciseId: exerciseId ?? this.exerciseId,
      exerciseName: exerciseName ?? this.exerciseName,
      exerciseNameRu: exerciseNameRu ?? this.exerciseNameRu,
      primaryMuscleGroup: primaryMuscleGroup ?? this.primaryMuscleGroup,
      secondaryMuscleGroupJson:
          secondaryMuscleGroupJson ?? this.secondaryMuscleGroupJson,
      equipmentJson: equipmentJson ?? this.equipmentJson,
      bodyRegion: bodyRegion ?? this.bodyRegion,
      version: version ?? this.version,
      fetchedAt: fetchedAt ?? this.fetchedAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<String>(id.value);
    }
    if (exerciseId.present) {
      map['exercise_id'] = Variable<String>(exerciseId.value);
    }
    if (exerciseName.present) {
      map['exercise_name'] = Variable<String>(exerciseName.value);
    }
    if (exerciseNameRu.present) {
      map['exercise_name_ru'] = Variable<String>(exerciseNameRu.value);
    }
    if (primaryMuscleGroup.present) {
      map['primary_muscle_group'] = Variable<String>(primaryMuscleGroup.value);
    }
    if (secondaryMuscleGroupJson.present) {
      map['secondary_muscle_group_json'] = Variable<String>(
        secondaryMuscleGroupJson.value,
      );
    }
    if (equipmentJson.present) {
      map['equipment_json'] = Variable<String>(equipmentJson.value);
    }
    if (bodyRegion.present) {
      map['body_region'] = Variable<String>(bodyRegion.value);
    }
    if (version.present) {
      map['version'] = Variable<int>(version.value);
    }
    if (fetchedAt.present) {
      map['fetched_at'] = Variable<DateTime>(fetchedAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('LocalExercisesCompanion(')
          ..write('id: $id, ')
          ..write('exerciseId: $exerciseId, ')
          ..write('exerciseName: $exerciseName, ')
          ..write('exerciseNameRu: $exerciseNameRu, ')
          ..write('primaryMuscleGroup: $primaryMuscleGroup, ')
          ..write('secondaryMuscleGroupJson: $secondaryMuscleGroupJson, ')
          ..write('equipmentJson: $equipmentJson, ')
          ..write('bodyRegion: $bodyRegion, ')
          ..write('version: $version, ')
          ..write('fetchedAt: $fetchedAt, ')
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
  late final $LocalWorkoutsTable localWorkouts = $LocalWorkoutsTable(this);
  late final $LocalExerciseLogsTable localExerciseLogs =
      $LocalExerciseLogsTable(this);
  late final $LocalInBodyMeasurementsTable localInBodyMeasurements =
      $LocalInBodyMeasurementsTable(this);
  late final $LocalPlansTable localPlans = $LocalPlansTable(this);
  late final $LocalForecastsTable localForecasts = $LocalForecastsTable(this);
  late final $LocalExercisesTable localExercises = $LocalExercisesTable(this);
  late final $SyncQueueTable syncQueue = $SyncQueueTable(this);
  @override
  Iterable<TableInfo<Table, Object?>> get allTables =>
      allSchemaEntities.whereType<TableInfo<Table, Object?>>();
  @override
  List<DatabaseSchemaEntity> get allSchemaEntities => [
    profiles,
    localWorkouts,
    localExerciseLogs,
    localInBodyMeasurements,
    localPlans,
    localForecasts,
    localExercises,
    syncQueue,
  ];
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
typedef $$LocalWorkoutsTableCreateCompanionBuilder =
    LocalWorkoutsCompanion Function({
      required String id,
      required String userId,
      Value<String?> clientId,
      required DateTime performedAt,
      Value<DateTime?> finishedAt,
      required String status,
      required String origin,
      Value<String?> planDayId,
      Value<String?> notes,
      Value<String> syncStatus,
      Value<DateTime> createdAt,
      Value<int> rowid,
    });
typedef $$LocalWorkoutsTableUpdateCompanionBuilder =
    LocalWorkoutsCompanion Function({
      Value<String> id,
      Value<String> userId,
      Value<String?> clientId,
      Value<DateTime> performedAt,
      Value<DateTime?> finishedAt,
      Value<String> status,
      Value<String> origin,
      Value<String?> planDayId,
      Value<String?> notes,
      Value<String> syncStatus,
      Value<DateTime> createdAt,
      Value<int> rowid,
    });

class $$LocalWorkoutsTableFilterComposer
    extends Composer<_$AppDatabase, $LocalWorkoutsTable> {
  $$LocalWorkoutsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get id => $composableBuilder(
    column: $table.id,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get userId => $composableBuilder(
    column: $table.userId,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get clientId => $composableBuilder(
    column: $table.clientId,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get performedAt => $composableBuilder(
    column: $table.performedAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get finishedAt => $composableBuilder(
    column: $table.finishedAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get status => $composableBuilder(
    column: $table.status,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get origin => $composableBuilder(
    column: $table.origin,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get planDayId => $composableBuilder(
    column: $table.planDayId,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get notes => $composableBuilder(
    column: $table.notes,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get syncStatus => $composableBuilder(
    column: $table.syncStatus,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
    column: $table.createdAt,
    builder: (column) => ColumnFilters(column),
  );
}

class $$LocalWorkoutsTableOrderingComposer
    extends Composer<_$AppDatabase, $LocalWorkoutsTable> {
  $$LocalWorkoutsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get id => $composableBuilder(
    column: $table.id,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get userId => $composableBuilder(
    column: $table.userId,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get clientId => $composableBuilder(
    column: $table.clientId,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get performedAt => $composableBuilder(
    column: $table.performedAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get finishedAt => $composableBuilder(
    column: $table.finishedAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get status => $composableBuilder(
    column: $table.status,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get origin => $composableBuilder(
    column: $table.origin,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get planDayId => $composableBuilder(
    column: $table.planDayId,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get notes => $composableBuilder(
    column: $table.notes,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get syncStatus => $composableBuilder(
    column: $table.syncStatus,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
    column: $table.createdAt,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$LocalWorkoutsTableAnnotationComposer
    extends Composer<_$AppDatabase, $LocalWorkoutsTable> {
  $$LocalWorkoutsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get userId =>
      $composableBuilder(column: $table.userId, builder: (column) => column);

  GeneratedColumn<String> get clientId =>
      $composableBuilder(column: $table.clientId, builder: (column) => column);

  GeneratedColumn<DateTime> get performedAt => $composableBuilder(
    column: $table.performedAt,
    builder: (column) => column,
  );

  GeneratedColumn<DateTime> get finishedAt => $composableBuilder(
    column: $table.finishedAt,
    builder: (column) => column,
  );

  GeneratedColumn<String> get status =>
      $composableBuilder(column: $table.status, builder: (column) => column);

  GeneratedColumn<String> get origin =>
      $composableBuilder(column: $table.origin, builder: (column) => column);

  GeneratedColumn<String> get planDayId =>
      $composableBuilder(column: $table.planDayId, builder: (column) => column);

  GeneratedColumn<String> get notes =>
      $composableBuilder(column: $table.notes, builder: (column) => column);

  GeneratedColumn<String> get syncStatus => $composableBuilder(
    column: $table.syncStatus,
    builder: (column) => column,
  );

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);
}

class $$LocalWorkoutsTableTableManager
    extends
        RootTableManager<
          _$AppDatabase,
          $LocalWorkoutsTable,
          LocalWorkout,
          $$LocalWorkoutsTableFilterComposer,
          $$LocalWorkoutsTableOrderingComposer,
          $$LocalWorkoutsTableAnnotationComposer,
          $$LocalWorkoutsTableCreateCompanionBuilder,
          $$LocalWorkoutsTableUpdateCompanionBuilder,
          (
            LocalWorkout,
            BaseReferences<_$AppDatabase, $LocalWorkoutsTable, LocalWorkout>,
          ),
          LocalWorkout,
          PrefetchHooks Function()
        > {
  $$LocalWorkoutsTableTableManager(_$AppDatabase db, $LocalWorkoutsTable table)
    : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$LocalWorkoutsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$LocalWorkoutsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$LocalWorkoutsTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback:
              ({
                Value<String> id = const Value.absent(),
                Value<String> userId = const Value.absent(),
                Value<String?> clientId = const Value.absent(),
                Value<DateTime> performedAt = const Value.absent(),
                Value<DateTime?> finishedAt = const Value.absent(),
                Value<String> status = const Value.absent(),
                Value<String> origin = const Value.absent(),
                Value<String?> planDayId = const Value.absent(),
                Value<String?> notes = const Value.absent(),
                Value<String> syncStatus = const Value.absent(),
                Value<DateTime> createdAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => LocalWorkoutsCompanion(
                id: id,
                userId: userId,
                clientId: clientId,
                performedAt: performedAt,
                finishedAt: finishedAt,
                status: status,
                origin: origin,
                planDayId: planDayId,
                notes: notes,
                syncStatus: syncStatus,
                createdAt: createdAt,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String id,
                required String userId,
                Value<String?> clientId = const Value.absent(),
                required DateTime performedAt,
                Value<DateTime?> finishedAt = const Value.absent(),
                required String status,
                required String origin,
                Value<String?> planDayId = const Value.absent(),
                Value<String?> notes = const Value.absent(),
                Value<String> syncStatus = const Value.absent(),
                Value<DateTime> createdAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => LocalWorkoutsCompanion.insert(
                id: id,
                userId: userId,
                clientId: clientId,
                performedAt: performedAt,
                finishedAt: finishedAt,
                status: status,
                origin: origin,
                planDayId: planDayId,
                notes: notes,
                syncStatus: syncStatus,
                createdAt: createdAt,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$LocalWorkoutsTableProcessedTableManager =
    ProcessedTableManager<
      _$AppDatabase,
      $LocalWorkoutsTable,
      LocalWorkout,
      $$LocalWorkoutsTableFilterComposer,
      $$LocalWorkoutsTableOrderingComposer,
      $$LocalWorkoutsTableAnnotationComposer,
      $$LocalWorkoutsTableCreateCompanionBuilder,
      $$LocalWorkoutsTableUpdateCompanionBuilder,
      (
        LocalWorkout,
        BaseReferences<_$AppDatabase, $LocalWorkoutsTable, LocalWorkout>,
      ),
      LocalWorkout,
      PrefetchHooks Function()
    >;
typedef $$LocalExerciseLogsTableCreateCompanionBuilder =
    LocalExerciseLogsCompanion Function({
      required String id,
      required String workoutId,
      required String exerciseId,
      Value<String?> clientId,
      required int setNumber,
      required int reps,
      required double weightKg,
      Value<int?> rpe,
      Value<int?> restSeconds,
      Value<bool> skipped,
      required DateTime loggedAt,
      Value<String> syncStatus,
      Value<int> rowid,
    });
typedef $$LocalExerciseLogsTableUpdateCompanionBuilder =
    LocalExerciseLogsCompanion Function({
      Value<String> id,
      Value<String> workoutId,
      Value<String> exerciseId,
      Value<String?> clientId,
      Value<int> setNumber,
      Value<int> reps,
      Value<double> weightKg,
      Value<int?> rpe,
      Value<int?> restSeconds,
      Value<bool> skipped,
      Value<DateTime> loggedAt,
      Value<String> syncStatus,
      Value<int> rowid,
    });

class $$LocalExerciseLogsTableFilterComposer
    extends Composer<_$AppDatabase, $LocalExerciseLogsTable> {
  $$LocalExerciseLogsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get id => $composableBuilder(
    column: $table.id,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get workoutId => $composableBuilder(
    column: $table.workoutId,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get exerciseId => $composableBuilder(
    column: $table.exerciseId,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get clientId => $composableBuilder(
    column: $table.clientId,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get setNumber => $composableBuilder(
    column: $table.setNumber,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get reps => $composableBuilder(
    column: $table.reps,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<double> get weightKg => $composableBuilder(
    column: $table.weightKg,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get rpe => $composableBuilder(
    column: $table.rpe,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get restSeconds => $composableBuilder(
    column: $table.restSeconds,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<bool> get skipped => $composableBuilder(
    column: $table.skipped,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get loggedAt => $composableBuilder(
    column: $table.loggedAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get syncStatus => $composableBuilder(
    column: $table.syncStatus,
    builder: (column) => ColumnFilters(column),
  );
}

class $$LocalExerciseLogsTableOrderingComposer
    extends Composer<_$AppDatabase, $LocalExerciseLogsTable> {
  $$LocalExerciseLogsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get id => $composableBuilder(
    column: $table.id,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get workoutId => $composableBuilder(
    column: $table.workoutId,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get exerciseId => $composableBuilder(
    column: $table.exerciseId,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get clientId => $composableBuilder(
    column: $table.clientId,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get setNumber => $composableBuilder(
    column: $table.setNumber,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get reps => $composableBuilder(
    column: $table.reps,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<double> get weightKg => $composableBuilder(
    column: $table.weightKg,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get rpe => $composableBuilder(
    column: $table.rpe,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get restSeconds => $composableBuilder(
    column: $table.restSeconds,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<bool> get skipped => $composableBuilder(
    column: $table.skipped,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get loggedAt => $composableBuilder(
    column: $table.loggedAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get syncStatus => $composableBuilder(
    column: $table.syncStatus,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$LocalExerciseLogsTableAnnotationComposer
    extends Composer<_$AppDatabase, $LocalExerciseLogsTable> {
  $$LocalExerciseLogsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get workoutId =>
      $composableBuilder(column: $table.workoutId, builder: (column) => column);

  GeneratedColumn<String> get exerciseId => $composableBuilder(
    column: $table.exerciseId,
    builder: (column) => column,
  );

  GeneratedColumn<String> get clientId =>
      $composableBuilder(column: $table.clientId, builder: (column) => column);

  GeneratedColumn<int> get setNumber =>
      $composableBuilder(column: $table.setNumber, builder: (column) => column);

  GeneratedColumn<int> get reps =>
      $composableBuilder(column: $table.reps, builder: (column) => column);

  GeneratedColumn<double> get weightKg =>
      $composableBuilder(column: $table.weightKg, builder: (column) => column);

  GeneratedColumn<int> get rpe =>
      $composableBuilder(column: $table.rpe, builder: (column) => column);

  GeneratedColumn<int> get restSeconds => $composableBuilder(
    column: $table.restSeconds,
    builder: (column) => column,
  );

  GeneratedColumn<bool> get skipped =>
      $composableBuilder(column: $table.skipped, builder: (column) => column);

  GeneratedColumn<DateTime> get loggedAt =>
      $composableBuilder(column: $table.loggedAt, builder: (column) => column);

  GeneratedColumn<String> get syncStatus => $composableBuilder(
    column: $table.syncStatus,
    builder: (column) => column,
  );
}

class $$LocalExerciseLogsTableTableManager
    extends
        RootTableManager<
          _$AppDatabase,
          $LocalExerciseLogsTable,
          LocalExerciseLog,
          $$LocalExerciseLogsTableFilterComposer,
          $$LocalExerciseLogsTableOrderingComposer,
          $$LocalExerciseLogsTableAnnotationComposer,
          $$LocalExerciseLogsTableCreateCompanionBuilder,
          $$LocalExerciseLogsTableUpdateCompanionBuilder,
          (
            LocalExerciseLog,
            BaseReferences<
              _$AppDatabase,
              $LocalExerciseLogsTable,
              LocalExerciseLog
            >,
          ),
          LocalExerciseLog,
          PrefetchHooks Function()
        > {
  $$LocalExerciseLogsTableTableManager(
    _$AppDatabase db,
    $LocalExerciseLogsTable table,
  ) : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$LocalExerciseLogsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$LocalExerciseLogsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$LocalExerciseLogsTableAnnotationComposer(
                $db: db,
                $table: table,
              ),
          updateCompanionCallback:
              ({
                Value<String> id = const Value.absent(),
                Value<String> workoutId = const Value.absent(),
                Value<String> exerciseId = const Value.absent(),
                Value<String?> clientId = const Value.absent(),
                Value<int> setNumber = const Value.absent(),
                Value<int> reps = const Value.absent(),
                Value<double> weightKg = const Value.absent(),
                Value<int?> rpe = const Value.absent(),
                Value<int?> restSeconds = const Value.absent(),
                Value<bool> skipped = const Value.absent(),
                Value<DateTime> loggedAt = const Value.absent(),
                Value<String> syncStatus = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => LocalExerciseLogsCompanion(
                id: id,
                workoutId: workoutId,
                exerciseId: exerciseId,
                clientId: clientId,
                setNumber: setNumber,
                reps: reps,
                weightKg: weightKg,
                rpe: rpe,
                restSeconds: restSeconds,
                skipped: skipped,
                loggedAt: loggedAt,
                syncStatus: syncStatus,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String id,
                required String workoutId,
                required String exerciseId,
                Value<String?> clientId = const Value.absent(),
                required int setNumber,
                required int reps,
                required double weightKg,
                Value<int?> rpe = const Value.absent(),
                Value<int?> restSeconds = const Value.absent(),
                Value<bool> skipped = const Value.absent(),
                required DateTime loggedAt,
                Value<String> syncStatus = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => LocalExerciseLogsCompanion.insert(
                id: id,
                workoutId: workoutId,
                exerciseId: exerciseId,
                clientId: clientId,
                setNumber: setNumber,
                reps: reps,
                weightKg: weightKg,
                rpe: rpe,
                restSeconds: restSeconds,
                skipped: skipped,
                loggedAt: loggedAt,
                syncStatus: syncStatus,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$LocalExerciseLogsTableProcessedTableManager =
    ProcessedTableManager<
      _$AppDatabase,
      $LocalExerciseLogsTable,
      LocalExerciseLog,
      $$LocalExerciseLogsTableFilterComposer,
      $$LocalExerciseLogsTableOrderingComposer,
      $$LocalExerciseLogsTableAnnotationComposer,
      $$LocalExerciseLogsTableCreateCompanionBuilder,
      $$LocalExerciseLogsTableUpdateCompanionBuilder,
      (
        LocalExerciseLog,
        BaseReferences<
          _$AppDatabase,
          $LocalExerciseLogsTable,
          LocalExerciseLog
        >,
      ),
      LocalExerciseLog,
      PrefetchHooks Function()
    >;
typedef $$LocalInBodyMeasurementsTableCreateCompanionBuilder =
    LocalInBodyMeasurementsCompanion Function({
      required String id,
      required String userId,
      Value<String?> clientId,
      required DateTime measuredAt,
      required double weightKg,
      required double heightCm,
      required String sex,
      required double bodyFatPercent,
      Value<double?> muscleMassKg,
      Value<double?> bodyWaterPercent,
      Value<double?> proteinKg,
      Value<double?> mineralsKg,
      Value<int?> visceralFatLevel,
      Value<int?> bmrKcal,
      Value<double?> fatFreeMassKg,
      required double bmi,
      required String source,
      Value<String?> originalPdfKey,
      Value<String> syncStatus,
      required DateTime createdAt,
      Value<int> rowid,
    });
typedef $$LocalInBodyMeasurementsTableUpdateCompanionBuilder =
    LocalInBodyMeasurementsCompanion Function({
      Value<String> id,
      Value<String> userId,
      Value<String?> clientId,
      Value<DateTime> measuredAt,
      Value<double> weightKg,
      Value<double> heightCm,
      Value<String> sex,
      Value<double> bodyFatPercent,
      Value<double?> muscleMassKg,
      Value<double?> bodyWaterPercent,
      Value<double?> proteinKg,
      Value<double?> mineralsKg,
      Value<int?> visceralFatLevel,
      Value<int?> bmrKcal,
      Value<double?> fatFreeMassKg,
      Value<double> bmi,
      Value<String> source,
      Value<String?> originalPdfKey,
      Value<String> syncStatus,
      Value<DateTime> createdAt,
      Value<int> rowid,
    });

class $$LocalInBodyMeasurementsTableFilterComposer
    extends Composer<_$AppDatabase, $LocalInBodyMeasurementsTable> {
  $$LocalInBodyMeasurementsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get id => $composableBuilder(
    column: $table.id,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get userId => $composableBuilder(
    column: $table.userId,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get clientId => $composableBuilder(
    column: $table.clientId,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get measuredAt => $composableBuilder(
    column: $table.measuredAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<double> get weightKg => $composableBuilder(
    column: $table.weightKg,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<double> get heightCm => $composableBuilder(
    column: $table.heightCm,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get sex => $composableBuilder(
    column: $table.sex,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<double> get bodyFatPercent => $composableBuilder(
    column: $table.bodyFatPercent,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<double> get muscleMassKg => $composableBuilder(
    column: $table.muscleMassKg,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<double> get bodyWaterPercent => $composableBuilder(
    column: $table.bodyWaterPercent,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<double> get proteinKg => $composableBuilder(
    column: $table.proteinKg,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<double> get mineralsKg => $composableBuilder(
    column: $table.mineralsKg,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get visceralFatLevel => $composableBuilder(
    column: $table.visceralFatLevel,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get bmrKcal => $composableBuilder(
    column: $table.bmrKcal,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<double> get fatFreeMassKg => $composableBuilder(
    column: $table.fatFreeMassKg,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<double> get bmi => $composableBuilder(
    column: $table.bmi,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get source => $composableBuilder(
    column: $table.source,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get originalPdfKey => $composableBuilder(
    column: $table.originalPdfKey,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get syncStatus => $composableBuilder(
    column: $table.syncStatus,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
    column: $table.createdAt,
    builder: (column) => ColumnFilters(column),
  );
}

class $$LocalInBodyMeasurementsTableOrderingComposer
    extends Composer<_$AppDatabase, $LocalInBodyMeasurementsTable> {
  $$LocalInBodyMeasurementsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get id => $composableBuilder(
    column: $table.id,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get userId => $composableBuilder(
    column: $table.userId,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get clientId => $composableBuilder(
    column: $table.clientId,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get measuredAt => $composableBuilder(
    column: $table.measuredAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<double> get weightKg => $composableBuilder(
    column: $table.weightKg,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<double> get heightCm => $composableBuilder(
    column: $table.heightCm,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get sex => $composableBuilder(
    column: $table.sex,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<double> get bodyFatPercent => $composableBuilder(
    column: $table.bodyFatPercent,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<double> get muscleMassKg => $composableBuilder(
    column: $table.muscleMassKg,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<double> get bodyWaterPercent => $composableBuilder(
    column: $table.bodyWaterPercent,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<double> get proteinKg => $composableBuilder(
    column: $table.proteinKg,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<double> get mineralsKg => $composableBuilder(
    column: $table.mineralsKg,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get visceralFatLevel => $composableBuilder(
    column: $table.visceralFatLevel,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get bmrKcal => $composableBuilder(
    column: $table.bmrKcal,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<double> get fatFreeMassKg => $composableBuilder(
    column: $table.fatFreeMassKg,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<double> get bmi => $composableBuilder(
    column: $table.bmi,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get source => $composableBuilder(
    column: $table.source,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get originalPdfKey => $composableBuilder(
    column: $table.originalPdfKey,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get syncStatus => $composableBuilder(
    column: $table.syncStatus,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
    column: $table.createdAt,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$LocalInBodyMeasurementsTableAnnotationComposer
    extends Composer<_$AppDatabase, $LocalInBodyMeasurementsTable> {
  $$LocalInBodyMeasurementsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get userId =>
      $composableBuilder(column: $table.userId, builder: (column) => column);

  GeneratedColumn<String> get clientId =>
      $composableBuilder(column: $table.clientId, builder: (column) => column);

  GeneratedColumn<DateTime> get measuredAt => $composableBuilder(
    column: $table.measuredAt,
    builder: (column) => column,
  );

  GeneratedColumn<double> get weightKg =>
      $composableBuilder(column: $table.weightKg, builder: (column) => column);

  GeneratedColumn<double> get heightCm =>
      $composableBuilder(column: $table.heightCm, builder: (column) => column);

  GeneratedColumn<String> get sex =>
      $composableBuilder(column: $table.sex, builder: (column) => column);

  GeneratedColumn<double> get bodyFatPercent => $composableBuilder(
    column: $table.bodyFatPercent,
    builder: (column) => column,
  );

  GeneratedColumn<double> get muscleMassKg => $composableBuilder(
    column: $table.muscleMassKg,
    builder: (column) => column,
  );

  GeneratedColumn<double> get bodyWaterPercent => $composableBuilder(
    column: $table.bodyWaterPercent,
    builder: (column) => column,
  );

  GeneratedColumn<double> get proteinKg =>
      $composableBuilder(column: $table.proteinKg, builder: (column) => column);

  GeneratedColumn<double> get mineralsKg => $composableBuilder(
    column: $table.mineralsKg,
    builder: (column) => column,
  );

  GeneratedColumn<int> get visceralFatLevel => $composableBuilder(
    column: $table.visceralFatLevel,
    builder: (column) => column,
  );

  GeneratedColumn<int> get bmrKcal =>
      $composableBuilder(column: $table.bmrKcal, builder: (column) => column);

  GeneratedColumn<double> get fatFreeMassKg => $composableBuilder(
    column: $table.fatFreeMassKg,
    builder: (column) => column,
  );

  GeneratedColumn<double> get bmi =>
      $composableBuilder(column: $table.bmi, builder: (column) => column);

  GeneratedColumn<String> get source =>
      $composableBuilder(column: $table.source, builder: (column) => column);

  GeneratedColumn<String> get originalPdfKey => $composableBuilder(
    column: $table.originalPdfKey,
    builder: (column) => column,
  );

  GeneratedColumn<String> get syncStatus => $composableBuilder(
    column: $table.syncStatus,
    builder: (column) => column,
  );

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);
}

class $$LocalInBodyMeasurementsTableTableManager
    extends
        RootTableManager<
          _$AppDatabase,
          $LocalInBodyMeasurementsTable,
          LocalInBodyMeasurement,
          $$LocalInBodyMeasurementsTableFilterComposer,
          $$LocalInBodyMeasurementsTableOrderingComposer,
          $$LocalInBodyMeasurementsTableAnnotationComposer,
          $$LocalInBodyMeasurementsTableCreateCompanionBuilder,
          $$LocalInBodyMeasurementsTableUpdateCompanionBuilder,
          (
            LocalInBodyMeasurement,
            BaseReferences<
              _$AppDatabase,
              $LocalInBodyMeasurementsTable,
              LocalInBodyMeasurement
            >,
          ),
          LocalInBodyMeasurement,
          PrefetchHooks Function()
        > {
  $$LocalInBodyMeasurementsTableTableManager(
    _$AppDatabase db,
    $LocalInBodyMeasurementsTable table,
  ) : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$LocalInBodyMeasurementsTableFilterComposer(
                $db: db,
                $table: table,
              ),
          createOrderingComposer: () =>
              $$LocalInBodyMeasurementsTableOrderingComposer(
                $db: db,
                $table: table,
              ),
          createComputedFieldComposer: () =>
              $$LocalInBodyMeasurementsTableAnnotationComposer(
                $db: db,
                $table: table,
              ),
          updateCompanionCallback:
              ({
                Value<String> id = const Value.absent(),
                Value<String> userId = const Value.absent(),
                Value<String?> clientId = const Value.absent(),
                Value<DateTime> measuredAt = const Value.absent(),
                Value<double> weightKg = const Value.absent(),
                Value<double> heightCm = const Value.absent(),
                Value<String> sex = const Value.absent(),
                Value<double> bodyFatPercent = const Value.absent(),
                Value<double?> muscleMassKg = const Value.absent(),
                Value<double?> bodyWaterPercent = const Value.absent(),
                Value<double?> proteinKg = const Value.absent(),
                Value<double?> mineralsKg = const Value.absent(),
                Value<int?> visceralFatLevel = const Value.absent(),
                Value<int?> bmrKcal = const Value.absent(),
                Value<double?> fatFreeMassKg = const Value.absent(),
                Value<double> bmi = const Value.absent(),
                Value<String> source = const Value.absent(),
                Value<String?> originalPdfKey = const Value.absent(),
                Value<String> syncStatus = const Value.absent(),
                Value<DateTime> createdAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => LocalInBodyMeasurementsCompanion(
                id: id,
                userId: userId,
                clientId: clientId,
                measuredAt: measuredAt,
                weightKg: weightKg,
                heightCm: heightCm,
                sex: sex,
                bodyFatPercent: bodyFatPercent,
                muscleMassKg: muscleMassKg,
                bodyWaterPercent: bodyWaterPercent,
                proteinKg: proteinKg,
                mineralsKg: mineralsKg,
                visceralFatLevel: visceralFatLevel,
                bmrKcal: bmrKcal,
                fatFreeMassKg: fatFreeMassKg,
                bmi: bmi,
                source: source,
                originalPdfKey: originalPdfKey,
                syncStatus: syncStatus,
                createdAt: createdAt,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String id,
                required String userId,
                Value<String?> clientId = const Value.absent(),
                required DateTime measuredAt,
                required double weightKg,
                required double heightCm,
                required String sex,
                required double bodyFatPercent,
                Value<double?> muscleMassKg = const Value.absent(),
                Value<double?> bodyWaterPercent = const Value.absent(),
                Value<double?> proteinKg = const Value.absent(),
                Value<double?> mineralsKg = const Value.absent(),
                Value<int?> visceralFatLevel = const Value.absent(),
                Value<int?> bmrKcal = const Value.absent(),
                Value<double?> fatFreeMassKg = const Value.absent(),
                required double bmi,
                required String source,
                Value<String?> originalPdfKey = const Value.absent(),
                Value<String> syncStatus = const Value.absent(),
                required DateTime createdAt,
                Value<int> rowid = const Value.absent(),
              }) => LocalInBodyMeasurementsCompanion.insert(
                id: id,
                userId: userId,
                clientId: clientId,
                measuredAt: measuredAt,
                weightKg: weightKg,
                heightCm: heightCm,
                sex: sex,
                bodyFatPercent: bodyFatPercent,
                muscleMassKg: muscleMassKg,
                bodyWaterPercent: bodyWaterPercent,
                proteinKg: proteinKg,
                mineralsKg: mineralsKg,
                visceralFatLevel: visceralFatLevel,
                bmrKcal: bmrKcal,
                fatFreeMassKg: fatFreeMassKg,
                bmi: bmi,
                source: source,
                originalPdfKey: originalPdfKey,
                syncStatus: syncStatus,
                createdAt: createdAt,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$LocalInBodyMeasurementsTableProcessedTableManager =
    ProcessedTableManager<
      _$AppDatabase,
      $LocalInBodyMeasurementsTable,
      LocalInBodyMeasurement,
      $$LocalInBodyMeasurementsTableFilterComposer,
      $$LocalInBodyMeasurementsTableOrderingComposer,
      $$LocalInBodyMeasurementsTableAnnotationComposer,
      $$LocalInBodyMeasurementsTableCreateCompanionBuilder,
      $$LocalInBodyMeasurementsTableUpdateCompanionBuilder,
      (
        LocalInBodyMeasurement,
        BaseReferences<
          _$AppDatabase,
          $LocalInBodyMeasurementsTable,
          LocalInBodyMeasurement
        >,
      ),
      LocalInBodyMeasurement,
      PrefetchHooks Function()
    >;
typedef $$LocalPlansTableCreateCompanionBuilder =
    LocalPlansCompanion Function({
      required String id,
      required String userId,
      required String status,
      required String goal,
      Value<int?> trainingFrequency,
      required DateTime validFrom,
      required DateTime validUntil,
      required String payloadJson,
      Value<DateTime> fetchedAt,
      Value<int> rowid,
    });
typedef $$LocalPlansTableUpdateCompanionBuilder =
    LocalPlansCompanion Function({
      Value<String> id,
      Value<String> userId,
      Value<String> status,
      Value<String> goal,
      Value<int?> trainingFrequency,
      Value<DateTime> validFrom,
      Value<DateTime> validUntil,
      Value<String> payloadJson,
      Value<DateTime> fetchedAt,
      Value<int> rowid,
    });

class $$LocalPlansTableFilterComposer
    extends Composer<_$AppDatabase, $LocalPlansTable> {
  $$LocalPlansTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get id => $composableBuilder(
    column: $table.id,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get userId => $composableBuilder(
    column: $table.userId,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get status => $composableBuilder(
    column: $table.status,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get goal => $composableBuilder(
    column: $table.goal,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get trainingFrequency => $composableBuilder(
    column: $table.trainingFrequency,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get validFrom => $composableBuilder(
    column: $table.validFrom,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get validUntil => $composableBuilder(
    column: $table.validUntil,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get payloadJson => $composableBuilder(
    column: $table.payloadJson,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get fetchedAt => $composableBuilder(
    column: $table.fetchedAt,
    builder: (column) => ColumnFilters(column),
  );
}

class $$LocalPlansTableOrderingComposer
    extends Composer<_$AppDatabase, $LocalPlansTable> {
  $$LocalPlansTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get id => $composableBuilder(
    column: $table.id,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get userId => $composableBuilder(
    column: $table.userId,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get status => $composableBuilder(
    column: $table.status,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get goal => $composableBuilder(
    column: $table.goal,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get trainingFrequency => $composableBuilder(
    column: $table.trainingFrequency,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get validFrom => $composableBuilder(
    column: $table.validFrom,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get validUntil => $composableBuilder(
    column: $table.validUntil,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get payloadJson => $composableBuilder(
    column: $table.payloadJson,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get fetchedAt => $composableBuilder(
    column: $table.fetchedAt,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$LocalPlansTableAnnotationComposer
    extends Composer<_$AppDatabase, $LocalPlansTable> {
  $$LocalPlansTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get userId =>
      $composableBuilder(column: $table.userId, builder: (column) => column);

  GeneratedColumn<String> get status =>
      $composableBuilder(column: $table.status, builder: (column) => column);

  GeneratedColumn<String> get goal =>
      $composableBuilder(column: $table.goal, builder: (column) => column);

  GeneratedColumn<int> get trainingFrequency => $composableBuilder(
    column: $table.trainingFrequency,
    builder: (column) => column,
  );

  GeneratedColumn<DateTime> get validFrom =>
      $composableBuilder(column: $table.validFrom, builder: (column) => column);

  GeneratedColumn<DateTime> get validUntil => $composableBuilder(
    column: $table.validUntil,
    builder: (column) => column,
  );

  GeneratedColumn<String> get payloadJson => $composableBuilder(
    column: $table.payloadJson,
    builder: (column) => column,
  );

  GeneratedColumn<DateTime> get fetchedAt =>
      $composableBuilder(column: $table.fetchedAt, builder: (column) => column);
}

class $$LocalPlansTableTableManager
    extends
        RootTableManager<
          _$AppDatabase,
          $LocalPlansTable,
          LocalPlan,
          $$LocalPlansTableFilterComposer,
          $$LocalPlansTableOrderingComposer,
          $$LocalPlansTableAnnotationComposer,
          $$LocalPlansTableCreateCompanionBuilder,
          $$LocalPlansTableUpdateCompanionBuilder,
          (
            LocalPlan,
            BaseReferences<_$AppDatabase, $LocalPlansTable, LocalPlan>,
          ),
          LocalPlan,
          PrefetchHooks Function()
        > {
  $$LocalPlansTableTableManager(_$AppDatabase db, $LocalPlansTable table)
    : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$LocalPlansTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$LocalPlansTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$LocalPlansTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback:
              ({
                Value<String> id = const Value.absent(),
                Value<String> userId = const Value.absent(),
                Value<String> status = const Value.absent(),
                Value<String> goal = const Value.absent(),
                Value<int?> trainingFrequency = const Value.absent(),
                Value<DateTime> validFrom = const Value.absent(),
                Value<DateTime> validUntil = const Value.absent(),
                Value<String> payloadJson = const Value.absent(),
                Value<DateTime> fetchedAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => LocalPlansCompanion(
                id: id,
                userId: userId,
                status: status,
                goal: goal,
                trainingFrequency: trainingFrequency,
                validFrom: validFrom,
                validUntil: validUntil,
                payloadJson: payloadJson,
                fetchedAt: fetchedAt,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String id,
                required String userId,
                required String status,
                required String goal,
                Value<int?> trainingFrequency = const Value.absent(),
                required DateTime validFrom,
                required DateTime validUntil,
                required String payloadJson,
                Value<DateTime> fetchedAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => LocalPlansCompanion.insert(
                id: id,
                userId: userId,
                status: status,
                goal: goal,
                trainingFrequency: trainingFrequency,
                validFrom: validFrom,
                validUntil: validUntil,
                payloadJson: payloadJson,
                fetchedAt: fetchedAt,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$LocalPlansTableProcessedTableManager =
    ProcessedTableManager<
      _$AppDatabase,
      $LocalPlansTable,
      LocalPlan,
      $$LocalPlansTableFilterComposer,
      $$LocalPlansTableOrderingComposer,
      $$LocalPlansTableAnnotationComposer,
      $$LocalPlansTableCreateCompanionBuilder,
      $$LocalPlansTableUpdateCompanionBuilder,
      (LocalPlan, BaseReferences<_$AppDatabase, $LocalPlansTable, LocalPlan>),
      LocalPlan,
      PrefetchHooks Function()
    >;
typedef $$LocalForecastsTableCreateCompanionBuilder =
    LocalForecastsCompanion Function({
      required String userId,
      required String modelVersion,
      required String confidence,
      required bool fallback,
      required DateTime generatedAt,
      required String payloadJson,
      Value<DateTime> fetchedAt,
      Value<int> rowid,
    });
typedef $$LocalForecastsTableUpdateCompanionBuilder =
    LocalForecastsCompanion Function({
      Value<String> userId,
      Value<String> modelVersion,
      Value<String> confidence,
      Value<bool> fallback,
      Value<DateTime> generatedAt,
      Value<String> payloadJson,
      Value<DateTime> fetchedAt,
      Value<int> rowid,
    });

class $$LocalForecastsTableFilterComposer
    extends Composer<_$AppDatabase, $LocalForecastsTable> {
  $$LocalForecastsTableFilterComposer({
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

  ColumnFilters<String> get modelVersion => $composableBuilder(
    column: $table.modelVersion,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get confidence => $composableBuilder(
    column: $table.confidence,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<bool> get fallback => $composableBuilder(
    column: $table.fallback,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get generatedAt => $composableBuilder(
    column: $table.generatedAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get payloadJson => $composableBuilder(
    column: $table.payloadJson,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get fetchedAt => $composableBuilder(
    column: $table.fetchedAt,
    builder: (column) => ColumnFilters(column),
  );
}

class $$LocalForecastsTableOrderingComposer
    extends Composer<_$AppDatabase, $LocalForecastsTable> {
  $$LocalForecastsTableOrderingComposer({
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

  ColumnOrderings<String> get modelVersion => $composableBuilder(
    column: $table.modelVersion,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get confidence => $composableBuilder(
    column: $table.confidence,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<bool> get fallback => $composableBuilder(
    column: $table.fallback,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get generatedAt => $composableBuilder(
    column: $table.generatedAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get payloadJson => $composableBuilder(
    column: $table.payloadJson,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get fetchedAt => $composableBuilder(
    column: $table.fetchedAt,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$LocalForecastsTableAnnotationComposer
    extends Composer<_$AppDatabase, $LocalForecastsTable> {
  $$LocalForecastsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get userId =>
      $composableBuilder(column: $table.userId, builder: (column) => column);

  GeneratedColumn<String> get modelVersion => $composableBuilder(
    column: $table.modelVersion,
    builder: (column) => column,
  );

  GeneratedColumn<String> get confidence => $composableBuilder(
    column: $table.confidence,
    builder: (column) => column,
  );

  GeneratedColumn<bool> get fallback =>
      $composableBuilder(column: $table.fallback, builder: (column) => column);

  GeneratedColumn<DateTime> get generatedAt => $composableBuilder(
    column: $table.generatedAt,
    builder: (column) => column,
  );

  GeneratedColumn<String> get payloadJson => $composableBuilder(
    column: $table.payloadJson,
    builder: (column) => column,
  );

  GeneratedColumn<DateTime> get fetchedAt =>
      $composableBuilder(column: $table.fetchedAt, builder: (column) => column);
}

class $$LocalForecastsTableTableManager
    extends
        RootTableManager<
          _$AppDatabase,
          $LocalForecastsTable,
          LocalForecast,
          $$LocalForecastsTableFilterComposer,
          $$LocalForecastsTableOrderingComposer,
          $$LocalForecastsTableAnnotationComposer,
          $$LocalForecastsTableCreateCompanionBuilder,
          $$LocalForecastsTableUpdateCompanionBuilder,
          (
            LocalForecast,
            BaseReferences<_$AppDatabase, $LocalForecastsTable, LocalForecast>,
          ),
          LocalForecast,
          PrefetchHooks Function()
        > {
  $$LocalForecastsTableTableManager(
    _$AppDatabase db,
    $LocalForecastsTable table,
  ) : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$LocalForecastsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$LocalForecastsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$LocalForecastsTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback:
              ({
                Value<String> userId = const Value.absent(),
                Value<String> modelVersion = const Value.absent(),
                Value<String> confidence = const Value.absent(),
                Value<bool> fallback = const Value.absent(),
                Value<DateTime> generatedAt = const Value.absent(),
                Value<String> payloadJson = const Value.absent(),
                Value<DateTime> fetchedAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => LocalForecastsCompanion(
                userId: userId,
                modelVersion: modelVersion,
                confidence: confidence,
                fallback: fallback,
                generatedAt: generatedAt,
                payloadJson: payloadJson,
                fetchedAt: fetchedAt,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String userId,
                required String modelVersion,
                required String confidence,
                required bool fallback,
                required DateTime generatedAt,
                required String payloadJson,
                Value<DateTime> fetchedAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => LocalForecastsCompanion.insert(
                userId: userId,
                modelVersion: modelVersion,
                confidence: confidence,
                fallback: fallback,
                generatedAt: generatedAt,
                payloadJson: payloadJson,
                fetchedAt: fetchedAt,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$LocalForecastsTableProcessedTableManager =
    ProcessedTableManager<
      _$AppDatabase,
      $LocalForecastsTable,
      LocalForecast,
      $$LocalForecastsTableFilterComposer,
      $$LocalForecastsTableOrderingComposer,
      $$LocalForecastsTableAnnotationComposer,
      $$LocalForecastsTableCreateCompanionBuilder,
      $$LocalForecastsTableUpdateCompanionBuilder,
      (
        LocalForecast,
        BaseReferences<_$AppDatabase, $LocalForecastsTable, LocalForecast>,
      ),
      LocalForecast,
      PrefetchHooks Function()
    >;
typedef $$LocalExercisesTableCreateCompanionBuilder =
    LocalExercisesCompanion Function({
      required String id,
      required String exerciseId,
      required String exerciseName,
      Value<String?> exerciseNameRu,
      required String primaryMuscleGroup,
      Value<String> secondaryMuscleGroupJson,
      Value<String> equipmentJson,
      required String bodyRegion,
      Value<int> version,
      Value<DateTime> fetchedAt,
      Value<int> rowid,
    });
typedef $$LocalExercisesTableUpdateCompanionBuilder =
    LocalExercisesCompanion Function({
      Value<String> id,
      Value<String> exerciseId,
      Value<String> exerciseName,
      Value<String?> exerciseNameRu,
      Value<String> primaryMuscleGroup,
      Value<String> secondaryMuscleGroupJson,
      Value<String> equipmentJson,
      Value<String> bodyRegion,
      Value<int> version,
      Value<DateTime> fetchedAt,
      Value<int> rowid,
    });

class $$LocalExercisesTableFilterComposer
    extends Composer<_$AppDatabase, $LocalExercisesTable> {
  $$LocalExercisesTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get id => $composableBuilder(
    column: $table.id,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get exerciseId => $composableBuilder(
    column: $table.exerciseId,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get exerciseName => $composableBuilder(
    column: $table.exerciseName,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get exerciseNameRu => $composableBuilder(
    column: $table.exerciseNameRu,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get primaryMuscleGroup => $composableBuilder(
    column: $table.primaryMuscleGroup,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get secondaryMuscleGroupJson => $composableBuilder(
    column: $table.secondaryMuscleGroupJson,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get equipmentJson => $composableBuilder(
    column: $table.equipmentJson,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get bodyRegion => $composableBuilder(
    column: $table.bodyRegion,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get version => $composableBuilder(
    column: $table.version,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get fetchedAt => $composableBuilder(
    column: $table.fetchedAt,
    builder: (column) => ColumnFilters(column),
  );
}

class $$LocalExercisesTableOrderingComposer
    extends Composer<_$AppDatabase, $LocalExercisesTable> {
  $$LocalExercisesTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get id => $composableBuilder(
    column: $table.id,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get exerciseId => $composableBuilder(
    column: $table.exerciseId,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get exerciseName => $composableBuilder(
    column: $table.exerciseName,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get exerciseNameRu => $composableBuilder(
    column: $table.exerciseNameRu,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get primaryMuscleGroup => $composableBuilder(
    column: $table.primaryMuscleGroup,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get secondaryMuscleGroupJson => $composableBuilder(
    column: $table.secondaryMuscleGroupJson,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get equipmentJson => $composableBuilder(
    column: $table.equipmentJson,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get bodyRegion => $composableBuilder(
    column: $table.bodyRegion,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get version => $composableBuilder(
    column: $table.version,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get fetchedAt => $composableBuilder(
    column: $table.fetchedAt,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$LocalExercisesTableAnnotationComposer
    extends Composer<_$AppDatabase, $LocalExercisesTable> {
  $$LocalExercisesTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get exerciseId => $composableBuilder(
    column: $table.exerciseId,
    builder: (column) => column,
  );

  GeneratedColumn<String> get exerciseName => $composableBuilder(
    column: $table.exerciseName,
    builder: (column) => column,
  );

  GeneratedColumn<String> get exerciseNameRu => $composableBuilder(
    column: $table.exerciseNameRu,
    builder: (column) => column,
  );

  GeneratedColumn<String> get primaryMuscleGroup => $composableBuilder(
    column: $table.primaryMuscleGroup,
    builder: (column) => column,
  );

  GeneratedColumn<String> get secondaryMuscleGroupJson => $composableBuilder(
    column: $table.secondaryMuscleGroupJson,
    builder: (column) => column,
  );

  GeneratedColumn<String> get equipmentJson => $composableBuilder(
    column: $table.equipmentJson,
    builder: (column) => column,
  );

  GeneratedColumn<String> get bodyRegion => $composableBuilder(
    column: $table.bodyRegion,
    builder: (column) => column,
  );

  GeneratedColumn<int> get version =>
      $composableBuilder(column: $table.version, builder: (column) => column);

  GeneratedColumn<DateTime> get fetchedAt =>
      $composableBuilder(column: $table.fetchedAt, builder: (column) => column);
}

class $$LocalExercisesTableTableManager
    extends
        RootTableManager<
          _$AppDatabase,
          $LocalExercisesTable,
          LocalExercise,
          $$LocalExercisesTableFilterComposer,
          $$LocalExercisesTableOrderingComposer,
          $$LocalExercisesTableAnnotationComposer,
          $$LocalExercisesTableCreateCompanionBuilder,
          $$LocalExercisesTableUpdateCompanionBuilder,
          (
            LocalExercise,
            BaseReferences<_$AppDatabase, $LocalExercisesTable, LocalExercise>,
          ),
          LocalExercise,
          PrefetchHooks Function()
        > {
  $$LocalExercisesTableTableManager(
    _$AppDatabase db,
    $LocalExercisesTable table,
  ) : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$LocalExercisesTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$LocalExercisesTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$LocalExercisesTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback:
              ({
                Value<String> id = const Value.absent(),
                Value<String> exerciseId = const Value.absent(),
                Value<String> exerciseName = const Value.absent(),
                Value<String?> exerciseNameRu = const Value.absent(),
                Value<String> primaryMuscleGroup = const Value.absent(),
                Value<String> secondaryMuscleGroupJson = const Value.absent(),
                Value<String> equipmentJson = const Value.absent(),
                Value<String> bodyRegion = const Value.absent(),
                Value<int> version = const Value.absent(),
                Value<DateTime> fetchedAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => LocalExercisesCompanion(
                id: id,
                exerciseId: exerciseId,
                exerciseName: exerciseName,
                exerciseNameRu: exerciseNameRu,
                primaryMuscleGroup: primaryMuscleGroup,
                secondaryMuscleGroupJson: secondaryMuscleGroupJson,
                equipmentJson: equipmentJson,
                bodyRegion: bodyRegion,
                version: version,
                fetchedAt: fetchedAt,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String id,
                required String exerciseId,
                required String exerciseName,
                Value<String?> exerciseNameRu = const Value.absent(),
                required String primaryMuscleGroup,
                Value<String> secondaryMuscleGroupJson = const Value.absent(),
                Value<String> equipmentJson = const Value.absent(),
                required String bodyRegion,
                Value<int> version = const Value.absent(),
                Value<DateTime> fetchedAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => LocalExercisesCompanion.insert(
                id: id,
                exerciseId: exerciseId,
                exerciseName: exerciseName,
                exerciseNameRu: exerciseNameRu,
                primaryMuscleGroup: primaryMuscleGroup,
                secondaryMuscleGroupJson: secondaryMuscleGroupJson,
                equipmentJson: equipmentJson,
                bodyRegion: bodyRegion,
                version: version,
                fetchedAt: fetchedAt,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$LocalExercisesTableProcessedTableManager =
    ProcessedTableManager<
      _$AppDatabase,
      $LocalExercisesTable,
      LocalExercise,
      $$LocalExercisesTableFilterComposer,
      $$LocalExercisesTableOrderingComposer,
      $$LocalExercisesTableAnnotationComposer,
      $$LocalExercisesTableCreateCompanionBuilder,
      $$LocalExercisesTableUpdateCompanionBuilder,
      (
        LocalExercise,
        BaseReferences<_$AppDatabase, $LocalExercisesTable, LocalExercise>,
      ),
      LocalExercise,
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
  $$LocalWorkoutsTableTableManager get localWorkouts =>
      $$LocalWorkoutsTableTableManager(_db, _db.localWorkouts);
  $$LocalExerciseLogsTableTableManager get localExerciseLogs =>
      $$LocalExerciseLogsTableTableManager(_db, _db.localExerciseLogs);
  $$LocalInBodyMeasurementsTableTableManager get localInBodyMeasurements =>
      $$LocalInBodyMeasurementsTableTableManager(
        _db,
        _db.localInBodyMeasurements,
      );
  $$LocalPlansTableTableManager get localPlans =>
      $$LocalPlansTableTableManager(_db, _db.localPlans);
  $$LocalForecastsTableTableManager get localForecasts =>
      $$LocalForecastsTableTableManager(_db, _db.localForecasts);
  $$LocalExercisesTableTableManager get localExercises =>
      $$LocalExercisesTableTableManager(_db, _db.localExercises);
  $$SyncQueueTableTableManager get syncQueue =>
      $$SyncQueueTableTableManager(_db, _db.syncQueue);
}
