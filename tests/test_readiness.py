import pytest

from readiness import calculate_readiness


WEIGHTS = {"skills": 0.40, "coding": 0.35, "interview": 0.25}


def test_readiness_score_uses_documented_weighted_components():
    result = calculate_readiness([4, 3], 10, 4, 2, WEIGHTS, coding_target=20)
    assert result == {"skills": 70, "coding": 50, "interview": 50, "overall": 58}


def test_empty_preparation_starts_at_zero_and_scores_cap_at_100():
    assert calculate_readiness([], 0, 0, 0, WEIGHTS) == {
        "skills": 0,
        "coding": 0,
        "interview": 0,
        "overall": 0,
    }
    assert calculate_readiness([5], 50, 1, 1, WEIGHTS) == {
        "skills": 100,
        "coding": 100,
        "interview": 100,
        "overall": 100,
    }


@pytest.mark.parametrize(
    "weights",
    [
        {"skills": 1, "coding": 1, "interview": 1},
        {"skills": 0.4, "coding": 0.4},
        {"skills": -0.2, "coding": 0.8, "interview": 0.4},
    ],
)
def test_invalid_weight_configurations_are_rejected(weights):
    with pytest.raises(ValueError):
        calculate_readiness([], 0, 0, 0, weights)


def test_invalid_counts_and_targets_are_rejected():
    with pytest.raises(ValueError):
        calculate_readiness([], 0, 0, 0, WEIGHTS, coding_target=0)
    with pytest.raises(ValueError):
        calculate_readiness([], 0, 1, 2, WEIGHTS)
