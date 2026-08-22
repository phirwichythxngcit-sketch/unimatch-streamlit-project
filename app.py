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
    function_totals,
    logic_expression,
    match_faculties,
    rank_nearby_faculties,
    university_options,
)
from response_state import answer_key, initialize_answer_store, persist_widget_value, widget_key

st.set_page_config(page_title="UniMatch — เลือกคณะด้วยตรรกศาสตร์", page_icon="🎓", layout="wide")

APTITUDE_QUESTION_COUNT = len(next(iter(APTITUDE_CATEGORIES.values()))["questions"])
APTITUDE_MAX_SCORE = APTITUDE_QUESTION_COUNT * max(LIKERT_LABELS)
APTITUDE_TOTAL_QUESTIONS = sum(len(item["questions"]) for item in APTITUDE_CATEGORIES.values())
COGNITIVE_ANSWER_STORE = "cognitive_answers"
APTITUDE_ANSWER_STORE = "aptitude_answers"


def ensure_state() -> None:
    st.session_state.setdefault("cognitive_done", False)
    st.session_state.setdefault("aptitude_done", False)
    st.session_state.setdefault("budget", "medium")
    initialize_answer_store(
        st.session_state,
        COGNITIVE_ANSWER_STORE,
        (
            answer_key("cf", function, number)
            for function, item in COGNITIVE_FUNCTIONS.items()
            for number in range(len(item["questions"]))
        ),
    )
    initialize_answer_store(
        st.session_state,
        APTITUDE_ANSWER_STORE,
        (
            answer_key("apt", code, number)
            for code, item in APTITUDE_CATEGORIES.items()
            for number in range(len(item["questions"]))
        ),
    )


def cognitive_responses() -> dict[str, list[int]]:
    return {
        function: [
            st.session_state[COGNITIVE_ANSWER_STORE][answer_key("cf", function, number)]
            for number in range(len(COGNITIVE_FUNCTIONS[function]["questions"]))
        ]
        for function in FUNCTION_ORDER
    }


def aptitude_responses() -> dict[str, list[int]]:
    return {
        code: [
            st.session_state[APTITUDE_ANSWER_STORE][answer_key("apt", code, number)]
            for number in range(len(item["questions"]))
        ]
        for code, item in APTITUDE_CATEGORIES.items()
    }


