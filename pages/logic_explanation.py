"""Logic Explanation Page — อธิบายหลักการตรรกศาสตร์ของระบบ"""

import streamlit as st
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from logic.logic_engine import LogicEngine


def run():
    st.header("🧠 หลักการตรรกศาสตร์ของระบบ")
    st.caption("ทำความเข้าใจว่าระบบใช้ตรรกศาสตร์อย่างไรในการคัดกรองคณะ")

    st.subheader("1. Proposition (ประพจน์)")
    st.markdown("""
    **ประพจน์** คือ ข้อความที่มีค่าความจริงเป็น **True** หรือ **False** เท่านั้น

    **ตัวอย่างจากระบบ:**
    """)
    st.code("""
P = (M > 65)     # คะแนน M มากกว่า 65% หรือไม่?
Q = (S > 45)     # คะแนน S มากกว่า 45% หรือไม่?
R = (MBTI ∈ {INTJ, INTP})  # MBTI ตรงกับกลุ่มที่กำหนดหรือไม่?
    """)
    st.markdown("""
    | ตัวแปร | ค่า True | ค่า False |
    |--------|----------|-----------|
    | P = M > 65 | M = 70% | M = 50% |
    | Q = S > 45 | S = 55% | S = 30% |
    | R = MBTI ∈ {...} | MBTI = INTP | MBTI = ESFJ |
    """)

    st.divider()
    st.subheader("2. AND (∧)")
    st.markdown("""
    **AND** — ทุกประพจน์ต้องเป็น True ถึงจะได้ True

    **ตัวอย่าง:** `AI = P ∧ Q ∧ R`
    """)

    truth_table = LogicEngine.get_truth_table()
    tt_markdown = "| P | Q | P ∧ Q |\n|---|---|-------|\n"
    for row in truth_table[:4]:
        p_str = "T" if row["P"] else "F"
        q_str = "T" if row["Q"] else "F"
        pq_str = "T" if row["P ∧ Q"] else "F"
        tt_markdown += f"| {p_str} | {q_str} | {pq_str} |\n"
    st.markdown(tt_markdown)

    st.code("""
# ตัวอย่างจริงจากระบบ
P = 70 > 65   # True
Q = 55 > 45   # True
R = "INTP" in ["INTJ", "INTP"]  # True

AI = P and Q and R  # True ✓ คณะนี้แนะนำ
    """)

    st.divider()
    st.subheader("3. OR (∨)")
    st.markdown("""
    **OR** — อย่างน้อย 1 ประพจน์ต้องเป็น True

    **ตัวอย่าง:** ตรวจสอบ MBTI ในกลุ่มที่กำหนด
    """)

    tt_markdown = "| P | Q | P ∨ Q |\n|---|---|-------|\n"
    for row in truth_table[:4]:
        p_str = "T" if row["P"] else "F"
        q_str = "T" if row["Q"] else "F"
        pq_str = "T" if row["P ∨ Q"] else "F"
        tt_markdown += f"| {p_str} | {q_str} | {pq_str} |\n"
    st.markdown(tt_markdown)

    st.code("""
# ตัวอย่างจริง: MBTI ∈ {INTJ, INTP, ISTP, ENTP, ISTJ}
R1 = "INTP" in ["INTJ"]        # False
R2 = "INTP" in ["INTP"]        # True
R3 = "INTP" in ["ISTP"]        # False

MBTI_match = R1 or R2 or R3   # True ✓
    """)

    st.divider()
    st.subheader("4. NOT (¬)")
    st.markdown("""
    **NOT** — กลับค่า True/False
    """)

    st.code("""
P = True
¬P = False

# ตัวอย่าง
has_project = True
no_project = not has_project  # False
    """)

    st.divider()
    st.subheader("5. เงื่อนไขเชิงตรรกะของคณะ")
    st.markdown("""
    รูปแบบมาตรฐานของเงื่อนไขคณะ:

    ```
    (MBTI₁ ∨ MBTI₂ ∨ ...) ∧ (หมวดวิชา₁ > เกณฑ์%) [∧ (หมวดวิชา₂ > เกณฑ์%)]
    ```
    """)

    st.markdown("**ตัวอย่างจริง: วิศวกรรมคอมพิวเตอร์ / ซอฟต์แวร์**")
    st.code("""
# MBTI Condition
mbti_set = ["INTJ", "INTP", "ISTP", "ENTP", "ISTJ"]
R = "INTP" in mbti_set  # True (ถ้าผู้ใช้เป็น INTP)

# Academic Condition
P = (M >= 60)  # M = 70% → True

# Final Condition
Faculty_OK = R and P  # True ✓ ผ่านเงื่อนไข
    """)

    st.divider()
    st.subheader("6. Financial Logic")
    st.markdown("""
    ปัจจัยทางการเงินใช้ทั้ง **Filter** และ **Score**:

    - **Filter (F1, F5, F6):** ป้องกันการแนะนำคณะที่เกินงบประมาณ
    - **Score (F2, F3, F4):** เพิ่ม/ลดคะแนนความเหมาะสม
    """)

    st.code("""
# Financial Filter
B = (งบประมาณ >= ค่าเทอมคณะ)
D = (สถานที่เรียนเหมาะกับข้อจำกัด)
F_OK = B and D

# Financial Score
F2_score = คำนวณจากเป้าหมายหลังเรียนจบ
F3_score = คำนวณจากภาระทางการเงิน
    """)

    st.divider()
    st.subheader("7. Match % Calculation")
    st.code("""
Academic_Match  = คำนวณจากคะแนนหมวดวิชา vs เกณฑ์
MBTI_Match      = 100% ถ้าตรง / 30% ถ้าไม่ตรง
Financial_Match = คำนวณจาก F1-F6
Logical_Match   = 90% ถ้ามีโครงงาน / 50% ถ้าไม่มี

Overall_Match = Academic × 0.35 + MBTI × 0.25 + Financial × 0.25 + Logical × 0.15
Overall_Match = min(max(Overall_Match, 0), 100)  # Cap 0-100%
    """)

    st.divider()
    st.subheader("8. ตัวอย่างผลลัพธ์จริง")
    engine = LogicEngine()

    P = engine.evaluate_condition(70, ">=", 65)
    Q = engine.evaluate_condition(55, ">=", 45)
    R = engine.evaluate_mbti_condition("INTP", ["INTJ", "INTP", "ISTP", "ENTP", "ISTJ"])
    AND_result = engine.AND(P, Q, R)

    st.markdown("**ตัวอย่าง: วิศวกรรมคอมพิวเตอร์**")
    st.markdown(engine.format_proposition_result(P))
    st.markdown(engine.format_proposition_result(Q))
    st.markdown(engine.format_proposition_result(R))
    st.divider()
    st.markdown(f"**ผลลัพธ์: {AND_result.name} = {'True ✅ ผ่านเงื่อนไข' if AND_result.value else 'False ❌ ไม่ผ่านเงื่อนไข'}**")

    st.divider()
    st.subheader("📊 Truth Table สมบูรณ์")
    st.markdown("| P | Q | P ∧ Q | P ∨ Q | ¬P |")
    st.markdown("|---|---|-------|-------|-----|")
    for row in truth_table:
        p_str = "T" if row["P"] else "F"
        q_str = "T" if row["Q"] else "F"
        st.markdown(f"| {p_str} | {q_str} | {'T' if row['P ∧ Q'] else 'F'} | {'T' if row['P ∨ Q'] else 'F'} | {'T' if row['¬P'] else 'F'} |")
