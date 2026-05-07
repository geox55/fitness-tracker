"""Тесты split — REQ-18 + SC-05 (no leakage)."""

import random

import pytest
from ml.etl.inbody.anchor import Anchor
from ml.etl.inbody.split import (
    DEFAULT_SPLIT,
    assert_no_leakage,
    assign_split,
    split_users,
)
from ml.etl.inbody.synthesize import synthesize_trajectory


class TestSplitUsers:
    def test_70_15_15_proportions_approx(self) -> None:
        users = [f"u{i}" for i in range(1000)]

        mapping = split_users(users, seed=42)

        counts = {"train": 0, "val": 0, "test": 0}
        for v in mapping.values():
            counts[v] += 1
        assert 690 <= counts["train"] <= 710
        assert 140 <= counts["val"] <= 160
        assert 140 <= counts["test"] <= 160

    def test_deterministic(self) -> None:
        users = [f"u{i}" for i in range(50)]
        a = split_users(users, seed=42)
        b = split_users(users, seed=42)
        assert a == b

    def test_different_seed_different_partition(self) -> None:
        users = [f"u{i}" for i in range(200)]
        a = split_users(users, seed=1)
        b = split_users(users, seed=2)
        assert a != b

    def test_ratios_must_sum_to_one(self) -> None:
        with pytest.raises(ValueError, match="sum to 1"):
            split_users(["u1"], ratios=(0.5, 0.3, 0.1), seed=0)

    def test_default_ratios_sum_correctly(self) -> None:
        assert sum(DEFAULT_SPLIT) == pytest.approx(1.0)


class TestAssignSplit:
    def _anchor(self, idx: int) -> Anchor:
        return Anchor(
            raw_user_id=f"u{idx}",
            source="s3",
            sex="male",
            age_years=30,
            height_cm=175.0,
            weight_kg=75.0,
            body_fat_percent=18.0,
            bmr_kcal=1700.0,
            training_frequency_per_week=3,
        )

    def test_no_leakage_invariant_holds(self) -> None:
        # Несколько пользователей × несколько строк каждый.
        rows = []
        for i in range(20):
            rng = random.Random(i)
            rows.extend(
                synthesize_trajectory(
                    self._anchor(i), anon_user_id=f"anon{i}", weeks=4, rng=rng
                )
            )

        paired = assign_split(rows, seed=7)

        # Каждый user в одной части — иначе assert_no_leakage упадёт.
        assert_no_leakage(paired)
        # Все строки получили split-метку.
        assert all(s in {"train", "val", "test"} for _, s in paired)

    def test_assert_no_leakage_catches_leak(self) -> None:
        rng = random.Random(0)
        rows = synthesize_trajectory(
            self._anchor(0), anon_user_id="anon0", weeks=4, rng=rng
        )
        # Подсунем левую раскладку: одну и ту же строку в двух частях.
        leaky = [(rows[0], "train"), (rows[1], "val")]
        with pytest.raises(AssertionError, match="leaked"):
            assert_no_leakage(leaky)
