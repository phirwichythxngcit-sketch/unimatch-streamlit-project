"""Dashboard Page — สถิติและการวิเคราะห์ข้อมูล"""

import streamlit as st
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from logic.database import Database


def run():
    st.header("📊 Dashboard")

    db = Database()
    count = db.get_count()

    if count == 0:
        st.info("📊 ยังมีข้อมูลไม่เพียงพอสำหรับสรุปสถิติ กรุณาทำแบบประเมินก่อน")
        return

    st.subheader("📈 สถิติภาพรวม")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("จำนวนผู้ทำแบบประเมิน", count)
    with col2:
        avg_match = db.get_average_match()
        st.metric("ค่าเฉลี่ย Match %", f"{avg_match}%")
    with col3:
        mbti_dist = db.get_mbti_distribution()
        most_common_mbti = max(mbti_dist, key=mbti_dist.get) if mbti_dist else "N/A"
        st.metric("MBTI ที่พบมาก", most_common_mbti)
    with col4:
        interest_dist = db.get_top_interest_distribution()
        most_common_interest = max(interest_dist, key=interest_dist.get) if interest_dist else "N/A"
        st.metric("หมวดความสนใจสูงสุด", most_common_interest)

    st.divider()

    st.subheader("🥧 สัดส่วน MBTI")
    if mbti_dist:
        chart_data = pd.DataFrame({
            "MBTI": list(mbti_dist.keys()),
            "จำนวน": list(mbti_dist.values()),
        })
        st.bar_chart(chart_data.set_index("MBTI"))
    else:
        st.info("ยังไม่มีข้อมูล MBTI")

    st.divider()

    st.subheader("🥧 สัดส่วนความสนใจ")
    if interest_dist and any(v > 0 for v in interest_dist.values()):
        filtered = {k: v for k, v in interest_dist.items() if v > 0}
        if filtered:
            chart_data = pd.DataFrame({
                "หมวด": list(filtered.keys()),
                "จำนวน": list(filtered.values()),
            })
            st.bar_chart(chart_data.set_index("หมวด"))
    else:
        st.info("ยังไม่มีข้อมูลความสนใจ")

    st.divider()

    st.subheader("🏛️ คณะที่ถูกแนะนำบ่อย")
    fac_dist = db.get_faculty_distribution()
    if fac_dist:
        sorted_fac = sorted(fac_dist.items(), key=lambda x: x[1], reverse=True)[:10]
        chart_data = pd.DataFrame({
            "คณะ": [f[0] for f in sorted_fac],
            "จำนวน": [f[1] for f in sorted_fac],
        })
        st.bar_chart(chart_data.set_index("คณะ"))

        for fac, cnt in sorted_fac:
            st.markdown(f"- **{fac}**: {cnt} ครั้ง")
    else:
        st.info("ยังไม่มีข้อมูลคณะที่แนะนำ")

    st.divider()

    st.subheader("📋 รายชื่อผู้ทำแบบประเมินล่าสุด")
    all_assessments = db.get_all_assessments()
    if all_assessments:
        df_data = []
        for a in all_assessments[:20]:
            df_data.append({
                "ID": a["assessment_id"],
                "วันที่": a["created_at"][:10],
                "MBTI": a["mbti"],
                "คณะอันดับ 1": a["top_faculty"],
                "Match %": a["top_match_pct"],
            })
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)
