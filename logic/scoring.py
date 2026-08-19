"""Scoring Engine — คำนวณคะแนน Interest/Aptitude และ Financial"""

MAX_INTEREST_SCORE_PER_CATEGORY = 100  # 20 questions * 5 max


class ScoringEngine:
    """คำนวณคะแนน Interest/Aptitude 5 หมวด (M, S, L, H, A)"""

    @staticmethod
    def compute_interest_scores(answers: dict[str, int]) -> dict[str, dict]:
        """
        รับคำตอบ {question_id: score} แล้วคำนวณคะแนนรวมแต่ละหมวด
        คำตอบมีรูปแบบ เช่น {"M_1": 4, "S_3": 5, ...}
        คืนค่า dict ของแต่ละหมวด:
        {
            "M": {"raw": 75, "percentage": 75.0, "max": 100},
            ...
        }
        """
        category_scores: dict[str, list[int]] = {}
        for qid, score in answers.items():
            cat = qid.split("_")[0]
            if cat in ("M", "S", "L", "H", "A"):
                category_scores.setdefault(cat, []).append(score)

        result = {}
        for cat in ("M", "S", "L", "H", "A"):
            scores = category_scores.get(cat, [])
            raw = sum(scores)
            percentage = (raw / MAX_INTEREST_SCORE_PER_CATEGORY) * 100 if MAX_INTEREST_SCORE_PER_CATEGORY > 0 else 0
            result[cat] = {
                "raw": raw,
                "percentage": round(percentage, 1),
                "max": MAX_INTEREST_SCORE_PER_CATEGORY,
            }
        return result

    @staticmethod
    def get_interest_ranking(interest_scores: dict[str, dict]) -> list[tuple[str, float]]:
        """เรียงลำดับหมวดความสนใจจากมากไปน้อย"""
        return sorted(
            [(cat, data["percentage"]) for cat, data in interest_scores.items()],
            key=lambda x: x[1],
            reverse=True,
        )

    @staticmethod
    def get_top_interest(interest_scores: dict[str, dict]) -> str:
        """คืนหมวดที่มีคะแนนสูงสุด"""
        ranking = ScoringEngine.get_interest_ranking(interest_scores)
        return ranking[0][0] if ranking else "Unknown"

    @staticmethod
    def compute_financial_profile(financial_answers: dict[str, str]) -> dict:
        """
        สร้าง Financial Profile จากคำตอบ F1–F6
        """
        return {
            "F1": financial_answers.get("F1", "medium"),
            "F2": financial_answers.get("F2", "stability"),
            "F3": financial_answers.get("F3", "low"),
            "F4": financial_answers.get("F4", "not_interested"),
            "F5": financial_answers.get("F5", "flexible"),
            "F6": financial_answers.get("F6", "medium"),
        }
