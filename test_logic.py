from data import APTITUDE_CATEGORIES, FUNCTION_ORDER
from logic import (
    aptitude_summary,
    derive_mbti,
    financial_summary,
    logic_expression,
    match_faculties,
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


def test_subject_percentages_and_strict_matching():
    responses = {code: [3] * 6 for code in APTITUDE_CATEGORIES}
    responses["M"] = [5] * 6
    responses["S"] = [4] * 6
    aptitude = aptitude_summary(responses)
    assert aptitude["M"]["percent"] == 100
    assert aptitude["S"]["percent"] == 80
    assert "วิศวกรรมคอมพิวเตอร์ / ซอฟต์แวร์" in {
        item["faculty"] for item in match_faculties("INTP", aptitude)
    }


def test_higher_budget_includes_more_tiers():
    assert len(university_options("STEM", "high")) > len(university_options("STEM", "low"))


def test_financial_summary_contains_all_planning_decisions():
    summary = financial_summary(
        "medium",
        "ความมั่นคงและสวัสดิการ",
        "ไม่มีภาระเร่งด่วน",
        "ไม่สนใจ / สนใจเฉพาะทุนมอบเปล่า",
        "ยืดหยุ่น ไปเรียนต่างจังหวัดได้",
    )
    assert summary["budget"] == "medium"
    assert len(summary["decisions"]) == 4
    assert len(summary["actions"]) == 4


def test_logic_expression_uses_or_for_mbti_and_and_for_conditions():
    rule = {
        "mbti_set": ("INTP", "ENTP"),
        "conditions": (("M", 60), ("L", 70)),
    }
    assert logic_expression(rule) == "(INTP ∨ ENTP) ∧ (M > 60% ∧ L > 70%)"
