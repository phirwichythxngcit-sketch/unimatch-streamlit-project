"""History Page — ประวัติการประเมิน"""

import streamlit as st
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
from logic.database import Database
from logic.mbti_engine import MBTIEngine


def run():
    st.header("📜 ประวัติการประเมิน")

    db = Database()
    all_assessments = db.get_all_assessments()

    if not all_assessments:
        st.info("ยังไม่มีประวัติการประเมิน กรุณาทำแบบประเมินก่อน")
        return

    st.caption(f"ทั้งหมด {len(all_assessments)} รายการ")

    for assessment in all_assessments:
        with st.expander(f"📋 {assessment['assessment_id']} — {assessment['created_at'][:10]} — {assessment['mbti']}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("MBTI", assessment["mbti"])
            with col2:
                st.metric("คณะอันดับ 1", assessment["top_faculty"] or "N/A")
            with col3:
                st.metric("Match %", f"{assessment['top_match_pct']}%")

            st.caption(f"ความสนใจสูงสุด: M={assessment['m_score']:.1f}% S={assessment['s_score']:.1f}% L={assessment['l_score']:.1f}% H={assessment['h_score']:.1f}% A={assessment['a_score']:.1f}%")

            try:
                recommended = json.loads(assessment["recommended_faculties"]) if isinstance(assessment["recommended_faculties"], str) else assessment["recommended_faculties"]
                match_scores = json.loads(assessment["faculty_match_scores"]) if isinstance(assessment["faculty_match_scores"], str) else assessment["faculty_match_scores"]
            except (json.JSONDecodeError, TypeError):
                recommended = []
                match_scores = {}

            if recommended:
                st.markdown("**คณะที่แนะนำ:**")
                medals = ["🥇", "🥈", "🥉"]
                for i, fac in enumerate(recommended[:5]):
                    medal = medals[i] if i < len(medals) else f"{i+1}."
                    pct = match_scores.get(fac, 0)
                    st.markdown(f"  {medal} {fac} — {pct}%")
