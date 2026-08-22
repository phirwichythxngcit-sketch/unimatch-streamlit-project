"""ตรรกะธุรกิจที่ทดสอบได้ โดยไม่ขึ้นกับหน้า Streamlit."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from data import APTITUDE_CATEGORIES, FACULTY_RULES, FUNCTION_ORDER, LIKERT_LABELS, MBTI_STACKS, UNIVERSITY_OPTIONS


@dataclass(frozen=True)
class MbtiResult:
    mbti: str
    stack: tuple[str, str, str, str]
    dominant_ties: tuple[str, ...]
    used_tiebreak: bool


def function_totals(responses: Mapping[str, Sequence[int]]) -> dict[str, int]:
    """รวมคะแนนแต่ละ cognitive function (10–50 เมื่อกรอกครบ 10 ข้อ)."""
    return {function: sum(responses.get(function, ())) for function in FUNCTION_ORDER}


def derive_mbti(scores: Mapping[str, int]) -> MbtiResult:
    """หา MBTI ตามลำดับ Dominant → Auxiliary → Tertiary → Inferior.

    เมื่อคะแนนตำแหน่งหนึ่งเสมอกัน ระบบจึงเปรียบเทียบตำแหน่งถัดไปตามลำดับนี้
    เพื่อให้ผลลัพธ์มีเงื่อนไขชัดเจนและทำซ้ำได้.
    """
    if set(scores) != set(FUNCTION_ORDER):
        raise ValueError("scores ต้องมีครบ 8 ฟังก์ชัน: Ne, Ni, Se, Si, Te, Ti, Fe, Fi")
    highest = max(scores.values())
    dominant_ties = tuple(function for function in FUNCTION_ORDER if scores[function] == highest)
    candidates = [
        (mbti, stack)
        for mbti, stack in MBTI_STACKS.items()
        if stack[0] in dominant_ties
    ]
    # เปรียบเทียบตามลำดับ Dom → Aux → Tert → Inf โดยตรง
    # จึงอธิบายเงื่อนไขของแต่ละตำแหน่งให้ผู้ใช้ตรวจตามได้
    def stack_affinity(item: tuple[str, tuple[str, str, str, str]]) -> tuple[int, int, int, int, str]:
        mbti, stack = item
        return (*[scores[function] for function in stack], mbti)

    mbti, stack = max(candidates, key=stack_affinity)
    return MbtiResult(
        mbti=mbti,
        stack=stack,
        dominant_ties=dominant_ties,
        used_tiebreak=len(dominant_ties) > 1 or scores[stack[1]] == scores[[s for _, s in candidates if s[0] == stack[0] and s != stack][0][1]],
    )


def aptitude_summary(responses: Mapping[str, Sequence[int]]) -> dict[str, dict[str, int | str]]:
    """รวมคะแนนและคิดเป็นเปอร์เซ็นต์ตามจำนวนคำถามจริงของแต่ละหมวด."""
    result: dict[str, dict[str, int | str]] = {}
    maximum_response = max(LIKERT_LABELS)
    for code, category in APTITUDE_CATEGORIES.items():
        total = sum(responses.get(code, ()))
        maximum = len(category["questions"]) * maximum_response
        percent = round((total / maximum) * 100) if maximum else 0
        zone = "พื้นที่เด่น" if percent >= 80 else "พื้นที่เสริม" if percent >= 60 else "พื้นที่ที่พัฒนาได้"
        result[code] = {"name": category["name"], "total": total, "percent": percent, "zone": zone}
    return result

def _rule_to_dict(rule: tuple) -> dict:
    faculty, group, mbti_set, conditions = rule
    return {"faculty": faculty, "group": group, "mbti_set": mbti_set, "conditions": conditions}


def match_faculties(mbti: str, aptitude: Mapping[str, Mapping[str, int | str]]) -> list[dict]:
    """ใช้ ∧ ระหว่าง MBTI กับทุกเกณฑ์หมวดวิชา; เครื่องหมาย > เป็น strict ตามโจทย์."""
    matches = []
    for raw_rule in FACULTY_RULES:
        rule = _rule_to_dict(raw_rule)
        mbti_pass = mbti in rule["mbti_set"]
        conditions = [
            {
                "category": category,
                "actual": int(aptitude[category]["percent"]),
                "minimum": minimum,
                "passed": int(aptitude[category]["percent"]) > minimum,
            }
            for category, minimum in rule["conditions"]
        ]
        passed = mbti_pass and all(condition["passed"] for condition in conditions)
        if passed:
            matches.append({**rule, "mbti_pass": mbti_pass, "condition_results": conditions, "passed": True})
    return matches


def rank_nearby_faculties(mbti: str, aptitude: Mapping[str, Mapping[str, int | str]], limit: int = 5) -> list[dict]:
    """เสนอทางเลือกใกล้เคียงเมื่อไม่มีคณะใดผ่านครบทุกประพจน์."""
    ranked = []
    for raw_rule in FACULTY_RULES:
        rule = _rule_to_dict(raw_rule)
        subject_ratio = sum(
            min(1.0, int(aptitude[category]["percent"]) / minimum)
            for category, minimum in rule["conditions"]
        ) / len(rule["conditions"])
        score = round((30 if mbti in rule["mbti_set"] else 0) + (70 * subject_ratio))
        ranked.append({**rule, "compatibility": min(100, score)})
    return sorted(ranked, key=lambda item: item["compatibility"], reverse=True)[:limit]


def university_options(group: str, budget: str) -> list[dict[str, str]]:
    """งบมากเลือกได้ทุกระดับ งบปานกลางเลือก low/medium และงบน้อยเลือก low."""
    allowed = {"low": ("low",), "medium": ("low", "medium"), "high": ("low", "medium", "high")}
    options = []
    for tier in allowed[budget]:
        for university, estimate in UNIVERSITY_OPTIONS[group][tier]:
            options.append({"tier": tier, "university": university, "estimate": estimate})
    return options


def logic_expression(rule: Mapping) -> str:
    mbti_term = " ∨ ".join(rule["mbti_set"])
    subject_term = " ∧ ".join(f"{category} > {minimum}%" for category, minimum in rule["conditions"])
    return f"({mbti_term}) ∧ ({subject_term})"
