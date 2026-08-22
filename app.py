"""Streamlit app: แบบทดสอบเลือกคณะเรียนต่อจาก Cognitive Functions และความถนัด."""

from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from data import (
    APTITUDE_CATEGORIES,
    BUDGET_LABELS,
    COGNITIVE_FUNCTIONS,
    FUNCTION_ORDER,
    LIKERT_LABELS,
    MBTI_PROFILES,
    MBTI_STACKS,
)
from logic import (
    aptitude_summary,
    derive_mbti,
    financial_summary,
    function_totals,
    logic_expression,
    match_faculties,
    rank_nearby_faculties,
    university_options,
)

st.set_page_config(page_title="UniMatch — เลือกคณะด้วยตรรกศาสตร์", page_icon="🎓", layout="wide")


def ensure_state() -> None:
    st.session_state.setdefault("cognitive_done", False)
    st.session_state.setdefault("aptitude_done", False)
    st.session_state.setdefault("finance_done", False)
    # Streamlit removes a widget key when its page is not rendered.  Keep a
    # separate, non-widget copy so changing pages never resets saved answers.
    st.session_state.setdefault(
        "saved_cognitive_responses",
        {function: [3] * len(item["questions"]) for function, item in COGNITIVE_FUNCTIONS.items()},
    )
    st.session_state.setdefault(
        "saved_aptitude_responses",
        {code: [3] * len(item["questions"]) for code, item in APTITUDE_CATEGORIES.items()},
    )
    st.session_state.setdefault(
        "saved_finance_inputs",
        {
            "budget": "medium",
            "career_goal": "ความมั่นคงและสวัสดิการ",
            "financial_urgency": "ไม่มีภาระเร่งด่วน",
            "bonded_scholarship": "ไม่สนใจ / สนใจเฉพาะทุนมอบเปล่า",
            "travel_constraint": "ยืดหยุ่น ไปเรียนต่างจังหวัดได้",
        },
    )
    st.session_state.setdefault("active_page", "เริ่มต้น")
    st.session_state.setdefault("nav_choice", "เริ่มต้น")


def current_cognitive_responses() -> dict[str, list[int]]:
    return {
        function: [st.session_state[f"cf_{function}_{number}"] for number in range(10)]
        for function in FUNCTION_ORDER
    }


def current_aptitude_responses() -> dict[str, list[int]]:
    return {
        code: [st.session_state[f"apt_{code}_{number}"] for number in range(6)]
        for code in APTITUDE_CATEGORIES
    }


def finance_inputs() -> dict[str, str]:
    """คืนค่าการเงินที่บันทึกไว้ ไม่อิง widget ที่อาจถูก Streamlit ล้าง."""
    return st.session_state.saved_finance_inputs


def current_finance_inputs() -> dict[str, str]:
    return {
        "budget": st.session_state.finance_budget,
        "career_goal": st.session_state.finance_career_goal,
        "financial_urgency": st.session_state.finance_financial_urgency,
        "bonded_scholarship": st.session_state.finance_bonded_scholarship,
        "travel_constraint": st.session_state.finance_travel_constraint,
    }


def render_intro() -> None:
    st.title("🎓 UniMatch: แบบทดสอบเลือกคณะเรียนต่อ")
    st.subheader("ใช้ Cognitive Functions + ความสนใจ/ความถนัด + งบประมาณ เพื่อหาเส้นทางที่น่าไปต่อ")
    st.info(
        "ผลลัพธ์เป็นแนวทางสำรวจตนเอง ไม่ใช่การวินิจฉัยบุคลิกภาพหรือเกณฑ์รับเข้าจริง "
        "ควรตรวจสอบคุณสมบัติ TCAS ค่าเทอม และหลักสูตรจากมหาวิทยาลัยโดยตรงก่อนตัดสินใจ"
    )
    st.markdown(
        """
**วิธีใช้**

1. ทำแบบประเมิน Cognitive Functions 80 ข้อ (8 ฟังก์ชัน × 10 ข้อ)
2. ทำแบบประเมินความสนใจ/ความถนัด 30 ข้อ (5 หมวด × 6 ข้อ)
3. เลือกระดับงบประมาณและเงื่อนไขการเงิน
4. เปิดหน้าสรุปเพื่อดู MBTI, ประพจน์ที่เป็นจริง, และคณะ/มหาวิทยาลัยตัวอย่าง
        """
    )

    st.subheader("หลักตรรกะที่แอปใช้")
    st.latex(r"\mathrm{Dom}=A \iff \forall f\; \mathrm{Score}(A) \geq \mathrm{Score}(f)")
    st.latex(r"(\mathrm{MBTI}_1 \lor \mathrm{MBTI}_2 \lor \cdots)\ \land\ (M > 60\%)\ \Rightarrow\ \text{แนะนำคณะ}")
    st.caption("กรณีคะแนนเสมอ แอปจะแจ้งและใช้คะแนน Auxiliary → Tertiary → Inferior เป็นตัวตัดสินที่ทำซ้ำได้")


