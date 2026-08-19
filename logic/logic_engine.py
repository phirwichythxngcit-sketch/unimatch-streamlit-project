"""Logic Engine — ระบบตรรกศาสตร์สำหรับการคัดกรองคณะ

รองรับ: AND (∧), OR (∨), NOT (¬)

ตัวอย่าง:
    P = M > 65
    Q = S > 45
    R = mbti in allowed_mbti
    AI = P ∧ Q ∧ R

"""


class Proposition:
    """แทนประพจน์ (Proposition) ที่มีค่า True/False"""

    def __init__(self, name: str, value: bool, description: str = ""):
        self.name = name
        self.value = value
        self.description = description

    def __repr__(self):
        return f"Proposition({self.name}={self.value})"

    def __str__(self):
        return f"{self.name} = {'True' if self.value else 'False'}"


class LogicEngine:
    """เครื่องยนต์ตรรกศาสตร์สำหรับการคัดกรองคณะ"""

    @staticmethod
    def AND(*props: Proposition) -> Proposition:
        """AND (∧) — ทุกประพจน์ต้องเป็น True"""
        name_parts = " ∧ ".join(p.name for p in props)
        value = all(p.value for p in props)
        return Proposition(name_parts, value, f"AND({', '.join(f'{p.name}={p.value}' for p in props)})")

    @staticmethod
    def OR(*props: Proposition) -> Proposition:
        """OR (∨) — อย่างน้อย 1 ประพจน์ต้องเป็น True"""
        name_parts = " ∨ ".join(p.name for p in props)
        value = any(p.value for p in props)
        return Proposition(name_parts, value, f"OR({', '.join(f'{p.name}={p.value}' for p in props)})")

    @staticmethod
    def NOT(prop: Proposition) -> Proposition:
        """NOT (¬) — กลับค่า True/False"""
        return Proposition(f"¬{prop.name}", not prop.value, f"NOT({prop.name}={prop.value})")

    @staticmethod
    def evaluate_condition(variable: float, operator: str, threshold: float) -> Proposition:
        """
        ประเมินเงื่อนไขเชิงตัวเลข
        เช่น evaluate_condition(70, ">", 65) → Proposition("70.0 > 65", True)
        """
        ops = {
            ">": lambda a, b: a > b,
            ">=": lambda a, b: a >= b,
            "<": lambda a, b: a < b,
            "<=": lambda a, b: a <= b,
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
        }
        func = ops.get(operator)
        if func is None:
            raise ValueError(f"Unknown operator: {operator}")
        value = func(variable, threshold)
        return Proposition(f"{variable} {operator} {threshold}", value)

    @staticmethod
    def evaluate_mbti_condition(mbti: str, allowed_set: list[str]) -> Proposition:
        """ตรวจสอบว่า MBTI type อยู่ในชุดที่กำหนดหรือไม่"""
        value = mbti in allowed_set
        return Proposition(
            f"MBTI ∈ {{{', '.join(allowed_set)}}}",
            value,
        )

    @staticmethod
    def evaluate_academic_condition(score_pct: float, min_pct: float, category: str) -> Proposition:
        """ตรวจสอบว่าคะแนนหมวดวิชาผ่านเกณฑ์ขั้นต่ำหรือไม่"""
        value = score_pct >= min_pct
        return Proposition(
            f"{category} ({score_pct:.1f}%) ≥ {min_pct}%",
            value,
        )

    @staticmethod
    def evaluate_financial_filter(f1_level: str, faculty_cost_level: str) -> Proposition:
        """
        ตรวจสอบ F1 — งบประมาณค่าเทอม
        ใช้ Filter (ไม่ใช่ Score)
        """
        level_order = {"low": 0, "medium": 1, "high": 2}
        cost_order = {"low": 0, "medium": 1, "high": 2}
        user_level = level_order.get(f1_level, 1)
        cost = cost_order.get(faculty_cost_level, 1)
        value = user_level >= cost
        return Proposition(
            f"F1 ({f1_level}) ≥ ค่าเทอม ({faculty_cost_level})",
            value,
        )

    @staticmethod
    def get_truth_table() -> list[dict]:
        """คืน Truth Table สำหรับ AND, OR, NOT"""
        table = []
        for p in [True, False]:
            for q in [True, False]:
                table.append({
                    "P": p, "Q": q,
                    "P ∧ Q": p and q,
                    "P ∨ Q": p or q,
                    "¬P": not p,
                })
        return table

    @staticmethod
    def format_proposition_result(prop: Proposition) -> str:
        """จัดรูปแบบผลลัพธ์ประพจน์"""
        icon = "✅" if prop.value else "❌"
        return f"{icon} {prop.name} = {'True' if prop.value else 'False'}"
