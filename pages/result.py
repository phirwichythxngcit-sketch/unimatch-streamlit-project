"""Result Page — แสดงผลการประเมิน"""

import streamlit as st
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
from logic.mbti_engine import MBTIEngine
from logic.database import Database

DATA_DIR = ROOT_DIR / "data"


def run():
    st.header("📊 ผลการประเมิน")

    if "assessment_id" not in st.session_state:
        st.info("ยังไม่มีผลการประเมิน กรุณาทำแบบประเมินก่อน")
        return

    db = Database()
    data = db.get_assessment(st.session_state.assessment_id)
    if data is None:
        st.error("ไม่พบผลการประเมิน")
        return

    mbti = data["mbti"]
    desc = MBTIEngine.get_mbti_description(mbti)

    st.markdown(f"## 🎯 MBTI: **{mbti}**")
    st.markdown(f"**{desc['name']}** ({desc['name_th']})")
    st.markdown(f"_{desc['desc']}_")

    st.warning("⚠️ ผลลัพธ์เป็นการประเมินเพื่อการสำรวจตนเอง ไม่ใช่การวินิจฉัยทางจิตวิทยา")

    st.divider()
    st.subheader("📈 Cognitive Functions")
    func_scores = {
        "Ti": data["ti_score"], "Te": data["te_score"],
        "Fe": data["fe_score"], "Fi": data["fi_score"],
        "Se": data["se_score"], "Si": data["si_score"],
        "Ne": data["ne_score"], "Ni": data["ni_score"],
    }
    max_score = 50
    for func_code, score in sorted(func_scores.items(), key=lambda x: x[1], reverse=True):
        bar_len = int((score / max_score) * 30)
        bar = "█" * bar_len + "░" * (30 - bar_len)
        st.markdown(f"`{func_code:2s} {bar} {score}/{max_score}`")

    st.divider()
    st.subheader("📊 ความสนใจ")
    interest_data = {
        "M": data["m_score"], "S": data["s_score"],
        "L": data["l_score"], "H": data["h_score"],
        "A": data["a_score"],
    }
    import pandas as pd
    chart_df = pd.DataFrame({
        "หมวด": list(interest_data.keys()),
        "เปอร์เซ็นต์": list(interest_data.values()),
    })
    st.bar_chart(chart_df.set_index("หมวด"))

    for cat, pct in sorted(interest_data.items(), key=lambda x: x[1], reverse=True):
        bar_len = int(pct / 100 * 30)
        bar = "█" * bar_len + "░" * (30 - bar_len)
        st.markdown(f"`{cat} {bar} {pct:.1f}%`")

    st.divider()
    st.subheader("💰 ปัจจัยทางการเงิน")
    fin_map = {"F1": data["f1"], "F2": data["f2"], "F3": data["f3"],
               "F4": data["f4"], "F5": data["f5"], "F6": data["f6"]}
    fin_names = {
        "F1": "งบประมาณค่าเทอม", "F2": "เป้าหมายหลังเรียนจบ",
        "F3": "ภาระทางการเงิน", "F4": "ทุนการศึกษา",
        "F5": "การเดินทาง", "F6": "ค่าใช้จ่ายแฝง"
    }
    col1, col2, col3 = st.columns(3)
    for i, (key, name) in enumerate(fin_names.items()):
        with [col1, col2, col3][i % 3]:
            st.metric(name, fin_map[key])

    st.divider()
    st.subheader("🏆 คณะที่แนะนำ")
    try:
        recommended = json.loads(data["recommended_faculties"]) if isinstance(data["recommended_faculties"], str) else data["recommended_faculties"]
        match_scores = json.loads(data["faculty_match_scores"]) if isinstance(data["faculty_match_scores"], str) else data["faculty_match_scores"]
    except (json.JSONDecodeError, TypeError):
        recommended = []
        match_scores = {}

    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    for i, fac_name in enumerate(recommended[:5]):
        medal = medals[i] if i < len(medals) else f"{i+1}."
        pct = match_scores.get(fac_name, 0)
        st.markdown(f"{medal} **{fac_name}** — Match {pct}%")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        csv_data = generate_csv(data)
        st.download_button(
            label="📥 ดาวน์โหลด CSV",
            data=csv_data,
            file_name=f"assessment_{data['assessment_id']}.csv",
            mime="text/csv",
        )
    with col2:
        if st.button("🔄 เริ่มทำแบบประเมินใหม่"):
            for key in ["step", "mbti_answers", "interest_answers", "financial_answers",
                         "current_question", "mbti_result", "function_scores",
                         "assessment_id", "faculty_results", "top_5"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()


def generate_csv(data: dict) -> str:
    lines = [
        "Field,Value",
        f"assessment_id,{data['assessment_id']}",
        f"created_at,{data['created_at']}",
        f"mbti,{data['mbti']}",
        f"ti_score,{data['ti_score']}",
        f"te_score,{data['te_score']}",
        f"fe_score,{data['fe_score']}",
        f"fi_score,{data['fi_score']}",
        f"se_score,{data['se_score']}",
        f"si_score,{data['si_score']}",
        f"ne_score,{data['ne_score']}",
        f"ni_score,{data['ni_score']}",
        f"m_score,{data['m_score']}",
        f"s_score,{data['s_score']}",
        f"l_score,{data['l_score']}",
        f"h_score,{data['h_score']}",
        f"a_score,{data['a_score']}",
        f"f1,{data['f1']}",
        f"f2,{data['f2']}",
        f"f3,{data['f3']}",
        f"f4,{data['f4']}",
        f"f5,{data['f5']}",
        f"f6,{data['f6']}",
        f"top_faculty,{data['top_faculty']}",
        f"top_match_pct,{data['top_match_pct']}",
    ]
    return "\n".join(lines)
