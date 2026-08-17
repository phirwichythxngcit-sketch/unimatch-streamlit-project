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
    st.session_state.setdefault("budget", "medium")
    st.session_state.setdefault("career_goal", "ความมั่นคงและสวัสดิการ")
    st.session_state.setdefault("financial_urgency", "ไม่มีภาระเร่งด่วน")
    st.session_state.setdefault("bonded_scholarship", "ไม่สนใจ / สนใจเฉพาะทุนมอบเปล่า")
    st.session_state.setdefault("travel_constraint", "ยืดหยุ่น ไปเรียนต่างจังหวัดได้")
    for function, item in COGNITIVE_FUNCTIONS.items():
        for number in range(len(item["questions"])):
            st.session_state.setdefault(f"cf_{function}_{number}", 3)
    for code, item in APTITUDE_CATEGORIES.items():
        for number in range(len(item["questions"])):
            st.session_state.setdefault(f"apt_{code}_{number}", 3)


def cognitive_responses() -> dict[str, list[int]]:
    return {
        function: [st.session_state[f"cf_{function}_{number}"] for number in range(10)]
        for function in FUNCTION_ORDER
    }


def aptitude_responses() -> dict[str, list[int]]:
    return {
        code: [st.session_state[f"apt_{code}_{number}"] for number in range(6)]
        for code in APTITUDE_CATEGORIES
    }