def render_cognitive() -> None:
    st.title("ส่วนที่ 1 — Cognitive Functions (80 ข้อ)")
    st.write("ให้คะแนนแต่ละข้อความจาก 1 ถึง 5 ตามความเป็นจริงของคุณ")
    tabs = st.tabs([function for function in FUNCTION_ORDER])
    for function, tab in zip(FUNCTION_ORDER, tabs):
        with tab:
            item = COGNITIVE_FUNCTIONS[function]
            st.subheader(item["name_th"])
            for number, question in enumerate(item["questions"], start=1):
                key = f"cf_{function}_{number - 1}"
                if key not in st.session_state:
                    st.session_state[key] = st.session_state.saved_cognitive_responses[function][number - 1]
                st.select_slider(
                    f"{number}. {question}",
                    options=list(LIKERT_LABELS),
                    format_func=lambda value: LIKERT_LABELS[value],
                    key=key,
                )
    if st.button("บันทึกส่วนที่ 1: Cognitive Functions", type="primary"):
        st.session_state.saved_cognitive_responses = current_cognitive_responses()
        st.session_state.cognitive_done = True
        st.success("บันทึกส่วนที่ 1 แล้ว ใช้ปุ่ม “สรุปผลทั้งหมด” ในเมนูเพื่อดูผล")


def render_aptitude() -> None:
    st.title("ส่วนที่ 2 — ความสนใจและความถนัด (30 ข้อ)")
    st.write("แต่ละหมวดมี 6 ข้อ คะแนนเต็มหมวดละ 30 คะแนน แล้วแปลงเป็นเปอร์เซ็นต์")
    tabs = st.tabs([f"{code}: {item['name']}" for code, item in APTITUDE_CATEGORIES.items()])
    for (code, item), tab in zip(APTITUDE_CATEGORIES.items(), tabs):
        with tab:
            st.subheader(item["name"])
            st.caption(item["short"])
            for number, question in enumerate(item["questions"], start=1):
                key = f"apt_{code}_{number - 1}"
                if key not in st.session_state:
                    st.session_state[key] = st.session_state.saved_aptitude_responses[code][number - 1]
                st.select_slider(
                    f"{number}. {question}",
                    options=list(LIKERT_LABELS),
                    format_func=lambda value: LIKERT_LABELS[value],
                    key=key,
                )
    if st.button("บันทึกส่วนที่ 2: ความสนใจและความถนัด", type="primary"):
        st.session_state.saved_aptitude_responses = current_aptitude_responses()
        st.session_state.aptitude_done = True
        st.success("บันทึกส่วนที่ 2 แล้ว ใช้ปุ่ม “สรุปผลทั้งหมด” ในเมนูเพื่อดูผล")


