from data import APTITUDE_CATEGORIES, FUNCTION_ORDER, MBTI_STACKS
from logic import (
    aptitude_summary, derive_mbti, is_affordable, match_faculties, rank_nearby_faculties,
    split_matches_by_budget, university_options, verify_rule_set,
)


def aptitude_at(value: int) -> dict:
    return aptitude_summary({code: [value] * len(category["questions"]) for code, category in APTITUDE_CATEGORIES.items()})


def test_ne_and_ti_select_entp_stack():
    scores = {function: 10 for function in FUNCTION_ORDER}
    scores.update({"Ne": 50, "Ti": 45, "Fi": 30, "Fe": 25, "Si": 20})
    result = derive_mbti(scores)
    assert result.mbti == "ENTP"
    assert result.stack == ("Ne", "Ti", "Fe", "Si")


def test_twenty_aptitude_questions_and_strict_matching():
    assert all(len(category["questions"]) == 20 for category in APTITUDE_CATEGORIES.values())
    aptitude = aptitude_at(3)
    aptitude["M"]["percent"] = 100
    aptitude["S"]["percent"] = 80
    assert "วิศวกรรมคอมพิวเตอร์ / ซอฟต์แวร์" in {item["faculty"] for item in match_faculties("INTP", aptitude)}


def test_high_cost_faculty_requires_high_budget():
    matches = match_faculties("ISTJ", aptitude_at(5))
    recommended_medium, over_medium = split_matches_by_budget(matches, "medium")
    assert "แพทยศาสตร์" not in {item["faculty"] for item in recommended_medium}
    assert "แพทยศาสตร์" in {item["faculty"] for item in over_medium}
    assert "แพทยศาสตร์" in {item["faculty"] for item in split_matches_by_budget(matches, "high")[0]}


def test_budget_semantics_and_university_options():
    assert is_affordable("high", "high") and not is_affordable("high", "medium")
    assert is_affordable("medium", "medium") and not is_affordable("medium", "low")
    assert len(university_options("STEM", "high")) > len(university_options("STEM", "low"))


def test_rule_set_is_satisfiable_and_covers_all_16_mbti():
    verification = verify_rule_set()
    assert verification["all_rules_satisfiable"]
    assert verification["mbti_exhaustive"]
    assert verification["uncovered_mbti"] == []
    assert len(verification["satisfiable_rules"]) > 0


def test_edge_cases_have_a_safe_fallback_for_every_mbti():
    for aptitude in (aptitude_at(1), aptitude_at(5), aptitude_at(3)):
        for mbti in MBTI_STACKS:
            strict = match_faculties(mbti, aptitude)
            relaxed = match_faculties(mbti, aptitude, subject_relaxation=10)
            nearby = rank_nearby_faculties(mbti, aptitude, budget="low")
            assert strict or relaxed or nearby


def test_equal_function_scores_are_deterministic():
    scores = {function: 30 for function in FUNCTION_ORDER}
    first = derive_mbti(scores)
    assert first == derive_mbti(scores)
    assert first.mbti in MBTI_STACKS
    assert first.used_tiebreak


def test_subject_relaxation_is_limited_and_respects_budget():
    aptitude = aptitude_at(3)
    assert match_faculties("INTP", aptitude, subject_relaxation=10)
    nearby = rank_nearby_faculties("INTP", aptitude_at(1), budget="low")
    assert nearby and all(item["cost"] == "low" for item in nearby)
