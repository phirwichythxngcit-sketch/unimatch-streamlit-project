from data import APTITUDE_CATEGORIES, FUNCTION_ORDER
from logic import aptitude_summary, derive_mbti, match_faculties, university_options


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