def render_finance() -> None:
    st.title("ส่วนที่ 3 — การบริหารและการเงิน")
    st.write("เลือกข้อมูลเพื่อกรองตัวอย่างมหาวิทยาลัยให้สอดคล้องกับข้อจำกัดของคุณ")
    saved = st.session_state.saved_finance_inputs
    for widget_key, saved_key in (
        ("finance_budget", "budget"),
        ("finance_career_goal", "career_goal"),
        ("finance_financial_urgency", "financial_urgency"),
        ("finance_bonded_scholarship", "bonded_scholarship"),
        ("finance_travel_constraint", "travel_constraint"),
    ):
        if widget_key not in st.session_state:
            st.session_state[widget_key] = saved[saved_key]
    st.radio(
        "งบประมาณค่าใช้จ่ายทางการศึกษาต่อเทอม",
        options=["low", "medium", "high"],
        format_func=lambda item: {
            "low": "งบน้อย — โดยประมาณไม่เกิน 20,000 บาท/เทอม หรือเน้นทุน/กยศ.",
            "medium": "งบปานกลาง — โดยประมาณ 17,000–45,000 บาท/เทอม",
            "high": "งบมาก — ตั้งแต่ประมาณ 60,000 บาท/เทอม หรือหลักสูตรนานาชาติ/เอกชน",
        }[item],
        key="finance_budget",
    )
    st.selectbox(
        "เป้าหมายหลังเรียนจบที่ให้ความสำคัญมากที่สุด",
        ["ความมั่นคงและสวัสดิการ", "รายได้เร็ว / คืนทุนไว", "อิสระและความเป็นตัวเอง"],
        key="finance_career_goal",
    )
    st.radio("ภาระหลังเรียนจบ", ["มีภาระ ต้องรีบหางาน", "ไม่มีภาระเร่งด่วน"], key="finance_financial_urgency")
    st.radio("ทุนแบบมีเงื่อนไขผูกพัน", ["สนใจมาก", "ไม่สนใจ / สนใจเฉพาะทุนมอบเปล่า"], key="finance_bonded_scholarship")
    st.radio("ข้อจำกัดเรื่องที่อยู่/การเดินทาง", ["จำเป็นต้องเรียนใกล้บ้าน", "ยืดหยุ่น ไปเรียนต่างจังหวัดได้"], key="finance_travel_constraint")
    if st.button("บันทึกส่วนที่ 3: การบริหารและการเงิน", type="primary"):
        st.session_state.saved_finance_inputs = current_finance_inputs()
        st.session_state.finance_done = True
        st.success("บันทึกส่วนที่ 3 แล้ว ใช้ปุ่ม “สรุปผลทั้งหมด” ในเมนูเพื่อดูผล")


def render_financial_summary(summary: dict) -> None:
    """แสดงผลส่วนที่ 3 ทั้งบนหน้าการเงินและหน้าสรุปรวม."""
    st.subheader("ส่วนที่ 3 — สรุปข้อมูลการบริหารและการเงิน")
    left, right = st.columns(2)
    left.metric("ระดับงบประมาณ", summary["budget_label"])
    right.metric("ค่าเทอมที่ใช้วางแผน", summary["tuition_range"])
    st.markdown(f"**แนวทางเลือกสถาบัน:** {summary['planning_focus']}")
    st.markdown("**ผลจากเงื่อนไขที่คุณเลือก**")
    st.dataframe(
        pd.DataFrame(summary["decisions"]).rename(
            columns={"topic": "หัวข้อ", "answer": "คำตอบ", "guidance": "ผลต่อแผนการเงิน"}
        ),
        hide_index=True,
        use_container_width=True,
    )
    st.markdown("**รายการที่ควรทำต่อ**")
    for action in summary["actions"]:
        st.write(f"- {action}")
    st.caption("ค่าเทอมเป็นข้อมูลประมาณการต่อเทอม ยังไม่รวมค่าหอพัก ค่าเดินทาง ค่าครองชีพ และอุปกรณ์")


