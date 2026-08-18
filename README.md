# UniMatch — แบบทดสอบเลือกคณะเรียนต่อ

เว็บแอป Streamlit ภาษาไทยที่ผสาน Cognitive Functions 80 ข้อ, แบบประเมินความสนใจและความถนัด 30 ข้อ, และระดับงบประมาณ เพื่อเสนอคณะ/สาขาที่ผ่านกฎตรรกศาสตร์เริ่มต้น

## ความสามารถ

- ให้คะแนน Cognitive Functions 8 ฟังก์ชัน (`Ne`, `Ni`, `Se`, `Si`, `Te`, `Ti`, `Fe`, `Fi`) ฟังก์ชันละ 10 ข้อ
- หาลำดับ Dominant → Auxiliary → Tertiary → Inferior และสรุป MBTI ทั้ง 16 ประเภท
- อธิบายหลักตรรกะและแสดงผลคะแนนอย่างโปร่งใส รวมถึงกรณีคะแนนเสมอ
- รวมคะแนนความถนัด 5 หมวด (`M`, `S`, `L`, `H`, `A`) เป็นคะแนนเต็ม 30 และเปอร์เซ็นต์
- ใช้เงือนไข `(MBTI₁ ∨ …) ∧ (หมวด > เกณฑ์%)` คัดเลือกคณะ/สาขา
- กรองตัวอย่างเส้นทางมหาวิทยาลัยตามงบ: น้อย / ปานกลาง / มาก
- ดาวน์โหลดรายงานผลเป็น JSON

## รันบนเครื่อง

ต้องมี Python 3.10 ขึ้นไป

```bash
git clone <YOUR-REPOSITORY-URL>
cd <YOUR-REPOSITORY>
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## ทดสอบตรรกะ

```bash
pip install -r requirements-dev.txt
pytest -q
```

## นำขึ้น GitHub และ Streamlit Community Cloud

1. สร้าง repository ใหม่บน GitHub แล้ว push ไฟล์ทั้งหมดในโฟลเดอร์นี้ขึ้นไป
2. เข้า [Streamlit Community Cloud](https://share.streamlit.io/) แล้วเลือก **Create app**
3. เลือก repository, branch และตั้ง Main file path เป็น `app.py`
4. กด Deploy

## ข้อจำกัดสำคัญ

MBTI และกฎจับคู่คณะในแอปเป็นเครื่องมือแนะแนว/heuristic ไม่ใช่การวินิจฉัยทางจิตวิทยาหรือเกณฑ์คัดเลือกของมหาวิทยาลัย ผลลัพธ์ไม่ควรใช้แทนการตรวจคุณสมบัติ TCAS, แผนการเรียน, ค่าใช้จ่ายจริง, ทุนการศึกษา และข้อมูลรับสมัครจากเว็บไซต์ทางการ

ค่าเทอมและตัวอย่างมหาวิทยาลัยใน `data.py` เป็นค่าโดยประมาณจากชุดข้อมูลตั้งต้นของโปรเจกต์ จึงต้องตรวจสอบหลักสูตรที่เปิดสอนและอัตราค่าธรรมเนียมล่าสุดกับมหาวิทยาลัยโดยตรงก่อนสมัคร
