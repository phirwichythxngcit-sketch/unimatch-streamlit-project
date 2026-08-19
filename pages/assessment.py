"""Assessment Page — แบบประเมิน MBTI + ความสนใจ + การเงิน"""

import streamlit as st
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from logic.mbti_engine import MBTIEngine
from logic.scoring import ScoringEngine
from logic.faculty_matcher import FacultyMatcher
from logic.database import Database

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def load_questions():
    with open(os.path.join(DATA_DIR, "questions.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def load_interest_questions():
    with open(os.path.join(DATA_DIR, "interest_questions.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def load_financial_questions():
    with open(os.path.join(DATA_DIR, "financial_questions.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def run():
    st.header("📋 แบบประเมิน")
    st.caption("ทำแบบสอบถาม 3 ขั้นตอน: MBTI → ความสนใจ → การเงิน")

    if "step" not in st.session_state:
        st.session_state.step = "start"
    if "mbti_answers" not in st.session_state:
        st.session_state.mbti_answers = {}
    if "interest_answers" not in st.session_state:
        st.session_state.interest_answers = {}
    if "financial_answers" not in st.session_state:
        st.session_state.financial_answers = {}
    if "current_question" not in st.session_state:
        st.session_state.current_question = 0

    step = st.session_state.step

    if step == "start":
        render_start()
    elif step == "mbti":
        render_mbti()
    elif step == "mbti_result":
        render_mbti_result()
    elif step == "interest":
        render_interest()
    elif step == "financial":
        render_financial()
    elif step == "result":
        render_final_result()


def render_start():
    st.subheader("ยินดีต้อนรับสู่แบบประเมิน")
    st.markdown("""
    แบบประเมินนี้ประกอบด้วย **3 ส่วน**:

    1. **แบบสอบถาม MBTI (Cognitive Functions)** — 80 ข้อ
    2. **แบบสำรวจความสนใจและความถนัด** — 100 ข้อ
    3. **แบบสอบถามปัจจัยทางการเงิน** — 6 ปัจจัย

    **เวลาที่ใช้:** ประมาณ 20–30 นาที

    > ⚠️ ผลลัพธ์เป็นการประเมินเพื่อการสำรวจตนเอง ไม่ใช่การวินิจฉัยทางจิตวิทยา
    """)

    st.info("💡 คะแนนแต่ละข้ออยู่ระหว่าง 1–5 (1 = ไม่เห็นด้วยอย่างยิ่ง, 5 = เห็นด้วยอย่างยิ่ง)")

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🚀 เริ่มทำแบบประเมิน", type="primary"):
            st.session_state.step = "mbti"
            st.session_state.current_question = 0
            st.rerun()


def render_mbti():
    questions_data = load_questions()
    functions = questions_data["functions"]
    total_questions = sum(len(f["questions"]) for f in functions)

    answered = len(st.session_state.mbti_answers)
    progress = answered / total_questions if total_questions > 0 else 0

    st.progress(progress, text=f"Progress: {answered}/{total_questions} ข้อ")

    st.subheader("🧠 แบบสอบถาม Cognitive Functions (MBTI)")

    func_idx = 0
    q_global = 0
    for fi, func in enumerate(functions):
        for qi, q in enumerate(func["questions"]):
            if q_global == st.session_state.current_question:
                render_mbti_question(func, fi, qi, q, functions, total_questions)
                return
            q_global += 1

    st.session_state.step = "mbti_result"
    st.rerun()


def render_mbti_question(func, func_idx, q_idx, question, functions, total_questions):
    qid = question["id"]
    current_val = st.session_state.mbti_answers.get(qid, 3)

    st.markdown(f"**{func['code']} — {func['name_th']}**")
    st.markdown(f"### ข้อที่ {st.session_state.current_question + 1}/{total_questions}")
    st.markdown(f"#### {question['text']}")

    score = st.slider(
        "ระดับความเห็นด้วย",
        min_value=1,
        max_value=5,
        value=current_val,
        key=f"mbti_{qid}",
        format="%d",
        help="1 = ไม่เห็นด้วยอย่างยิ่ง, 5 = เห็นด้วยอย่างยิ่ง",
    )

    labels = {1: "❌ ไม่เห็นด้วยอย่างยิ่ง", 2: "😕 ไม่เห็นด้วย", 3: "😐 เฉยๆ", 4: "😊 เห็นด้วย", 5: "🤩 เห็นด้วยอย่างยิ่ง"}
    st.caption(labels.get(score, ""))

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.session_state.current_question > 0:
            if st.button("◀️ ก่อนหน้า"):
                st.session_state.mbti_answers[qid] = score
                st.session_state.current_question -= 1
                st.rerun()

    with col3:
        if st.button("ถัดไป ▶️"):
            st.session_state.mbti_answers[qid] = score
            if st.session_state.current_question < total_questions - 1:
                st.session_state.current_question += 1
            else:
                st.session_state.step = "mbti_result"
            st.rerun()

    st.session_state.mbti_answers[qid] = score


def render_mbti_result():
    st.subheader("📊 ผลลัพธ์ MBTI")
    engine = MBTIEngine()
    scores = engine.compute_function_scores(st.session_state.mbti_answers)
    mbti = engine.determine_mbti(scores)
    ranking = engine.get_function_ranking(scores)
    desc = engine.get_mbti_description(mbti)

    st.session_state.mbti_result = mbti
    st.session_state.function_scores = scores

    st.markdown(f"## 🎯 MBTI ของคุณ: **{mbti}**")
    st.markdown(f"**{desc['name']}** ({desc['name_th']})")
    st.markdown(f"_{desc['desc']}_")

    st.warning("⚠️ ผลลัพธ์เป็นการประเมินเพื่อการสำรวจตนเอง ไม่ใช่การวินิจฉัยทางจิตวิทยา")

    st.subheader("📈 Cognitive Functions Score")
    max_score = 50
    for func_code, score in ranking:
        bar_len = int((score / max_score) * 30)
        bar = "█" * bar_len + "░" * (30 - bar_len)
        func_name = next((f["name_th"] for f in load_questions()["functions"] if f["code"] == func_code), func_code)
        st.markdown(f"**{func_code}** ({func_name})")
        st.markdown(f"`{bar}` **{score}/{max_score}**")

    import pandas as pd
    chart_data = pd.DataFrame({
        "Function": [r[0] for r in ranking],
        "Score": [r[1] for r in ranking],
    })
    st.bar_chart(chart_data.set_index("Function"))

    col1, col2 = st.columns(2)
    with col2:
        if st.button("ถัดไป: แบบสำรวจความสนใจ →", type="primary"):
            st.session_state.step = "interest"
            st.session_state.current_question = 0
            st.rerun()


def render_interest():
    questions_data = load_interest_questions()
    categories = questions_data["categories"]
    total_questions = sum(len(c["questions"]) for c in categories)

    answered = len(st.session_state.interest_answers)
    progress = answered / total_questions if total_questions > 0 else 0

    st.progress(progress, text=f"Progress: {answered}/{total_questions} ข้อ")

    st.subheader("📚 แบบสำรวจความสนใจและความถนัด")

    q_global = 0
    for ci, cat in enumerate(categories):
        for qi, q in enumerate(cat["questions"]):
            if q_global == st.session_state.current_question:
                render_interest_question(cat, ci, qi, q, categories, total_questions)
                return
            q_global += 1

    st.session_state.step = "financial"
    st.rerun()


def render_interest_question(cat, cat_idx, q_idx, question, categories, total_questions):
    qid = question["id"]
    current_val = st.session_state.interest_answers.get(qid, 3)

    st.markdown(f"**{cat['code']} — {cat['name']}**")
    st.markdown(f"### ข้อที่ {st.session_state.current_question + 1}/{total_questions}")
    st.markdown(f"#### {question['text']}")

    score = st.slider(
        "ระดับความสนใจ",
        min_value=1,
        max_value=5,
        value=current_val,
        key=f"interest_{qid}",
        format="%d",
        help="1 = ไม่ใช่เลย, 5 = ใช่มากที่สุด",
    )

    labels = {1: "❌ ไม่ใช่เลย", 2: "😕 น้อยมาก", 3: "😐 ปานกลาง", 4: "😊 ค่อนข้างใช่", 5: "🤩 ใช่มากที่สุด"}
    st.caption(labels.get(score, ""))

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.session_state.current_question > 0:
            if st.button("◀️ ก่อนหน้า"):
                st.session_state.interest_answers[qid] = score
                st.session_state.current_question -= 1
                st.rerun()

    with col3:
        if st.button("ถัดไป ▶️"):
            st.session_state.interest_answers[qid] = score
            if st.session_state.current_question < total_questions - 1:
                st.session_state.current_question += 1
            else:
                st.session_state.step = "financial"
                st.session_state.current_question = 0
            st.rerun()

    st.session_state.interest_answers[qid] = score


def render_financial():
    st.subheader("💰 แบบสอบถามปัจจัยทางการเงิน")

    fin_data = load_financial_questions()
    factors = fin_data["factors"]

    for factor in factors:
        code = factor["code"]
        st.markdown(f"### {code}. {factor['name']}")

        options = {opt["label"]: opt["value"] for opt in factor["options"]}
        descriptions = {opt["label"]: opt["description"] for opt in factor["options"]}

        current = st.session_state.financial_answers.get(code, None)
        current_label = None
        if current:
            for label, val in options.items():
                if val == current:
                    current_label = label
                    break

        selected = st.radio(
            f"เลือก {code}",
            options.keys(),
            index=list(options.keys()).index(current_label) if current_label else 0,
            key=f"fin_{code}",
            label_visibility="collapsed",
        )

        if selected:
            st.session_state.financial_answers[code] = options[selected]

        st.caption(descriptions.get(selected, ""))
        st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("◀️ กลับ"):
            st.session_state.step = "interest"
            st.session_state.current_question = 0
            st.rerun()
    with col2:
        if st.button("✅ ดูผลลัพธ์", type="primary"):
            st.session_state.step = "result"
            st.rerun()


def render_final_result():
    st.subheader("🎉 ผลการประเมินของคุณ")

    mbti = st.session_state.get("mbti_result", "Unknown")
    func_scores = st.session_state.get("function_scores", {})
    interest_scores = ScoringEngine.compute_interest_scores(st.session_state.interest_answers)
    financial_profile = ScoringEngine.compute_financial_profile(st.session_state.financial_answers)

    engine = MBTIEngine()
    desc = engine.get_mbti_description(mbti)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("MBTI", mbti)
        st.caption(f"{desc['name']} ({desc['name_th']})")
    with col2:
        top_interest = ScoringEngine.get_top_interest(interest_scores)
        interest_names = {"M": "คณิตศาสตร์/คอมพิวเตอร์", "S": "วิทยาศาสตร์/เทคโนโลยี", "L": "ภาษา/วรรณกรรม", "H": "สังคมศึกษา/มนุษยศาสตร์", "A": "ศิลปะ/ดนตรี/การออกแบบ"}
        st.metric("ความสนใจสูงสุด", f"{top_interest} ({interest_names.get(top_interest, '')})")

    st.divider()

    st.subheader("📈 ผล_mbti")
    max_score = 50
    for func_code, score in sorted(func_scores.items(), key=lambda x: x[1], reverse=True):
        bar_len = int((score / max_score) * 30)
        bar = "█" * bar_len + "░" * (30 - bar_len)
        st.markdown(f"`{func_code:2s} {bar} {score}/{max_score}`")

    st.divider()
    st.subheader("📊 ผลความสนใจ")
    import pandas as pd
    chart_data = pd.DataFrame({
        "หมวด": list(interest_scores.keys()),
        "เปอร์เซ็นต์": [d["percentage"] for d in interest_scores.values()],
    })
    st.bar_chart(chart_data.set_index("หมวด"))

    col1, col2 = st.columns(2)
    with col1:
        for cat, data in interest_scores.items():
            st.markdown(f"**{cat}**: {data['percentage']:.1f}% ({data['raw']}/{data['max']})")

    st.divider()
    st.subheader("💰 ปัจจัยทางการเงิน")
    fin_names = {
        "F1": "งบประมาณค่าเทอม", "F2": "เป้าหมายหลังเรียนจบ",
        "F3": "ภาระทางการเงิน", "F4": "ทุนการศึกษา",
        "F5": "การเดินทาง", "F6": "ค่าใช้จ่ายแฝง"
    }
    col1, col2, col3 = st.columns(3)
    for i, (key, name) in enumerate(fin_names.items()):
        with [col1, col2, col3][i % 3]:
            val = financial_profile.get(key, "")
            st.metric(name, val)

    st.divider()
    st.subheader("🧠 Logical Thinking")
    has_project = st.checkbox("ฉันมีประสบการณ์ทำโครงงานคณิตศาสตร์เกี่ยวกับตรรกศาสตร์", value=True)
    st.session_state.logical_project = has_project

    st.divider()

    if st.button("🔍 ค้นหาคณะที่เหมาะสม", type="primary"):
        matcher = FacultyMatcher()
        results = matcher.match_all(
            mbti=mbti,
            interest_scores=interest_scores,
            financial_profile=financial_profile,
            has_logical_project=has_project,
        )

        top_5 = results[:5]
        st.session_state.faculty_results = results
        st.session_state.top_5 = top_5

        db = Database()
        assessment_id = f"AST-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        data = {
            "assessment_id": assessment_id,
            "created_at": datetime.now().isoformat(),
            "mbti": mbti,
            "ti_score": func_scores.get("Ti", 0),
            "te_score": func_scores.get("Te", 0),
            "fe_score": func_scores.get("Fe", 0),
            "fi_score": func_scores.get("Fi", 0),
            "se_score": func_scores.get("Se", 0),
            "si_score": func_scores.get("Si", 0),
            "ne_score": func_scores.get("Ne", 0),
            "ni_score": func_scores.get("Ni", 0),
            "m_score": interest_scores.get("M", {}).get("percentage", 0),
            "s_score": interest_scores.get("S", {}).get("percentage", 0),
            "l_score": interest_scores.get("L", {}).get("percentage", 0),
            "h_score": interest_scores.get("H", {}).get("percentage", 0),
            "a_score": interest_scores.get("A", {}).get("percentage", 0),
            "f1": financial_profile.get("F1", "medium"),
            "f2": financial_profile.get("F2", "stability"),
            "f3": financial_profile.get("F3", "low"),
            "f4": financial_profile.get("F4", "not_interested"),
            "f5": financial_profile.get("F5", "flexible"),
            "f6": financial_profile.get("F6", "medium"),
            "logical_project": has_project,
            "recommended_faculties": [r["faculty"] for r in top_5],
            "faculty_match_scores": {r["faculty"]: r["overall_match"] for r in results},
            "top_faculty": top_5[0]["faculty"] if top_5 else "",
            "top_match_pct": top_5[0]["overall_match"] if top_5 else 0,
        }
        db.save_assessment(data)
        st.session_state.assessment_id = assessment_id
        st.rerun()

    if "top_5" in st.session_state:
        render_top_faculties()


def render_top_faculties():
    top_5 = st.session_state.top_5
    st.divider()
    st.subheader("🏆 คณะที่แนะนำ")

    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    for i, fac in enumerate(top_5):
        medal = medals[i] if i < len(medals) else f"{i+1}."
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"### {medal} {fac['faculty']}")
                st.caption(f"กลุ่ม: {fac['group']}")
            with col2:
                st.metric("Overall Match", f"{fac['overall_match']}%")
            with col3:
                if st.button("ดูรายละเอียด", key=f"detail_{i}"):
                    st.session_state.selected_faculty = fac
                    st.session_state.show_faculty_detail = True
                    st.rerun()

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.caption(f"Academic: {fac['academic_match']}%")
            with col2:
                st.caption(f"MBTI: {fac['mbti_match']}%")
            with col3:
                st.caption(f"Financial: {fac['financial_match']}%")
            with col4:
                st.caption(f"Logical: {fac['logical_match']}%")
            st.divider()

    if "show_faculty_detail" in st.session_state and st.session_state.show_faculty_detail:
        render_faculty_detail()


def render_faculty_detail():
    fac = st.session_state.selected_faculty
    st.subheader(f"📋 {fac['faculty']}")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Overall Match", f"{fac['overall_match']}%")
    with col2:
        st.metric("กลุ่ม", fac["group"])

    st.divider()
    st.markdown("### 📊 คะแนนย่อย")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Academic Match", f"{fac['academic_match']}%")
    with col2:
        st.metric("MBTI Match", f"{fac['mbti_match']}%")
    with col3:
        st.metric("Financial Match", f"{fac['financial_match']}%")
    with col4:
        st.metric("Logical Match", f"{fac['logical_match']}%")

    st.divider()
    st.markdown("### 🔍 เงื่อนไข")
    for detail in fac.get("condition_details", []):
        st.markdown(f"{detail['icon']} **{detail['section']}**: {detail['description']} — {detail['reason']}")

    if st.button("ปิด"):
        st.session_state.show_faculty_detail = False
        st.rerun()
        st.rerun()