def render_mbti_explanation(result, scores: dict[str, int]) -> None:
    dominant, auxiliary, tertiary, inferior = result.stack
    profile = MBTI_PROFILES[result.mbti]
    st.subheader("ส่วนที่ 1 — ผล MBTI และลำดับ Cognitive Functions")
    st.metric("ประเภทที่ระบบสรุป", result.mbti)
    st.write(f"**ภาพรวม:** {profile[0]}")
    st.write(f"**จุดเด่น:** {profile[1]}")
    st.write(f"**สิ่งที่ควรระวัง:** {profile[2]}")
    cols = st.columns(4)
    descriptions = {
        "Dominant": "กระบวนการหลักที่ใช้โดยเป็นธรรมชาติและบ่อยที่สุด",
        "Auxiliary": "กระบวนการรองที่ช่วยถ่วงสมดุลและสนับสนุนฟังก์ชันหลัก",
        "Tertiary": "กระบวนการลำดับสามที่พัฒนาเด่นขึ้นตามประสบการณ์",
        "Inferior": "กระบวนการตรงข้ามของ Dominant; มักเป็นพื้นที่ท้าทายและพัฒนาได้",
    }
    for column, role, function in zip(cols, descriptions, (dominant, auxiliary, tertiary, inferior)):
        with column:
            st.markdown(f"**{role}: {function}**")
            st.caption(descriptions[role])
            st.metric("คะแนน", f"{scores[function]} / 50")
    if result.used_tiebreak:
        st.warning("มีคะแนน Dominant หรือ Auxiliary เสมอกัน จึงใช้ลำดับ Tertiary/Inferior เป็นตัวตัดสินผลที่แสดง")

    # อธิบายหลักตรรกศาสตร์ของฟังก์ชันรอง (Aux) ในรูปแบบประพจน์เชิงตรรกะ
    st.subheader("อธิบายหลักตรรกศาสตร์ของฟังก์ชันรอง (Aux) เป็นประพจน์")
    auxiliary_candidates = sorted({stack[1] for stack in MBTI_STACKS.values() if stack[0] == dominant})

    st.markdown(
        f"""
ต่อไปนี้เป็นนิยามสัญกรณ์และประพจน์เชิงตรรกะที่ครบถ้วน เพื่อให้ทุกสัญลักษณ์ถูกกำหนดก่อนใช้งาน:

1. นิยามคะแนน:
   - `Score(f)` = ผลรวมคะแนนของฟังก์ชัน `f` (รวมจากคำตอบ 10 ข้อ)
2. นิยาม Dominant:
   - `Dom = d ⇔ ∀f: Score(d) ≥ Score(f)`  (d เป็นฟังก์ชันที่มีคะแนนสูงสุดหรือเท่ากับสูงสุด)
3. นิยามเซตผู้สมัคร Auxiliary:
   - `CandidateAux(d) = {{ {', '.join(auxiliary_candidates)} }}`
     (เซตของฟังก์ชันที่ปรากฏเป็นตำแหน่ง Auxiliary ใน canonical stacks เมื่อ Dominant = d)
4. กฎการเลือก Auxiliary (ประพจน์หลัก):
   - `Aux = argmax_{a ∈ CandidateAux(d)} Score(a)`
   - เทียบความหมายเชิงประพจน์: `Aux = a* ⇔ (a* ∈ CandidateAux(d)) ∧ (∀a ∈ CandidateAux(d): Score(a*) ≥ Score(a))`
     (เลือกผู้สมัครที่มีคะแนนสูงสุดใน CandidateAux(d))
5. การแก้เสมอ (tie-breaking) — นิยามและขั้นตอนสม่ำเสมอ:
   - หาก `TieSet = { a ∈ CandidateAux(d) | Score(a) = max_{x ∈ CandidateAux(d)} Score(x) }` และ |TieSet| > 1 ให้ทำตามลำดับ:
     a) สำหรับแต่ละ a ∈ TieSet ให้กำหนด `Stack(a)` = canonical stack ที่มี (Dominant=d, Auxiliary=a).
        - (ในระบบ canonical แต่ละคู่ (d,a) ควรแมปไปยัง tertiary และ inferior ที่แน่นอน; หากมีหลาย stack ให้รวมทุก tertiary/ inferior ที่สอดคล้อง)
     b) นิยาม `Tert(a)` = tertiary function ตาม `Stack(a)` และ `Inf(a)` = inferior ตาม `Stack(a)` (หากหลาย ให้ใช้คะแนนสูงสุดของ tertiary/ inferior ที่สอดคล้องเป็นตัวแทน)
     c) เปรียบเทียบ `Score(Tert(a))` ระหว่างสมาชิกใน TieSet — เลือก a ที่มีค่า `Score(Tert(a))` สูงสุด
     d) หากยังเสมอกัน ให้เปรียบเทียบ `Score(Inf(a))` — เลือก a ที่มีค่า `Score(Inf(a))` สูงสุด
     e) หากยังเสมอกันจนถึงขั้นสุดท้าย ให้ใช้กฎ deterministic fallback (เช่น ลำดับความสำคัญคงที่ที่กำหนดไว้ล่วงหน้า หรือการเลือกตามลำดับตัวอักษรของชื่อฟังก์ชัน) เพื่อให้ผลลัพธ์ reproducible
   - ระบบจะตั้ง `used_tiebreak = True` ในผลลัพธ์เมื่อเกิดการใช้ขั้นตอน tie-breaking ใด ๆ
6. นิยามประเภท (Type) โดยประพจน์รวม:
   - `Type = mbti ⇔ (Dom = d) ∧ (Aux = a) ∧ (Tert = t) ∧ (Inf = i)`,
     โดย `t` และ `i` มาจาก canonical stack ที่สอดคล้องกับ (d, a)

ข้อความด้านบนกำหนดสัญกรณ์ทุกตัวที่ใช้ในกฎการเลือก Auxiliary และขั้นตอนการแก้เสมออย่างชัดเจน
        """
    )

    st.code(
        "สรุปเชิงประพจน์:\n"
        f"Dom={dominant} ⇔ ∀f Score({dominant}) ≥ Score(f)\n"
        f"CandidateAux({dominant}) = {{{', '.join(auxiliary_candidates)}}}\n"
        "Aux = argmax_{a ∈ CandidateAux(Dom)} Score(a)\n"
        "Tie-breaking (หากมีหลาย a ที่มีคะแนนเท่ากัน):\n"
        "  1) เลือกตาม Score(Tertiary) ของ stack ที่สอดคล้อง\n"
        "  2) หากยังเสมอ ให้เลือกตาม Score(Inferior)\n"
        "  3) หากยังเสมอ ให้ใช้ deterministic fallback (เช่น priority list หรือการเรียงชื่อ)\n"
        f"Type={result.mbti} ⇔ Dom={dominant} ∧ Aux={auxiliary} ∧ Tert={tertiary} ∧ Inf={inferior}",
        language="text",
    )
    with st.expander("ดูคำอธิบายทั้ง 16 MBTI"):
        for mbti, (title, strength, caution) in MBTI_PROFILES.items():
            st.markdown(f"**{mbti} — {title}:** เด่นเรื่อง {strength}; ควรระวัง {caution}.")
    with st.expander("ดูประพจน์ของ MBTI ทั้ง 16 ประเภท"):
        st.caption("รูปแบบนี้บอก canonical stack ของแต่ละประเภท; แอปหาคะแนน Dominant ก่อน แล้วใช้ Auxiliary แยกสองประเภทที่มี Dominant เดียวกัน")
        for mbti, stack in MBTI_STACKS.items():
            dominant_item, auxiliary_item, tertiary_item, inferior_item = stack
            st.code(
                f"Type={mbti} ⇔ (Dom={dominant_item} ∧ Aux={auxiliary_item} ∧ "
                f"Tert={tertiary_item} ∧ Inf={inferior_item})",
                language="text",
            )


