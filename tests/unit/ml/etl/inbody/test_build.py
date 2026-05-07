"""Интеграционный тест pipeline без I/O — REQ-20 + SC-05."""

from ml.etl.inbody.anchor import Anchor
from ml.etl.inbody.build import build_rows


def _make_anchor(i: int, *, sex: str = "male") -> Anchor:
    return Anchor(
        raw_user_id=f"u{i}",
        source="s3",
        sex=sex,
        age_years=25 + (i % 15),
        height_cm=170.0 + (i % 20),
        weight_kg=70.0 + (i % 20),
        body_fat_percent=15.0 + (i % 15),
        muscle_mass_kg=None,
        bmr_kcal=None,
        training_frequency_per_week=3 + (i % 3),
    )


class TestBuildRows:
    def test_pipeline_produces_rows_for_all_users(self) -> None:
        anchors = [_make_anchor(i) for i in range(10)]

        paired = build_rows(anchors, weeks=8, seed=42, salt="s")

        # 10 анкеров × 8 недель = 80 строк.
        assert len(paired) == 80
        # Все строки имеют валидный split.
        assert {s for _, s in paired} == {"train", "val", "test"}

    def test_deterministic_with_same_seed_and_salt(self) -> None:
        anchors = [_make_anchor(i) for i in range(15)]

        a = build_rows(anchors, weeks=5, seed=7, salt="s")
        b = build_rows(anchors, weeks=5, seed=7, salt="s")

        assert [(r.weight_kg, sp) for r, sp in a] == [
            (r.weight_kg, sp) for r, sp in b
        ]

    def test_outliers_are_filtered_out(self) -> None:
        anchors = [_make_anchor(0)]
        anchors.append(
            Anchor(
                raw_user_id="bad",
                source="s3",
                sex="male",
                age_years=30,
                height_cm=175.0,
                weight_kg=10.0,  # BMI ~3 — outlier
                body_fat_percent=20.0,
            )
        )

        paired = build_rows(anchors, weeks=4, seed=42, salt="s")

        users = {r.anon_user_id for r, _ in paired}
        # Bad-юзер должен быть отфильтрован — остался только один.
        assert len(users) == 1
