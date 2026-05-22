"""Чистка каталога упражнений: удаление пустых переводов и дублей.

В исходном JSON-каталоге (0016_seed_full_catalog) из 873 упражнений
оказалось 296 с пустым русским названием и 221 дубль по name_ru
(например, «Приседания» встречалось 17 раз, «Жим» — 14 раз, потому
что Wide/Narrow/Front/Back-варианты переводились одинаково).

Эта миграция удаляет 517 проблемных записей по их exercise_id. JSON
уже почищен — в репо лежит cleaned-версия из 356 уникальных упражнений
(см. ml/data/processed/exercises_catalog_ru.original.json для отката).

12 fixture'ов из 0004_seed_exercises (slug'и `barbell_squat` и т.п.)
не затрагиваются — они с другими ID и нужны для integration-тестов.

FK на exercises.id стоят ondelete RESTRICT — в dev-окружении без
реальных юзеров DELETE проходит чисто. На проде же часть удаляемых
упражнений уже захватили в свои планы реальные пользователи
(plan_exercises.exercise_id → exercises.id), поэтому миграция
выполняется идемпотентно: удаляются только те ID, на которые нет
FK-ссылок; остальные остаются в каталоге как «исторические»
(пользователю в UI они не предлагаются — фронт берёт каталог из
JSON, а БД-каталог нужен только как справочник для plan_exercises).

Revision ID: 0020_clean_exercise_catalog
Revises: 0019_profile_equipment_available
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
from sqlalchemy import text

revision: str = "0020_clean_exercise_catalog"
# Заодно merge'имся с 0017_merge_heads — после этого history линейная.
down_revision: str | Sequence[str] | None = (
    "0019_profile_equipment",
    "0017_merge_heads",
)
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


REMOVED_IDS: tuple[str, ...] = (
    '90_90_hamstring', 'ab_roller', 'adductor', 'adductor_groin', 'advanced_kettlebell_windmill', 'air_bike',
    'all_fours_quad_stretch', 'alternate_heel_touchers', 'alternate_leg_diagonal_bound', 'ankle_circles', 'ankle_on_the_knee', 'anterior_tibialis_smr',
    'arm_circles', 'around_the_worlds', 'atlas_stone_trainer', 'atlas_stones', 'backward_drag', 'balance_board',
    'band_hip_adductions', 'band_skull_crusher', 'barbell_ab_rollout', 'barbell_ab_rollout_on_knees', 'barbell_glute_bridge', 'barbell_hip_thrust',
    'barbell_rollout_from_bench', 'barbell_side_bend', 'battling_ropes', 'bear_crawl_sled_drags', 'behind_head_chest_stretch', 'bench_jump',
    'bench_sprint', 'body_up', 'bottoms_up', 'box_jump_multiple_response', 'box_skip', 'brachialis_smr',
    'butt_lift_bridge', 'butt_ups', 'cable_hip_adduction', 'cable_incline_pushdown', 'cable_internal_rotation', 'cable_iron_cross',
    'cable_judo_flip', 'calf_stretch_elbows_against_wall', 'calf_stretch_hands_against_wall', 'calves_smr', 'car_drivers', 'carioca_quick_step',
    'cat_stretch', 'chair_leg_extended_stretch', 'chair_lower_back_stretch', 'chair_upper_body_stretch', 'chest_and_front_of_shoulder_stretch', 'chest_push_multiple_response',
    'chest_push_single_response', 'chest_push_from_3_point_stance', 'chest_push_with_run_release', 'chest_stretch_on_stability_ball', 'child_s_pose', 'chin_to_chest_stretch',
    'circus_bell', 'cocoons', 'conan_s_wheel', 'cross_over_with_bands', 'crucifix', 'dancer_s_stretch',
    'dead_bug', 'decline_close_grip_bench_to_skull_crusher', 'depth_jump_leap', 'double_kettlebell_jerk', 'double_kettlebell_windmill', 'double_leg_butt_kick',
    'downward_facing_balance', 'drop_push', 'dumbbell_lying_pronation', 'dumbbell_lying_supination', 'dumbbell_scaption', 'dumbbell_seated_box_jump',
    'dumbbell_side_bend', 'dynamic_back_stretch', 'dynamic_chest_stretch', 'ez_bar_skullcrusher', 'elbow_circles', 'elbow_to_knee',
    'elbows_back', 'elliptical_trainer', 'external_rotation', 'external_rotation_with_band', 'external_rotation_with_cable', 'farmer_s_walk',
    'fast_skipping', 'flutter_kicks', 'foot_smr', 'frog_hops', 'front_box_jump', 'front_cone_hops_or_hurdle_hops',
    'gironda_sternum_chins', 'groin_and_back_stretch', 'groiners', 'hamstring_stretch', 'hamstring_smr', 'hanging_pike',
    'heavy_bag_thrust', 'hip_circles_prone', 'hip_flexion_with_band', 'hip_lift_with_band', 'hug_a_ball', 'hug_knees_to_chest',
    'hurdle_hops', 'it_band_and_glute_stretch', 'iliotibial_tract_smr', 'inchworm', 'incline_dumbbell_bench_with_palms_facing_in', 'intermediate_groin_stretch',
    'intermediate_hip_flexor_and_quad_stretch', 'internal_rotation_with_band', 'iron_cross', 'iron_crosses_stretch', 'isometric_chest_squeezes', 'isometric_neck_exercise_front_and_back',
    'isometric_neck_exercise_sides', 'isometric_wipers', 'jerk_balance', 'jogging_treadmill', 'keg_load', 'kettlebell_figure_8',
    'kettlebell_pass_between_the_legs', 'kettlebell_pirate_ships', 'kettlebell_windmill', 'kipping_muscle_up', 'knee_across_the_body', 'knee_circles',
    'knee_tuck_jump', 'kneeling_arm_drill', 'kneeling_forearm_stretch', 'kneeling_hip_flexor', 'landmine_180_s', 'landmine_linear_jammer',
    'lateral_bound', 'lateral_box_jump', 'lateral_cone_hops', 'latissimus_dorsi_smr', 'leg_lift', 'leg_up_hamstring_stretch',
    'linear_3_part_start_technique', 'linear_acceleration_wall_drill', 'linear_depth_jump', 'log_lift', 'london_bridges', 'looking_at_ceiling',
    'lower_back_smr', 'lying_bent_leg_groin', 'lying_face_down_plate_neck_resistance', 'lying_face_up_plate_neck_resistance', 'lying_glute', 'lying_hamstring',
    'lying_prone_quadriceps', 'medicine_ball_chest_pass', 'middle_back_stretch', 'mixed_grip_chin', 'monster_walk', 'mountain_climbers',
    'moving_claw_series', 'muscle_up', 'neck_smr', 'on_your_side_quad_stretch', 'on_your_back_quad_stretch', 'one_arm_against_wall',
    'one_half_locust', 'one_handed_hang', 'one_knee_to_chest', 'one_arm_kettlebell_jerk', 'one_arm_kettlebell_split_jerk', 'one_arm_medicine_ball_slam',
    'one_arm_side_laterals', 'otis_up', 'overhead_lat', 'overhead_slam', 'overhead_stretch', 'overhead_triceps',
    'pelvic_tilt_into_bridge', 'peroneals_stretch', 'peroneals_smr', 'physioball_hip_bridge', 'piriformis_smr', 'plate_pinch',
    'platform_hamstring_slides', 'plyo_kettlebell_pushups', 'posterior_tibialis_stretch', 'power_jerk', 'power_partials', 'power_stairs',
    'prone_manual_hamstring', 'pushups', 'pushups_close_and_wide_hand_positions', 'pyramid', 'quad_stretch', 'quadriceps_smr',
    'quick_leap', 'rack_delivery', 'recumbent_bike', 'return_push_from_stance', 'reverse_grip_triceps_pushdown', 'rhomboids_smr',
    'rickshaw_carry', 'rocket_jump', 'rope_climb', 'rope_jumping', 'round_the_world_shoulder_stretch', 'runner_s_stretch',
    'sandbag_load', 'scissor_kick', 'scissors_jump', 'seated_biceps', 'seated_calf_stretch', 'seated_floor_hamstring_stretch',
    'seated_front_deltoid', 'seated_glute', 'seated_hamstring', 'seated_hamstring_and_calf_stretch', 'seated_head_harness_neck_resistance', 'seated_leg_tucks',
    'seated_overhead_stretch', 'shoulder_circles', 'shoulder_stretch', 'side_bridge', 'side_hop_sprint', 'side_jackknife',
    'side_lying_groin_stretch', 'side_neck_stretch', 'side_standing_long_jump', 'side_to_side_chins', 'side_to_side_box_shuffle', 'side_lying_floor_stretch',
    'single_leg_butt_kick', 'single_leg_glute_bridge', 'single_leg_push_off', 'single_arm_linear_jammer', 'single_cone_sprint_drill', 'single_leg_hop_progression',
    'single_leg_lateral_hop', 'single_leg_stride_jump', 'skating', 'sled_drag_harness', 'sled_overhead_backward_walk', 'sled_push',
    'speed_band_overhead_triceps', 'spell_caster', 'spider_crawl', 'spinal_stretch', 'split_jerk', 'split_jump',
    'stairmaster', 'standing_biceps_stretch', 'standing_cable_lift', 'standing_cable_wood_chop', 'standing_elevated_quad_stretch', 'standing_gastrocnemius_calf_stretch',
    'standing_hamstring_and_calf_stretch', 'standing_hip_circles', 'standing_hip_flexors', 'standing_lateral_stretch', 'standing_long_jump', 'standing_olympic_plate_hand_squeeze',
    'standing_pelvic_tilt', 'standing_soleus_and_achilles_stretch', 'standing_toe_touches', 'star_jump', 'step_mill', 'stomach_vacuum',
    'superman', 'suspended_fallout', 'the_straddle', 'thigh_abductor', 'thigh_adductor', 'tire_flip',
    'toe_touchers', 'torso_rotation', 'tricep_side_stretch', 'triceps_pushdown', 'triceps_pushdown_rope_attachment', 'triceps_pushdown_v_bar_attachment',
    'triceps_stretch', 'two_arm_kettlebell_jerk', 'upper_back_stretch', 'upper_back_leg_grab', 'upward_stretch', 'weighted_ball_side_bend',
    'wide_stance_stiff_legs', 'wind_sprints', 'windmills', 'world_s_greatest_stretch', 'wrist_circles', 'wrist_roller',
    'wrist_rotations_with_straight_bar', 'yoke_walk', 'band_good_morning_pull_through', 'barbell_guillotine_bench_press', 'barbell_hack_squat', 'barbell_side_split_squat',
    'barbell_squat', 'barbell_squat_to_a_bench', 'barbell_walking_lunge', 'bent_over_two_arm_long_bar_row', 'bent_over_two_dumbbell_row_with_palms_in', 'bent_press',
    'bent_arm_barbell_pullover', 'bicycling_stationary', 'board_press', 'bradford_rocky_presses', 'cable_preacher_curl', 'cable_reverse_crunch',
    'car_deadlift', 'chain_press', 'clean', 'clean_deadlift', 'clean_pull', 'clean_and_jerk',
    'clean_and_press', 'clean_from_blocks', 'close_grip_ez_bar_curl_with_band', 'concentration_curls', 'cross_body_hammer_curl', 'crunch_hands_overhead',
    'crunches', 'cuban_press', 'decline_reverse_crunch', 'deficit_deadlift', 'drag_curl', 'dumbbell_bicep_curl',
    'dumbbell_floor_press', 'dumbbell_prone_incline_curl', 'dumbbell_rear_lunge', 'dumbbell_squat_to_a_bench', 'elevated_cable_rows', 'face_pull',
    'finger_curls', 'flexor_incline_dumbbell_curls', 'floor_press', 'forward_drag_with_press', 'frankenstein_squat', 'freehand_jump_squat',
    'frog_sit_ups', 'front_barbell_squat', 'front_barbell_squat_to_a_bench', 'front_dumbbell_raise', 'front_squat_clean_grip', 'front_two_dumbbell_raise',
    'glute_ham_raise', 'goblet_squat', 'good_morning_off_pins', 'gorilla_chin_crunch', 'hack_squat', 'hammer_curls',
    'handstand_push_ups', 'hang_clean', 'hang_clean_below_the_knees', 'hang_snatch_below_knees', 'hanging_bar_good_morning', 'hanging_leg_raise',
    'heaving_snatch_balance', 'high_cable_curls', 'incline_dumbbell_curl', 'incline_dumbbell_flyes_with_a_twist', 'incline_push_up_depth_jump', 'incline_push_up_medium',
    'incline_push_up_wide', 'inverted_row', 'jm_press', 'jackknife_sit_up', 'janda_sit_up', 'jefferson_squats',
    'jerk_dip_squat', 'kettlebell_hang_clean', 'kettlebell_seesaw_press', 'kettlebell_turkish_get_up_squat_style', 'knee_hip_raise_on_parallel_bars', 'kneeling_squat',
    'leg_over_floor_press', 'leverage_deadlift', 'leverage_high_row', 'leverage_iso_row', 'leverage_shrug', 'low_cable_crossover',
    'low_cable_triceps_extension', 'lunge_pass_through', 'lunge_sprint', 'muscle_snatch', 'narrow_stance_hack_squats', 'narrow_stance_leg_press',
    'narrow_stance_squats', 'natural_glute_ham_raise', 'oblique_crunches_on_the_floor', 'olympic_squat', 'one_arm_pronated_dumbbell_triceps_extension', 'one_arm_supinated_dumbbell_triceps_extension',
    'one_arm_dumbbell_row', 'one_arm_kettlebell_clean_and_jerk', 'one_arm_kettlebell_floor_press', 'one_arm_kettlebell_para_press', 'one_arm_kettlebell_split_snatch', 'one_arm_long_bar_row',
    'one_arm_open_palm_kettlebell_clean', 'open_palm_kettlebell_clean', 'overhead_cable_curl', 'overhead_squat', 'pallof_press', 'pallof_press_with_rotation',
    'palms_up_dumbbell_wrist_curl_over_a_bench', 'pin_presses', 'plie_dumbbell_squat', 'plyo_push_up', 'power_clean', 'power_clean_from_blocks',
    'power_snatch', 'power_snatch_from_blocks', 'preacher_curl', 'press_sit_up', 'prowler_sprint', 'pull_through',
    'pullups', 'push_up_to_side_plank', 'push_up_wide', 'push_ups_with_feet_elevated', 'rack_pull_with_bands', 'rack_pulls',
    'rear_leg_raises', 'reverse_band_bench_press', 'reverse_band_box_squat', 'reverse_band_deadlift', 'reverse_band_power_squat', 'reverse_band_sumo_deadlift',
    'reverse_barbell_curl', 'reverse_barbell_preacher_curls', 'reverse_cable_curl', 'reverse_crunch', 'reverse_flyes_with_external_rotation', 'reverse_hyperextension',
    'rickshaw_deadlift', 'ring_dips', 'romanian_deadlift', 'romanian_deadlift_from_deficit', 'rowing_stationary', 'scapular_pull_up',
    'seated_bent_over_two_arm_dumbbell_triceps_extension', 'seated_close_grip_concentration_barbell_curl', 'seated_dumbbell_palms_up_wrist_curl', 'seated_one_arm_dumbbell_palms_up_wrist_curl', 'seated_one_arm_cable_pulley_rows', 'seated_palms_down_barbell_wrist_curl',
    'see_saw_press_alternating_side_press', 'shotgun_row', 'side_leg_raises', 'single_dumbbell_raise', 'sit_squats', 'sit_up',
    'sled_reverse_flye', 'sled_row', 'smith_machine_reverse_calf_raises', 'smith_machine_squat', 'smith_single_leg_split_squat', 'snatch',
    'snatch_balance', 'snatch_deadlift', 'snatch_pull', 'snatch_shrug', 'snatch_from_blocks', 'speed_box_squat',
    'speed_squats', 'spider_curl', 'split_clean', 'split_snatch', 'split_squat_with_dumbbells', 'split_squats',
    'squat_jerk', 'squat_with_bands', 'squat_with_chains', 'squats_with_bands', 'standing_bent_over_one_arm_dumbbell_triceps_extension', 'standing_bent_over_two_arm_dumbbell_triceps_extension',
    'standing_calf_raises', 'standing_one_arm_dumbbell_curl_over_incline_bench', 'standing_one_arm_dumbbell_triceps_extension', 'standing_palm_in_one_arm_dumbbell_press', 'standing_palms_in_dumbbell_press', 'standing_towel_triceps_extension',
    'straight_arm_dumbbell_pullover', 'sumo_deadlift', 'sumo_deadlift_with_bands', 'sumo_deadlift_with_chains', 'supine_one_arm_overhead_throw', 'supine_two_arm_overhead_throw',
    'suspended_push_up', 'suspended_reverse_crunch', 'suspended_row', 'suspended_split_squat', 'svend_press', 't_bar_row_with_handle',
    'tate_press', 'trail_running_walking', 'tuck_crunch', 'two_arm_dumbbell_preacher_curl', 'two_arm_kettlebell_clean', 'two_arm_kettlebell_row',
    'upright_barbell_row', 'upright_cable_row', 'upright_row_with_bands', 'v_bar_pulldown', 'v_bar_pullup', 'vertical_swing',
    'weighted_sissy_squat', 'weighted_squat', 'wide_stance_barbell_squat', 'wide_grip_decline_barbell_bench_press', 'zercher_squats', 'zottman_curl',
    'zottman_preacher_curl',
)


def upgrade() -> None:
    # Удаляем только те упражнения, на которые нет FK-ссылок ни из
    # одной из таблиц-потребителей каталога: plan_exercises,
    # exercise_logs, user_exercise_favorites. На проде у пользователей
    # сохранены планы / логи / избранное с «плохими» упражнениями —
    # такие записи остаются в каталоге как исторические (см. docstring):
    # UI всё равно тянет список упражнений из JSON.
    # Партиями по 500, чтобы PostgreSQL не упёрся в лимит параметров.
    batch_size = 500
    for i in range(0, len(REMOVED_IDS), batch_size):
        batch = REMOVED_IDS[i:i + batch_size]
        op.execute(
            text(
                "DELETE FROM exercises "
                "WHERE exercise_id = ANY(:ids) "
                "AND id NOT IN ("
                "  SELECT exercise_id FROM plan_exercises "
                "  UNION "
                "  SELECT exercise_id FROM exercise_logs "
                "  UNION "
                "  SELECT exercise_id FROM user_exercise_favorites"
                ")"
            ).bindparams(ids=list(batch))
        )


def downgrade() -> None:
    # Откат через повторный seed из original.json (через scripts/seed_exercises.py).
    # Программный откат через миграцию неоправдан — это data restore, а не
    # schema change. Если нужно — `uv run python -m app.scripts.seed_exercises \
    # ml/data/processed/exercises_catalog_ru.original.json`.
    raise NotImplementedError(
        "Откат удалённых упражнений делать через seed_exercises.py "
        "с original.json (см. docstring)."
    )
