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
    """หา MBTI แบบกำหนดผลได้แน่นอนด้วย Dom → Aux → Tert → Inf."""
    if set(scores) != set(FUNCTION_ORDER):
        raise ValueError("scores ต้องมีครบ 8 ฟังก์ชัน: Ne, Ni, Se, Si, Te, Ti, Fe, Fi")

    highest = max(scores.values())
    dominant_ties = tuple(function for function in FUNCTION_ORDER if scores[function] == highest)
    candidates = [(mbti, stack) for mbti, stack in MBTI_STACKS.items() if stack[0] in dominant_ties]

    def stack_affinity(item: tuple[str, tuple[str, str, str, str]]) -> tuple[int, int, int, int, str]:
        mbti, stack = item
        return (*[scores[function] for function in stack], mbti)

    mbti, stack = max(candidates, key=stack_affinity)
    # มีการใช้ตัวตัดสินเมื่อฟังก์ชัน Dominant เสมอกัน หรือมีมากกว่าหนึ่ง stack ที่เริ่มต้นเหมือนกัน
    used_tiebreak = len(dominant_ties) > 1 or sum(1 for _, item_stack in candidates if item_stack[0] == stack[0]) > 1
    return MbtiResult(mbti=mbti, stack=stack, dominant_ties=dominant_ties, used_tiebreak=used_tiebreak)


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
    faculty, group, mbti_set, conditions, cost = rule
    return {"faculty": faculty, "group": group, "mbti_set": mbti_set, "conditions": conditions, "cost": cost}


def _evaluate_rule(
    rule: Mapping,
    mbti: str,
    aptitude: Mapping[str, Mapping[str, int | str]],
    subject_relaxation: int = 0,
) -> dict:
    """Evaluate a rule without inventing a weighted personality score."""
    conditions = [
        {
            "category": category,
            "actual": int(aptitude[category]["percent"]),
            "minimum": minimum,
            "effective_minimum": max(0, minimum - subject_relaxation),
            "passed": int(aptitude[category]["percent"]) > max(0, minimum - subject_relaxation),
        }
        for category, minimum in rule["conditions"]
    ]
    subject_average = round(sum(item["actual"] for item in conditions) / len(conditions))
    margins = [item["actual"] - item["effective_minimum"] for item in conditions]
    minimum_margin = min(margins)
    average_margin = round(sum(margins) / len(margins))
    passed_conditions = sum(item["passed"] for item in conditions)
    mbti_pass = mbti in rule["mbti_set"]
    return {
        **rule,
        "mbti_pass": mbti_pass,
        "subject_average": subject_average,
        "minimum_margin": minimum_margin,
        "average_margin": average_margin,
        "passed_conditions": passed_conditions,
        "total_conditions": len(conditions),
        "condition_results": conditions,
        "passed": mbti_pass and passed_conditions == len(conditions),
    }


def logical_rank_key(item: Mapping) -> tuple[int, int, int, int, int, int]:
    """Transparent ranking: exact MBTI → all subjects pass → passed count → weakest margin → average margin → actual average."""
    return (
        int(item["mbti_pass"]),
        int(item["passed_conditions"] == item["total_conditions"]),
        int(item["passed_conditions"]),
        int(item["minimum_margin"]),
        int(item["average_margin"]),
        int(item["subject_average"]),
    )


def match_faculties(
    mbti: str,
    aptitude: Mapping[str, Mapping[str, int | str]],
    subject_relaxation: int = 0,
) -> list[dict]:
    """Return strict logical matches, ordered by actual scores relevant to each faculty."""
    if not 0 <= subject_relaxation <= 10:
        raise ValueError("subject_relaxation ต้องอยู่ระหว่าง 0 ถึง 10")
    matches = [
        evaluated
        for raw_rule in FACULTY_RULES
        if (evaluated := _evaluate_rule(_rule_to_dict(raw_rule), mbti, aptitude, subject_relaxation))["passed"]
    ]
    return sorted(matches, key=lambda item: (logical_rank_key(item), item["faculty"]), reverse=True)


def rank_nearby_faculties(
    mbti: str,
    aptitude: Mapping[str, Mapping[str, int | str]],
    limit: int = 5,
    budget: str | None = None,
) -> list[dict]:
    """Rank affordable alternatives with auditable logical precedence, not arbitrary weights."""
    ranked = [
        _evaluate_rule(_rule_to_dict(raw_rule), mbti, aptitude)
        for raw_rule in FACULTY_RULES
        if is_affordable(raw_rule[4], budget)
    ]
    return sorted(ranked, key=lambda item: (logical_rank_key(item), item["faculty"]), reverse=True)[:limit]


BUDGET_TIERS = {"low": ("low",), "medium": ("low", "medium"), "high": ("low", "medium", "high")}


def is_affordable(cost_tier: str, budget: str | None) -> bool:
    if budget is None:
        return True
    return cost_tier in BUDGET_TIERS[budget]


def split_matches_by_budget(matches: Sequence[Mapping], budget: str | None) -> tuple[list[dict], list[dict]]:
    recommended = [dict(item) for item in matches if is_affordable(item["cost"], budget)]
    over_budget = [dict(item) for item in matches if not is_affordable(item["cost"], budget)]
    return recommended, over_budget


def university_options(group: str, budget: str) -> list[dict[str, str]]:
    options = []
    for tier in BUDGET_TIERS[budget]:
        for university, estimate in UNIVERSITY_OPTIONS[group][tier]:
            options.append({"tier": tier, "university": university, "estimate": estimate})
    return options


def logic_expression(rule: Mapping) -> str:
    mbti_term = " ∨ ".join(rule["mbti_set"])
    subject_term = " ∧ ".join(f"{category} > {minimum}%" for category, minimum in rule["conditions"])
    return f"({mbti_term}) ∧ ({subject_term})"


def verify_rule_set() -> dict[str, object]:
    """ตรวจ satisfiability และความครอบคลุมของกฎจากข้อมูลจริงของระบบ."""
    all_types = set(MBTI_STACKS)
    covered_types: set[str] = set()
    satisfiable_rules: list[str] = []

    for raw_rule in FACULTY_RULES:
        rule = _rule_to_dict(raw_rule)
        if not rule["mbti_set"] or not rule["conditions"]:
            raise ValueError(f"กฎ {rule['faculty']} ต้องมี MBTI และเงื่อนไขวิชา")
        if rule["cost"] not in BUDGET_TIERS:
            raise ValueError(f"ระดับงบของ {rule['faculty']} ไม่ถูกต้อง")
        for mbti in rule["mbti_set"]:
            if mbti not in all_types:
                raise ValueError(f"MBTI {mbti} ไม่อยู่ในระบบ")
        for category, minimum in rule["conditions"]:
            if category not in APTITUDE_CATEGORIES or not 0 <= minimum < 100:
                raise ValueError(f"เกณฑ์ของ {rule['faculty']} ไม่สามารถทำให้จริงได้")
        covered_types.update(rule["mbti_set"])
        satisfiable_rules.append(rule["faculty"])

    return {
        "all_rules_satisfiable": len(satisfiable_rules) == len(FACULTY_RULES),
        "satisfiable_rules": satisfiable_rules,
        "uncovered_mbti": sorted(all_types - covered_types),
        "mbti_exhaustive": covered_types == all_types,
    }
