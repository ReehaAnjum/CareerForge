import math


def calculate_readiness(skill_levels, solved_count, interview_total, interview_completed, weights, coding_target=20):
    """Return 0-100 skill, coding, interview, and weighted overall readiness."""
    expected_weights = {"skills", "coding", "interview"}
    if set(weights) != expected_weights:
        raise ValueError("Readiness weights must define skills, coding, and interview.")
    if any(not math.isfinite(value) or value < 0 for value in weights.values()):
        raise ValueError("Readiness weights must be finite, non-negative numbers.")
    if not math.isclose(sum(weights.values()), 1.0, abs_tol=1e-9):
        raise ValueError("Readiness weights must add up to 1.0.")
    if coding_target <= 0:
        raise ValueError("The coding practice target must be greater than zero.")
    if any(not 1 <= level <= 5 for level in skill_levels):
        raise ValueError("Skill levels must be between 1 and 5.")
    if solved_count < 0 or interview_total < 0 or not 0 <= interview_completed <= interview_total:
        raise ValueError("Practice totals must be valid non-negative counts.")

    skills_score = (
        sum(skill_levels) / len(skill_levels) * 20
        if skill_levels
        else 0
    )
    coding_score = min(solved_count / coding_target, 1) * 100
    interview_score = (
        interview_completed / interview_total * 100
        if interview_total
        else 0
    )
    components = {
        "skills": round(skills_score),
        "coding": round(coding_score),
        "interview": round(interview_score),
    }
    overall = round(sum(components[key] * weights[key] for key in expected_weights))
    return {**components, "overall": overall}
