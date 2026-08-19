# ระบบแนะนำคณะ/สาขามหาวิทยาลัย

> Web Application สำหรับแนะแนวการเลือกคณะ/สาขามหาวิทยาลัย ด้วยหลักการตรรกศาสตร์

## คุณสมบัติ

- **แบบสอบถาม MBTI (Cognitive Functions)** — 80 ข้อ, 8 ฟังก์ชัน
- **แบบสำรวจความสนใจและความถนัด** — 100 ข้อ, 5 หมวด
- **แบบสอบถามปัจจัยทางการเงิน** — 6 ปัจจัย (F1-F6)
- **Logic Engine** — ใช้ AND/OR/NOT ในการคัดกรองคณะ
- **50+ คณะ** จาก 6 กลุ่มวิชาการ
- **Match %** — คำนวณความเข้ากันได้แบบถ่วงน้ำหนัก
- **Dashboard** — สถิติและการวิเคราะห์ข้อมูล
- **Export** — ดาวน์โหลดผลลัพธ์เป็น CSV

## วิธีติดตั้ง

### Clone Repository

```bash
git clone https://github.com/your-username/logic-faculty-recommender.git
cd logic-faculty-recommender
```

### ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

### รันแอปพลิเคชัน

```bash
streamlit run app.py
```

## Deploy บน Streamlit Community Cloud

1. Push โค้ดไป GitHub Repository
2. เข้า https://share.streamlit.io
3. เชื่อมต่อ GitHub Repository
4. เลือก Branch (main/master)
5. ตั้ง Main file path: `app.py`
6. กด Deploy

## โครงสร้างโปรเจกต์

```
project/
├── app.py                    # Main Streamlit App
├── requirements.txt          # Dependencies
├── README.md                 # เอกสารประกอบ
├── .gitignore                # Git ignore rules
│
├── data/
│   ├── .gitkeep              # สำหรับ Git
│   ├── app.db                # SQLite Database (ไม่ commit)
│   ├── faculties.json        # ข้อมูลคณะและเงื่อนไข
│   ├── questions.json        # แบบสอบถาม MBTI 80 ข้อ
│   └── financial_questions.json  # แบบสอบถามการเงิน
│
├── logic/
│   ├── __init__.py
│   ├── mbti_engine.py        # MBTI Cognitive Functions Engine
│   ├── scoring.py            # Scoring Engine (Interest/Financial)
│   ├── logic_engine.py       # Logic Engine (AND/OR/NOT)
│   ├── faculty_matcher.py    # Faculty Matching Engine
│   └── database.py           # SQLite Database Layer
│
├── pages/
│   ├── assessment.py         # แบบประเมิน (MBTI + Interest + Financial)
│   ├── result.py             # ผลการประเมิน
│   ├── dashboard.py          # Dashboard สถิติ
│   ├── history.py            # ประวัติการประเมิน
│   └── logic_explanation.py  # อธิบายหลักการตรรกศาสตร์
│
└── tests/
    ├── test_mbti.py          # ทดสอบ MBTI Engine
    ├── test_logic.py         # ทดสอบ Logic Engine
    ├── test_scoring.py       # ทดสอบ Scoring Engine
    └── test_database.py      # ทดสอบ Database
```

## หลักการตรรกศาสตร์

ระบบใช้ตรรกศาสตร์จริงในการคัดกรองคณะ:

```
(MBTI₁ ∨ MBTI₂ ∨ ...) ∧ (หมวดวิชา₁ > เกณฑ์%) [∧ (หมวดวิชา₂ > เกณฑ์%)]
```

**ตัวอย่าง:**
```python
P = M >= 60      # คะแนน M มากกว่า 60%
R = MBTI in ["INTJ", "INTP", "ISTP", "ENTP", "ISTJ"]
Faculty_OK = P and R
```

## Match % Calculation

```
Overall = Academic × 0.35 + MBTI × 0.25 + Financial × 0.25 + Logical × 0.15
```

## หมายเหตุ

⚠️ ผลลัพธ์เป็นการประเมินเพื่อการสำรวจตนเอง ไม่ใช่การวินิจฉัยทางจิตวิทยา

## License

MIT License
