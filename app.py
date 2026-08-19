"""ระบบแนะนำคณะ/สาขามหาวิทยาลัยจากความถนัด บุคลิกภาพ และปัจจัยทางการเงิน"""

import streamlit as st
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(
    page_title="ระบบแนะนำคณะมหาวิทยาลัย",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("🎓 ระบบแนะนำคณะ")
st.sidebar.caption("แนะแนวการศึกษาด้วยตรรกศาสตร์")

st.sidebar.divider()

page = st.sidebar.radio(
    "เลือกหน้า",
    ["🏠 หน้าแรก", "📋 แบบประเมิน", "📊 ผลการประเมิน", "📈 Dashboard", "📜 ประวัติ", "🧠 หลักการตรรกศาสตร์"],
    index=0,
)

st.sidebar.divider()
st.sidebar.markdown("---")
st.sidebar.caption("⚠️ ผลลัพธ์เป็นการประเมินเพื่อการสำรวจตนเอง")
st.sidebar.caption("ไม่ใช่การวินิจฉัยทางจิตวิทยา")

if page == "🏠 หน้าแรก":
    st.header("🎓 ระบบแนะนำคณะ/สาขามหาวิทยาลัย")
    st.subheader("จากความถนัด บุคลิกภาพ และปัจจัยทางการเงิน")

    st.divider()

    st.markdown("""
    ### เกี่ยวกับระบบ

    ระบบแนะนำคณะ/สาขามหาวิทยาลัยนี้พัฒนาขึ้นโดยใช้หลักการ **ตรรกศาสตร์ (Logic)** ในการคัดกรอง
    โดยพิจารณาจาก 4 ปัจจัยหลัก:

    1. **🧠 บุคลิกภาพ MBTI** — จากแบบสอบถาม Cognitive Functions 80 ข้อ
    2. **📚 ความสนใจและความถนัด** — จากแบบสำรวจ 5 หมวด 100 ข้อ
    3. **💰 ปัจจัยทางการเงิน** — งบประมาณ เป้าหมาย ภาระทางการเงิน
    4. **🧩 ประสบการณ์ตรรกศาสตร์** — โครงงานคณิตศาสตร์เกี่ยวกับตรรกศาสตร์
    """)

    col1, col2 = st.columns(2)
    with col1:
        st.info("📊 **50+ คณะ** จาก 6 กลุ่มวิชาการ")
    with col2:
        st.info("🧠 **ตรรกศาสตร์จริง** ใช้ AND/OR/NOT ในการคัดกรอง")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("จำนวนข้อ MBTI", "80 ข้อ")
    with col2:
        st.metric("จำนวนข้อความสนใจ", "100 ข้อ")
    with col3:
        st.metric("ปัจจัยการเงิน", "6 ปัจจัย")

    st.divider()

    st.markdown("""
    ### วิธีใช้งาน

    1. กดปุ่ม **"📋 แบบประเมิน"** ทางด้านซ้าย
    2. ทำแบบสอบถาม MBTI (80 ข้อ)
    3. ทำแบบสำรวจความสนใจ (100 ข้อ)
    4. ตอบแบบสอบถามการเงิน (6 ปัจจัย)
    5. ดูผลลัพธ์และคณะที่แนะนำ
    6. ดูรายละเอียดแต่ละคณะ
    """)

    st.warning("⚠️ ผลลัพธ์เป็นการประเมินเพื่อการสำรวจตนเอง ไม่ใช่การวินิจฉัยทางจิตวิทยา")

    st.divider()
    st.caption("โครงงานคณิตศาสตร์เรื่อง ตรรกศาสตร์")

elif page == "📋 แบบประเมิน":
    from pages.assessment import run
    run()

elif page == "📊 ผลการประเมิน":
    from pages.result import run
    run()

elif page == "📈 Dashboard":
    from pages.dashboard import run
    run()

elif page == "📜 ประวัติ":
    from pages.history import run
    run()

elif page == "🧠 หลักการตรรกศาสตร์":
    from pages.logic_explanation import run
    run()