def persist_answer(store_name: str, saved_key: str, input_key: str) -> None:
    """Save an answer before Streamlit removes the widget during navigation."""
    persist_widget_value(st.session_state, store_name, saved_key, input_key)


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
2. ทำแบบประเมินความสนใจ/ความถนัด 100 ข้อ (5 หมวด × 20 ข้อ)
3. เลือกระดับทุน/งบประมาณที่มี
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
                saved_key = answer_key("cf", function, number - 1)
                input_key = widget_key(saved_key)
                st.select_slider(
                    f"{number}. {question}",
                    options=list(LIKERT_LABELS),
                    format_func=lambda value: LIKERT_LABELS[value],
                    value=st.session_state[COGNITIVE_ANSWER_STORE][saved_key],
                    key=input_key,
                    on_change=persist_answer,
                    args=(COGNITIVE_ANSWER_STORE, saved_key, input_key),
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
    st.title(f"ส่วนที่ 2 — ความสนใจและความถนัด ({APTITUDE_TOTAL_QUESTIONS} ข้อ)")
    st.write(f"แต่ละหมวดมี {APTITUDE_QUESTION_COUNT} ข้อ คะแนนเต็มหมวดละ {APTITUDE_MAX_SCORE} คะแนน แล้วแปลงเป็นเปอร์เซ็นต์")
    tabs = st.tabs([f"{code}: {item['name']}" for code, item in APTITUDE_CATEGORIES.items()])
    for (code, item), tab in zip(APTITUDE_CATEGORIES.items(), tabs):
        with tab:
            st.subheader(item["name"])
            st.caption(item["short"])
            for number, question in enumerate(item["questions"], start=1):
                saved_key = answer_key("apt", code, number - 1)
                input_key = widget_key(saved_key)
                st.select_slider(
                    f"{number}. {question}",
                    options=list(LIKERT_LABELS),
                    format_func=lambda value: LIKERT_LABELS[value],
                    value=st.session_state[APTITUDE_ANSWER_STORE][saved_key],
                    key=input_key,
                    on_change=persist_answer,
                    args=(APTITUDE_ANSWER_STORE, saved_key, input_key),
                )
    if st.button("สรุปผลความสนใจและความถนัด", type="primary"):
        st.session_state.aptitude_done = True
        st.success("บันทึกผลแล้ว เปิดหน้าสรุปเพื่อดูเปอร์เซ็นต์และคณะที่ตรงเงื่อนไข")
    if st.session_state.aptitude_done:
        summary = aptitude_summary(aptitude_responses())
        st.dataframe(
            pd.DataFrame(summary.values()).rename(columns={"name": "หมวด", "total": f"คะแนน / {APTITUDE_MAX_SCORE}", "percent": "%", "zone": "การแปลผล"}),
            use_container_width=True,
            hide_index=True,
        )


def render_finance() -> None:
    st.title("ส่วนที่ 3 — ทุนและงบประมาณ")
    st.write("เลือกช่วงทุนหรือเงินที่มีโดยประมาณ เพื่อกรองตัวอย่างมหาวิทยาลัยให้เหมาะกับงบของคุณ")
    st.session_state.budget = st.radio(
        "คุณมีทุนหรือเงินสำหรับค่าใช้จ่ายทางการศึกษาต่อเทอมอยู่ประมาณไหน?",
        options=["low", "medium", "high"],
        format_func=lambda item: {
            "low": "งบน้อย — ต้องการตัวเลือกค่าใช้จ่ายต่ำ หรือใช้ทุน/กยศ.",
            "medium": "งบปานกลาง — เลือกได้ทั้งมหาวิทยาลัยรัฐและหลักสูตรทั่วไป",
            "high": "งบมาก — เปิดกว้างสำหรับหลักสูตรค่าใช้จ่ายสูง",
        }[item],
    )
    st.success("ระบบจะใช้คำตอบนี้เพื่อแสดงตัวอย่างมหาวิทยาลัยที่อยู่ในระดับงบของคุณ")

def render_mbti_explanation(result, scores: dict[str, int]) -> None:
    dominant, auxiliary, tertiary, inferior = result.stack
    profile = MBTI_PROFILES[result.mbti]
    st.title("ผล MBTI และลำดับ Cognitive Functions")
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

    st.subheader("ตรรกศาสตร์: เงื่อนไขหา MBTI (Dom → Aux → Tert → Inf)")
    st.markdown(
        """
ให้คิดว่า MBTI แต่ละประเภทเป็น “ชุดลำดับ” ของ 4 ตำแหน่ง ได้แก่ Dominant (Dom),
Auxiliary (Aux), Tertiary (Tert) และ Inferior (Inf) ระบบเลือกชุดที่มีเงื่อนไขครบที่สุด

กำหนดให้ `T` คือ MBTI ตัวเลือกหนึ่ง และ `U` คือตัวเลือกอื่นที่กำลังเปรียบเทียบ

- `P_D(T)`: คะแนน Dom ของ T สูงที่สุดในทุกฟังก์ชัน
- `P_A(T)`: เมื่อ Dom เท่ากัน คะแนน Aux ของ T สูงกว่าหรือเท่ากับ Aux ของ U
- `P_T(T)`: ถ้า Dom และ Aux ยังเท่ากัน คะแนน Tert ของ T สูงกว่าหรือเท่ากับ Tert ของ U
- `P_I(T)`: ถ้า Dom, Aux และ Tert ยังเท่ากัน คะแนน Inf ของ T สูงกว่าหรือเท่ากับ Inf ของ U

จึงสรุปเงื่อนไขของตัวเลือก T ได้ว่า

`MBTI = T ⇔ P_D(T) ∧ P_A(T) ∧ P_T(T) ∧ P_I(T)`

อ่านว่า “ผลเป็น MBTI ประเภท T ก็ต่อเมื่อเงื่อนไขของ Dom, Aux, Tert และ Inf ของ T เป็นจริงครบ”
โดยระบบเปรียบเทียบตามลำดับ **Dom → Aux → Tert → Inf**: ตำแหน่งก่อนหน้ามีความสำคัญกว่า
ตำแหน่งถัดไป และจะดูตำแหน่งถัดไปเมื่อคะแนนก่อนหน้ายังเสมอกันเท่านั้น
        """
    )
    st.code(
        "P_D(T): Score(Dom_T) = คะแนนสูงสุด\n"
        "P_A(T): Dom เสมอ → Score(Aux_T) ≥ Score(Aux_U)\n"
        "P_T(T): Dom และ Aux เสมอ → Score(Tert_T) ≥ Score(Tert_U)\n"
        "P_I(T): Dom, Aux และ Tert เสมอ → Score(Inf_T) ≥ Score(Inf_U)\n\n"
        "MBTI = T ⇔ P_D(T) ∧ P_A(T) ∧ P_T(T) ∧ P_I(T)",
        language="text",
    )
    with st.expander("ดูคำอธิบายทั้ง 16 MBTI"):
        for mbti, (title, strength, caution) in MBTI_PROFILES.items():
            st.markdown(f"**{mbti} — {title}:** เด่นเรื่อง {strength}; ควรระวัง {caution}.")
    with st.expander("ดูประพจน์ของ MBTI ทั้ง 16 ประเภท"):
        st.caption("แต่ละบรรทัดเป็นรูปแบบของ MBTI หนึ่งประเภท โดยผลจะเป็นประเภทนั้นเมื่อเงื่อนไข Dom, Aux, Tert และ Inf สอดคล้องกันครบ")
        for mbti, stack in MBTI_STACKS.items():
            dominant_item, auxiliary_item, tertiary_item, inferior_item = stack
            st.code(
                f"Type={mbti} ⇔ (Dom={dominant_item} ∧ Aux={auxiliary_item} ∧ "
                f"Tert={tertiary_item} ∧ Inf={inferior_item})",
                language="text",
            )


def render_summary() -> None:
    st.title("ส่วนสรุป — ประพจน์ คณะที่ตรงเงื่อนไข และมหาวิทยาลัย")
    if not (st.session_state.cognitive_done and st.session_state.aptitude_done):
        st.warning("กรุณาทำส่วนที่ 1 และส่วนที่ 2 ให้เสร็จก่อน จึงจะสรุปผลแบบครบถ้วนได้")
        return

    scores = function_totals(cognitive_responses())
    mbti_result = derive_mbti(scores)
    aptitude = aptitude_summary(aptitude_responses())
    render_mbti_explanation(mbti_result, scores)

    st.divider()
    st.subheader("ผลความสนใจและความถนัด")
    aptitude_table = pd.DataFrame(
        [
            {
                "รหัส": code,
                "หมวด": value["name"],
                f"คะแนน / {APTITUDE_MAX_SCORE}": value["total"],
                "%": value["percent"],
                "โซน": value["zone"],
            }
            for code, value in aptitude.items()
        ]
    )
    st.dataframe(aptitude_table, use_container_width=True, hide_index=True)

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
        "budget": st.session_state.budget,
        "matched_faculties": [item["faculty"] for item in matches],
    }
    st.download_button("ดาวน์โหลดผลลัพธ์ JSON", data=json.dumps(report, ensure_ascii=False, indent=2), file_name="unimatch-result.json", mime="application/json")
    st.caption("ตัวอย่างค่าเทอมเป็นข้อมูลประมาณการจากชุดข้อมูลเริ่มต้นของโปรเจกต์ ไม่รวมค่าครองชีพและอาจเปลี่ยนแปลงได้")


ensure_state()
with st.sidebar:
    st.title("UniMatch")
    page = st.radio("เมนู", ["เริ่มต้น", "1. Cognitive Functions", "2. ความถนัด", "3. ทุนและงบประมาณ", "สรุปผล"])
    st.caption(f"Cognitive: {'✓' if st.session_state.cognitive_done else '○'} | ความถนัด: {'✓' if st.session_state.aptitude_done else '○'}")

if page == "เริ่มต้น":
    render_intro()
elif page == "1. Cognitive Functions":
    render_cognitive()
elif page == "2. ความถนัด":
    render_aptitude()
elif page == "3. ทุนและงบประมาณ":
    render_finance()
else:
    render_summary()
