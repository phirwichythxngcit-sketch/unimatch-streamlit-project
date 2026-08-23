from data import APTITUDE_CATEGORIES, FUNCTION_ORDER
from logic import (
    aptitude_summary,
    derive_mbti,
    is_affordable,
    match_faculties,
    split_matches_by_budget,
    university_options,
)


def test_ne_and_ti_select_entp_stack():
    scores = {function: 10 for function in FUNCTION_ORDER}
    scores.update({"Ne": 50, "Ti": 45, "Fi": 30, "Fe": 25, "Si": 20})
    result = derive_mbti(scores)
    assert result.mbti == "ENTP"
    assert result.stack == ("Ne", "Ti", "Fe", "Si")


def test_ni_and_fe_select_infj_stack():
    scores = {function: 10 for function in FUNCTION_ORDER}
    scores.update({"Ni": 50, "Fe": 42, "Te": 20, "Se": 15})
    result = derive_mbti(scores)
    assert result.mbti == "INFJ"
    assert result.stack == ("Ni", "Fe", "Ti", "Se")


def test_twenty_aptitude_questions_and_strict_matching():
    assert all(len(category["questions"]) == 20 for category in APTITUDE_CATEGORIES.values())

    responses = {code: [3] * len(category["questions"]) for code, category in APTITUDE_CATEGORIES.items()}
    responses["M"] = [5] * len(APTITUDE_CATEGORIES["M"]["questions"])
    responses["S"] = [4] * len(APTITUDE_CATEGORIES["S"]["questions"])

    aptitude = aptitude_summary(responses)

    assert aptitude["M"]["total"] == 100
    assert aptitude["M"]["percent"] == 100
    assert aptitude["S"]["percent"] == 80
    assert "วิศวกรรมคอมพิวเตอร์ / ซอฟต์แวร์" in {item["faculty"] for item in match_faculties("INTP", aptitude)}

def test_higher_budget_includes_more_tiers():
    assert len(university_options("STEM", "high")) > len(university_options("STEM", "low"))


def max_aptitude() -> dict:
    responses = {code: [5] * len(category["questions"]) for code, category in APTITUDE_CATEGORIES.items()}
    return aptitude_summary(responses)


def test_high_cost_faculty_requires_high_budget():
    faculties = {item["faculty"]: item["cost"] for item in match_faculties("ISTJ", max_aptitude())}
    assert faculties.get("แพทยศาสตร์") == "high"


def test_split_matches_by_budget_blocks_insufficient_funds():
    matches = match_faculties("ISTJ", max_aptitude())

    recommended_medium, over_medium = split_matches_by_budget(matches, "medium")
    assert "แพทยศาสตร์" not in {item["faculty"] for item in recommended_medium}
    assert "แพทยศาสตร์" in {item["faculty"] for item in over_medium}

    recommended_high, over_high = split_matches_by_budget(matches, "high")
    assert "แพทยศาสตร์" in {item["faculty"] for item in recommended_high}
    assert over_high == []


def test_is_affordable_semantics():
    assert is_affordable("high", "high")
    assert not is_affordable("high", "medium")
    assert not is_affordable("high", "low")
    assert is_affordable("medium", "medium")
    assert not is_affordable("medium", "low")
    assert is_affordable("low", "low")
    assert is_affordable("low", "high")


def test_no_budget_filter_returns_all_matches_as_recommended():
    matches = match_faculties("ISTP", max_aptitude())
    recommended, over = split_matches_by_budget(matches, None)
    assert len(recommended) == len(matches)
    assert over == []


def test_tertiary_score_breaks_an_auxiliary_tie():
    scores = {function: 10 for function in FUNCTION_ORDER}
    scores.update({"Ne": 50, "Ti": 40, "Fi": 40, "Te": 45, "Fe": 20})
    result = derive_mbti(scores)
    assert result.mbti == "ENFP"


def test_inferior_score_breaks_a_remaining_stack_tie():
    scores = {function: 10 for function in FUNCTION_ORDER}
    scores.update({"Ne": 50, "Se": 50, "Ti": 40, "Fe": 30, "Ni": 20})
    result = derive_mbti(scores)
    assert result.mbti == "ESTP"