def finance_inputs() -> dict[str, str]:
    return {
        "budget": st.session_state.budget,
        "career_goal": st.session_state.career_goal,
        "financial_urgency": st.session_state.financial_urgency,
        "bonded_scholarship": st.session_state.bonded_scholarship,
        "travel_constraint": st.session_state.travel_constraint,
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
4. เปิดหน้าสรุปเพื่อดู MBTI, ประพจน์ที่เป็นจริง และคณะ/มหาวิทยาลัยตัวอย่าง
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
                st.select_slider(
                    f"{number}. {question}",
                    options=list(LIKERT_LABELS),
                    format_func=lambda value: LIKERT_LABELS[value],
                    key=f"cf_{function}_{number - 1}",
                )
    if st.button("คำนวณผล Cognitive Functions", type="primary"):
        st.session_state.cognitive_done = True
        st.success("บันทึกผลแล้ว เปิดหน้าสรุป MBTI เพื่อดูผลได้เลย")
    if st.session_state.cognitive_done:
        scores = function_totals(cognitive_responses())
        result = derive_mbti(scores)
        st.subheader(f"ผลเบื้องต้น: {result.mbti}")
        st.dataframe(
            pd.DataFrame([{"Function": function, "คะแนน / 50": scores[function]} for function in FUNCTION_ORDER])
            .sort_values("คะแนน / 50", ascending=False),
            use_container_width=True,
            hide_index=True,
        )


def render_aptitude() -> None:
    st.title("ส่วนที่ 2 — ความสนใจและความถนัด (30 ข้อ)")
    st.write("แต่ละหมวดมี 6 ข้อ คะแนนเต็มหมวดละ 30 คะแนน แล้วแปลงเป็นเปอร์เซ็นต์")
    tabs = st.tabs([f"{code}: {item['name']}" for code, item in APTITUDE_CATEGORIES.items()])
    for (code, item), tab in zip(APTITUDE_CATEGORIES.items(), tabs):
        with tab:
            st.subheader(item["name"])
            st.caption(item["short"])
            for number, question in enumerate(item["questions"], start=1):
                st.select_slider(
                    f"{number}. {question}",
                    options=list(LIKERT_LABELS),
                    format_func=lambda value: LIKERT_LABELS[value],
                    key=f"apt_{code}_{number - 1}",
                )
    if st.button("สรุปผลความสนใจและความถนัด", type="primary"):
        st.session_state.aptitude_done = True
        st.success("บันทึกผลแล้ว เปิดหน้าสรุปเพื่อดูเปอร์เซ็นต์และคณะที่ตรงเงื่อนไข")
    if st.session_state.aptitude_done:
        summary = aptitude_summary(aptitude_responses())
        st.dataframe(
            pd.DataFrame(summary.values()).rename(columns={"name": "หมวด", "total": "คะแนน / 30", "percent": "%", "zone": "การแปลผล"}),
            use_container_width=True,
            hide_index=True,
        )


def render_finance() -> None:
    st.title("ส่วนที่ 3 — การบริหารและการเงิน")
    st.write("เลือกข้อมูลเพื่อกรองตัวอย่างมหาวิทยาลัยให้สอดคล้องกับข้อจำกัดของคุณ")
    st.radio(
        "งบประมาณค่าใช้จ่ายทางการศึกษาต่อเทอม",
        options=["low", "medium", "high"],
        format_func=lambda item: {
            "low": "งบน้อย — โดยประมาณไม่เกิน 20,000 บาท/เทอม หรือเน้นทุน/กยศ.",
            "medium": "งบปานกลาง — โดยประมาณ 17,000–45,000 บาท/เทอม",
            "high": "งบมาก — ตั้งแต่ประมาณ 60,000 บาท/เทอม หรือหลักสูตรนานาชาติ/เอกชน",
        }[item],
        key="budget",
    )
    st.selectbox(
        "เป้าหมายหลังเรียนจบที่ให้ความสำคัญมากที่สุด",
        ["ความมั่นคงและสวัสดิการ", "รายได้เร็ว / คืนทุนไว", "อิสระและความเป็นตัวเอง"],
        key="career_goal",
    )
    st.radio("ภาระหลังเรียนจบ", ["มีภาระ ต้องรีบหางาน", "ไม่มีภาระเร่งด่วน"], key="financial_urgency")
    st.radio("ทุนแบบมีเงื่อนไขผูกพัน", ["สนใจมาก", "ไม่สนใจ / สนใจเฉพาะทุนมอบเปล่า"], key="bonded_scholarship")
    st.radio("ข้อจำกัดเรื่องที่อยู่/การเดินทาง", ["จำเป็นต้องเรียนใกล้บ้าน", "ยืดหยุ่น ไปเรียนต่างจังหวัดได้"], key="travel_constraint")
    if st.button("บันทึกและสรุปแผนการเงิน", type="primary"):
        st.session_state.finance_done = True
        st.success("บันทึกข้อมูลการเงินแล้ว หน้าสรุปผลจะแสดงทั้ง 3 ส่วน")
    if st.session_state.finance_done:
        render_financial_summary(financial_summary(**finance_inputs()))


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

    st.subheader("อธิบายตรรกศาสตร์ที่ใช้หา MBTI")
    st.markdown(
        f"""
1. กำหนด `Score(f)` เป็นคะแนนรวมของ function `f` จากคำตอบ 10 ข้อ
2. `Dom = {dominant}` เป็นจริง เพราะ `{scores[dominant]}` เป็นค่าสูงสุดของทุก function
3. เมื่อ `Dom = {dominant}` ประเภทที่เป็นไปได้จะถูกจำกัดเหลือสอง stack ที่มี Dominant เดียวกัน แล้วเปรียบเทียบ Auxiliary
4. ผลที่เลือกคือ `{result.mbti}` มี stack `{dominant} → {auxiliary} → {tertiary} → {inferior}` และใช้กฎคู่ตรงข้าม: Dominant กับ Inferior เป็นคู่แกนเดียวกัน (เช่น `Ne ⇔ Si`, `Ni ⇔ Se`, `Te ⇔ Fi`, `Ti ⇔ Fe`)
        """
    )
    st.code(
        f"Dom={dominant} ⇔ ∀f Score({dominant}) ≥ Score(f)\n"
        f"Dom={dominant} ⇒ Aux ∈ {{…}}\n"
        f"Type={result.mbti} ⇒ {dominant} → {auxiliary} → {tertiary} → {inferior}",
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

    scores = function_totals(cognitive_responses())
    mbti_result = derive_mbti(scores)
    aptitude = aptitude_summary(aptitude_responses())
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
                for option in university_options(rule["group"], st.session_state.budget):
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
with st.sidebar:
    st.title("UniMatch")
    page = st.radio("เมนู", ["เริ่มต้น", "1. Cognitive Functions", "2. ความถนัด", "3. การเงิน", "สรุปผล"])
    st.caption(f"Cognitive: {'✓' if st.session_state.cognitive_done else '○'} | ความถนัด: {'✓' if st.session_state.aptitude_done else '○'}")

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