def render_summary() -> None:
    st.title("ส่วนสรุป — ผลทั้ง 3 ส่วน คณะ และมหาวิทยาลัย")
    completed = {
        "ส่วนที่ 1 Cognitive Functions": st.session_state.cognitive_done,
        "ส่วนที่ 2 ความสนใจและความถนัด": st.session_state.aptitude_done,
        "ส่วนที่ 3 การบริหารและการเงิน": st.session_state.finance_done,
    }
    if not all(completed.values()):
        remaining = ", ".join(name for name, is_done in completed.items() if not is_done)
        st.warning(f"กรุณาทำให้ครบก่อนเพื่อดูผลสรุปรวม: {remaining}")
        return

    scores = function_totals(st.session_state.saved_cognitive_responses)
    mbti_result = derive_mbti(scores)
    aptitude = aptitude_summary(st.session_state.saved_aptitude_responses)
    finance = financial_summary(**finance_inputs())
    strongest = sorted(aptitude.items(), key=lambda item: int(item[1]["percent"]), reverse=True)[:2]

    st.subheader("ภาพรวมผลทั้ง 3 ส่วน")
    overview_mbti, overview_aptitude, overview_finance = st.columns(3)
    overview_mbti.metric("1. MBTI", mbti_result.mbti, f"Dominant: {mbti_result.stack[0]}")
    overview_aptitude.metric("2. หมวดที่เด่น", strongest[0][1]["name"], f"{strongest[0][1]['percent']}%")
    overview_finance.metric("3. งบประมาณ", finance["budget_label"], finance["tuition_range"])
    st.caption(f"หมวดรองที่เด่น: {strongest[1][1]['name']} ({strongest[1][1]['percent']}%)")

    render_mbti_explanation(mbti_result, scores)

    st.divider()
    st.subheader("ส่วนที่ 2 — ผลความสนใจและความถนัด")
    aptitude_table = pd.DataFrame(
        [{"รหัส": code, "หมวด": value["name"], "คะแนน / 30": value["total"], "%": value["percent"], "โซน": value["zone"]} for code, value in aptitude.items()]
    )
    st.dataframe(aptitude_table, use_container_width=True, hide_index=True)

    st.divider()
    render_financial_summary(finance)

    st.divider()
    matches = match_faculties(mbti_result.mbti, aptitude)
    st.subheader("คณะที่ผ่านประพจน์ทั้งหมด")
    if matches:
        for index, rule in enumerate(matches, start=1):
            with st.expander(f"{index}. {rule['faculty']}", expanded=index <= 3):
                st.code(logic_expression(rule), language="text")
                details = [
                    {"ประพจน์": f"{item['category']} > {item['minimum']}%", "คะแนนของคุณ": f"{item['actual']}%", "เป็นจริง": "จริง" if item["passed"] else "เท็จ"}
                    for item in rule["condition_results"]
                ]
                st.dataframe(pd.DataFrame(details), hide_index=True, use_container_width=True)
                st.markdown(f"`{mbti_result.mbti} ∈ {{{' ∨ '.join(rule['mbti_set'])}}}` → **จริง**")
                st.markdown("**ตัวอย่างมหาวิทยาลัยภายในงบที่เลือก**")
                for option in university_options(rule["group"], finance["budget"]):
                    st.write(f"- [{BUDGET_LABELS[option['tier']]}] {option['university']} — {option['estimate']}")
    else:
        st.info("ยังไม่มีคณะที่ผ่านทุกประพจน์แบบ strict (`>`). นี่ไม่ได้แปลว่าเรียนไม่ได้ แต่บอกว่าคะแนนยังไม่ผ่านเกณฑ์ตั้งต้นของกฎนี้ครบทุกข้อ")
        st.subheader("คณะที่ใกล้เคียงที่สุด")
        nearby = rank_nearby_faculties(mbti_result.mbti, aptitude)
        st.dataframe(pd.DataFrame([{"คณะ / สาขา": item["faculty"], "ความเข้ากันโดยประมาณ": f"{item['compatibility']}%"} for item in nearby]), hide_index=True, use_container_width=True)

    st.divider()
    report = {
        "mbti": mbti_result.mbti,
        "cognitive_stack": {"dominant": mbti_result.stack[0], "auxiliary": mbti_result.stack[1], "tertiary": mbti_result.stack[2], "inferior": mbti_result.stack[3]},
        "function_scores": scores,
        "aptitude": aptitude,
        "financial_summary": finance,
        "matched_faculties": [item["faculty"] for item in matches],
    }
    st.download_button("ดาวน์โหลดผลลัพธ์ JSON", data=json.dumps(report, ensure_ascii=False, indent=2), file_name="unimatch-result.json", mime="application/json")
    st.caption("ตัวอย่างค่าเทอมเป็นข้อมูลประมาณการจากชุดข้อมูลเริ่มต้นของโปรเจกต์ ไม่รวมค่าครองชีพและอาจเปลี่ยนแปลงได้")


ensure_state()


def navigate_from_menu() -> None:
    st.session_state.active_page = st.session_state.nav_choice


def navigate_to_summary() -> None:
    st.session_state.nav_choice = "สรุปผล"
    st.session_state.active_page = "สรุปผล"


with st.sidebar:
    st.title("UniMatch")
    st.radio(
        "เมนู",
        ["เริ่มต้น", "1. Cognitive Functions", "2. ความถนัด", "3. การเงิน", "สรุปผล"],
        key="nav_choice",
        on_change=navigate_from_menu,
    )
    st.button("📊 สรุปผลทั้งหมด", type="primary", use_container_width=True, on_click=navigate_to_summary)
    st.caption(
        f"ส่วนที่ 1: {'✓' if st.session_state.cognitive_done else '○'} | "
        f"ส่วนที่ 2: {'✓' if st.session_state.aptitude_done else '○'} | "
        f"ส่วนที่ 3: {'✓' if st.session_state.finance_done else '○'}"
    )

page = st.session_state.active_page

if page == "เริ่มต้น":
    render_intro()
elif page == "1. Cognitive Functions":
    render_cognitive()
elif page == "2. ความถนัด":
    render_aptitude()
elif page == "3. การเงิน":
    render_finance()
else:
    render_summary()
