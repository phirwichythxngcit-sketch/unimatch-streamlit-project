"""Faculty Matcher — จับคู่ผู้เรียนกับคณะโดยใช้ Logic Engine"""

import json
import os
from logic.logic_engine import LogicEngine, Proposition


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def load_faculties() -> list[dict]:
    path = os.path.join(DATA_DIR, "faculties.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


F2_MAPPING = {
    "stability": "careerStability",
    "income": "incomeSpeed",
    "freedom": "careerFreedom",
}

F6_COST_LEVELS = {
    "limited": "low",
    "medium": "medium",
    "flexible": "high",
}


class FacultyMatcher:
    """จับคู่ผู้เรียนกับคณะ"""

    def __init__(self):
        self.faculties = load_faculties()
        self.logic = LogicEngine()

    def match_all(
        self,
        mbti: str,
        interest_scores: dict[str, dict],
        financial_profile: dict[str, str],
        has_logical_project: bool = True,
    ) -> list[dict]:
        """
        คัดกรองทุกคณะ แล้วคำนวณ Match %
        คืน list ของ dict เรียงตาม Overall Match % จากมากไปน้อย
        """
        results = []
        for fac in self.faculties:
            result = self._evaluate_faculty(
                fac, mbti, interest_scores, financial_profile, has_logical_project
            )
            results.append(result)

        results.sort(key=lambda r: r["overall_match"], reverse=True)
        return results

    def _evaluate_faculty(
        self,
        faculty: dict,
        mbti: str,
        interest_scores: dict[str, dict],
        financial_profile: dict[str, str],
        has_logical_project: bool,
    ) -> dict:
        """ประเมินคณะเดียว"""

        # === 1. MBTI Match ===
        mbti_props = []
        for mbti_type in faculty["mbtiSet"]:
            prop = self.logic.evaluate_mbti_condition(mbti, [mbti_type])
            mbti_props.append(prop)
        mbti_prop = self.logic.OR(*mbti_props)
        mbti_match = 100.0 if mbti_prop.value else 30.0

        # === 2. Academic Match ===
        academic_conditions = faculty.get("academicConditions", [])
        academic_props = []
        academic_details = []
        all_academic_pass = True

        for cond in academic_conditions:
            cat = cond["category"]
            min_pct = cond["min"]
            user_pct = interest_scores.get(cat, {}).get("percentage", 0)
            prop = self.logic.evaluate_academic_condition(user_pct, min_pct, cat)
            academic_props.append(prop)
            academic_details.append({
                "category": cat,
                "user_pct": user_pct,
                "min_pct": min_pct,
                "passed": prop.value,
                "description": str(prop),
            })
            if not prop.value:
                all_academic_pass = False

        if not academic_conditions:
            academic_match = 80.0
        elif all_academic_pass:
            academic_match = 100.0
        else:
            total_ratio = 0
            for cond in academic_conditions:
                cat = cond["category"]
                min_pct = cond["min"]
                user_pct = interest_scores.get(cat, {}).get("percentage", 0)
                ratio = min(user_pct / min_pct, 1.5) if min_pct > 0 else 1.0
                total_ratio += ratio
            academic_match = min((total_ratio / len(academic_conditions)) * 70, 99.0)

        # === 3. Financial Match ===
        financial_match = self._compute_financial_match(faculty, financial_profile)

        # === 4. Logical Thinking Match ===
        logical_match = 90.0 if has_logical_project else 50.0

        # === 5. Overall Match ===
        overall = (
            academic_match * 0.35
            + mbti_match * 0.25
            + financial_match * 0.25
            + logical_match * 0.15
        )
        overall = min(max(overall, 0), 100)

        # === 6. Condition Details ===
        condition_details = self._build_condition_details(
            mbti_prop, academic_details, financial_profile, faculty, has_logical_project
        )

        return {
            "faculty": faculty["faculty"],
            "group": faculty.get("group", ""),
            "academic_match": round(academic_match, 1),
            "mbti_match": round(mbti_match, 1),
            "financial_match": round(financial_match, 1),
            "logical_match": round(logical_match, 1),
            "overall_match": round(overall, 1),
            "mbti_passed": mbti_prop.value,
            "all_academic_passed": all_academic_pass,
            "academic_details": academic_details,
            "condition_details": condition_details,
            "financial": faculty.get("financial", {}),
        }

    def _compute_financial_match(self, faculty: dict, financial_profile: dict[str, str]) -> float:
        """คำนวณคะแนน Financial Match"""
        fin = faculty.get("financial", {})
        score = 50.0

        # F2 match
        f2_key = F2_MAPPING.get(financial_profile.get("F2", "stability"), "careerStability")
        f2_val = fin.get(f2_key, 5)
        score += (f2_val / 10) * 15

        # F3 match
        f3 = financial_profile.get("F3", "low")
        post_grad_need = fin.get("postGraduationIncomeNeed", 5)
        if f3 == "high" and post_grad_need >= 7:
            score += 10
        elif f3 == "low":
            score += 5

        # F4 match
        f4 = financial_profile.get("F4", "not_interested")
        scholarship = fin.get("bindingScholarship", "medium")
        if f4 == "interested" and scholarship in ("high", "medium"):
            score += 10
        elif f4 == "not_interested" and scholarship == "low":
            score += 10
        else:
            score += 5

        # F5 match
        f5 = financial_profile.get("F5", "flexible")
        location = fin.get("locationFlexibility", "medium")
        if f5 == "limited" and location == "limited":
            score -= 10
        elif f5 == "flexible":
            score += 5

        # F6 match
        f6 = financial_profile.get("F6", "medium")
        hidden = fin.get("hiddenCost", "medium")
        f6_order = {"limited": 0, "medium": 1, "flexible": 2}
        h_order = {"low": 0, "medium": 1, "high": 2}
        if f6_order.get(f6, 1) >= h_order.get(hidden, 1):
            score += 10
        else:
            score -= 5

        return min(max(score, 10), 100)

    def _build_condition_details(
        self,
        mbti_prop: Proposition,
        academic_details: list[dict],
        financial_profile: dict[str, str],
        faculty: dict,
        has_logical_project: bool,
    ) -> list[dict]:
        """สร้างรายละเอียดเงื่อนไขสำหรับแสดงผล"""
        details = []

        # MBTI
        details.append({
            "section": "MBTI",
            "description": f"MBTI ต้องอยู่ในกลุ่ม {faculty['mbtiSet']}",
            "passed": mbti_prop.value,
            "icon": "✅" if mbti_prop.value else "❌",
            "reason": f"MBTI ของคุณตรงกับกลุ่มที่กำหนด" if mbti_prop.value else f"MBTI ไม่ตรงกับกลุ่มที่กำหนด",
        })

        # Academic
        for ad in academic_details:
            details.append({
                "section": f"หมวดวิชา {ad['category']}",
                "description": f"{ad['category']} ต้อง ≥ {ad['min_pct']}%",
                "passed": ad["passed"],
                "icon": "✅" if ad["passed"] else "❌",
                "reason": f"ได้ {ad['user_pct']:.1f}% {'ผ่านเกณฑ์' if ad['passed'] else 'ไม่ผ่านเกณฑ์'}",
            })

        # Financial
        f1 = financial_profile.get("F1", "medium")
        details.append({
            "section": "การเงิน (F1)",
            "description": "งบประมาณค่าเทอม",
            "passed": True,
            "icon": "ℹ️",
            "reason": f"ระดับงบประมาณ: {f1}",
        })

        f5 = financial_profile.get("F5", "flexible")
        details.append({
            "section": "การเงิน (F5)",
            "description": "ข้อจำกัดด้านการเดินทาง",
            "passed": True,
            "icon": "ℹ️",
            "reason": f"ระดับ: {f5}",
        })

        # Logical Thinking
        details.append({
            "section": "ตรรกศาสตร์",
            "description": "ประสบการณ์ทำโครงงานตรรกศาสตร์",
            "passed": has_logical_project,
            "icon": "✅" if has_logical_project else "⚠️",
            "reason": "มีประสบการณ์ทำโครงงาน" if has_logical_project else "ไม่มีประสบการณ์ทำโครงงาน",
        })

        return details
