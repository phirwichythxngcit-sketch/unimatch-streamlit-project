"""MBTI Cognitive Functions Engine — คำนวณ MBTI จากคะแนน Cognitive Functions"""

MBTI_FUNCTION_STACKS = {
    "INTJ": ["Ni", "Te", "Fi", "Se"],
    "INTP": ["Ti", "Ne", "Si", "Fe"],
    "ENTJ": ["Te", "Ni", "Se", "Fi"],
    "ENTP": ["Ne", "Ti", "Fe", "Si"],
    "INFJ": ["Ni", "Fe", "Ti", "Se"],
    "INFP": ["Fi", "Ne", "Si", "Te"],
    "ENFJ": ["Fe", "Ni", "Se", "Ti"],
    "ENFP": ["Ne", "Fi", "Te", "Si"],
    "ISTJ": ["Si", "Te", "Fi", "Ne"],
    "ISFJ": ["Si", "Fe", "Ti", "Ne"],
    "ESTJ": ["Te", "Si", "Ne", "Fi"],
    "ESFJ": ["Fe", "Si", "Ne", "Ti"],
    "ISTP": ["Ti", "Se", "Ni", "Fe"],
    "ISFP": ["Fi", "Se", "Ni", "Te"],
    "ESTP": ["Se", "Ti", "Fe", "Ni"],
    "ESFP": ["Se", "Fi", "Te", "Ni"],
}

FUNCTION_PAIRS = {
    "Ti": "Te", "Te": "Ti",
    "Fe": "Fi", "Fi": "Fe",
    "Se": "Si", "Si": "Se",
    "Ne": "Ni", "Ni": "Ne",
}

THINKING_FUNCTIONS = {"Ti", "Te"}
FEELING_FUNCTIONS = {"Fe", "Fi"}
SENSING_FUNCTIONS = {"Se", "Si"}
INTUITION_FUNCTIONS = {"Ne", "Ni"}


class MBTIEngine:
    """คำนวณ MBTI จากคะแนน Cognitive Functions 8 ด้าน"""

    @staticmethod
    def compute_function_scores(answers: dict[str, int]) -> dict[str, int]:
        """
        รับคำตอบ {question_id: score} แล้วคำนวณคะแนนรวมของแต่ละ Function
        คำตอบมีรูปแบบ เช่น {"Ti_1": 4, "Ti_2": 5, ...}
        """
        scores: dict[str, list[int]] = {}
        for qid, score in answers.items():
            func = qid.split("_")[0]
            if func in ("Ti", "Te", "Fe", "Fi", "Se", "Si", "Ne", "Ni"):
                scores.setdefault(func, []).append(score)
        return {func: sum(vals) for func, vals in scores.items()}

    @staticmethod
    def determine_mbti(function_scores: dict[str, int]) -> str:
        """
        กำหนด MBTI type จากคะแนน Cognitive Functions
        ใช้ ranked function stack เทียบกับ MBTI 16 ประเภท
        """
        if not function_scores or len(function_scores) < 8:
            return "Unknown"

        sorted_funcs = sorted(function_scores.keys(), key=lambda f: function_scores[f], reverse=True)
        dominant = sorted_funcs[0]
        auxiliary = sorted_funcs[1]

        best_type = None
        best_score = -1

        for mbti_type, stack in MBTI_FUNCTION_STACKS.items():
            score = 0
            if stack[0] == dominant:
                score += 3
            if stack[1] == auxiliary:
                score += 2
            for i, f in enumerate(stack[:2]):
                if f in sorted_funcs[:4]:
                    score += (3 - i)
            if score > best_score:
                best_score = score
                best_type = mbti_type

        return best_type or "Unknown"

    @staticmethod
    def get_function_ranking(function_scores: dict[str, int]) -> list[tuple[str, int]]:
        """เรียงลำดับ Cognitive Functions จากมากไปน้อย"""
        return sorted(function_scores.items(), key=lambda x: x[1], reverse=True)

    @staticmethod
    def get_mbti_description(mbti_type: str) -> dict:
        """คืนคำอธิบาย MBTI type"""
        descriptions = {
            "INTJ": {"name": "The Architect", "name_th": "นักออกแบบ", "desc": "มีวิสัยทัศน์ ชอบวางแผนระยะยาว ใช้ตรรกะในการตัดสินใจ"},
            "INTP": {"name": "The Logician", "name_th": "นักตรรกศาสตร์", "desc": "ชอบวิเคราะห์ รักการเรียนรู้ ชื่นชอบทฤษฎีและความคิดเชิงนามธรรม"},
            "ENTJ": {"name": "The Commander", "name_th": "ผู้บัญชาการ", "desc": "เป็นผู้นำโดยธรรมชาติ กล้าตัดสินใจ มีเป้าหมายชัดเจน"},
            "ENTP": {"name": "The Debater", "name_th": "นักถกเถียง", "desc": "ชอบท้าทาย มองเห็นความเป็นไปได้ ชอบแลกเปลี่ยนความคิด"},
            "INFJ": {"name": "The Advocate", "name_th": "ผู้พิทักษ์", "desc": "มีอุดมคติ เข้าใจผู้อื่นลึกซึ้ง มองเห็นภาพรวมในอนาคต"},
            "INFP": {"name": "The Mediator", "name_th": "ผู้ไกล่เกลี่ย", "desc": "มีคุณค่าส่วนตัวชัดเจน รักอิสระ เห็นอกเห็นใจผู้อื่น"},
            "ENFJ": {"name": "The Protagonist", "name_th": "ตัวเอก", "desc": "มีเสน่ห์ สร้างแรงบันดาลใจ ใส่ใจผู้อื่น"},
            "ENFP": {"name": "The Campaigner", "name_th": "นักรณรงค์", "desc": "รักอิสระ สร้างสรรค์ มองเห็นความเป็นไปได้รอบตัว"},
            "ISTJ": {"name": "The Logistician", "name_th": "นักตรรกศาสตร์ภาคสนาม", "desc": "จริงจัง เชื่อถือได้ ชอบระบบระเบียบและขั้นตอน"},
            "ISFJ": {"name": "The Defender", "name_th": "ผู้ป้องกัน", "desc": "อบอุ่น ใส่ใจรายละเอียด รักษาประเพณี"},
            "ESTJ": {"name": "The Executive", "name_th": "ผู้บริหาร", "desc": "มีระบบระเบียบ ตัดสินใจเด็ดขาด จัดการเก่ง"},
            "ESFJ": {"name": "The Consul", "name_th": "ที่ปรึกษา", "desc": "ใส่ใจผู้อื่น ชอบช่วยเหลือ รักษาความกลมเกลียว"},
            "ISTP": {"name": "The Virtuoso", "name_th": "ช่างฝีมือ", "desc": "คล่องแคล่ว ชอบลงมือทำ แก้ปัญหาเฉพาะหน้าเก่ง"},
            "ISFP": {"name": "The Adventurer", "name_th": "นักผจญภัย", "desc": "อ่อนโยน สร้างสรรค์ รักศิลปะและความงาม"},
            "ESTP": {"name": "The Entrepreneur", "name_th": "ผู้ประกอบการ", "desc": "กระฉับกระเฉง กล้าเสี่ยง ชอบความท้าทาย"},
            "ESFP": {"name": "The Entertainer", "name_th": "นักแสดง", "desc": "สนุกสนาน มีชีวิตชีวา ชอบอยู่กับผู้คน"},
        }
        return descriptions.get(mbti_type, {"name": "Unknown", "name_th": "ไม่ทราบ", "desc": "ไม่พบข้อมูล"})
