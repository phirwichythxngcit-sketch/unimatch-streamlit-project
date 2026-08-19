"""Database Layer — SQLite สำหรับเก็บผลการประเมิน"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DB_DIR = ROOT_DIR / "data"
DB_PATH = DB_DIR / "app.db"


class Database:
    """จัดการฐานข้อมูล SQLite"""

    def __init__(self, db_path: str = DB_PATH):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        conn = self._get_conn()
        try:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS assessments (
                    assessment_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    mbti TEXT,
                    ti_score INTEGER DEFAULT 0,
                    te_score INTEGER DEFAULT 0,
                    fe_score INTEGER DEFAULT 0,
                    fi_score INTEGER DEFAULT 0,
                    se_score INTEGER DEFAULT 0,
                    si_score INTEGER DEFAULT 0,
                    ne_score INTEGER DEFAULT 0,
                    ni_score INTEGER DEFAULT 0,
                    m_score REAL DEFAULT 0,
                    s_score REAL DEFAULT 0,
                    l_score REAL DEFAULT 0,
                    h_score REAL DEFAULT 0,
                    a_score REAL DEFAULT 0,
                    f1 TEXT DEFAULT 'medium',
                    f2 TEXT DEFAULT 'stability',
                    f3 TEXT DEFAULT 'low',
                    f4 TEXT DEFAULT 'not_interested',
                    f5 TEXT DEFAULT 'flexible',
                    f6 TEXT DEFAULT 'medium',
                    logical_project INTEGER DEFAULT 1,
                    recommended_faculties TEXT DEFAULT '[]',
                    faculty_match_scores TEXT DEFAULT '{}',
                    top_faculty TEXT DEFAULT '',
                    top_match_pct REAL DEFAULT 0
                );
            """)
            conn.commit()
        finally:
            conn.close()

    def save_assessment(self, data: dict) -> str:
        """บันทึกผลการประเมิน คืน assessment_id"""
        assessment_id = data.get("assessment_id", "")
        if not assessment_id:
            assessment_id = f"AST-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        conn = self._get_conn()
        try:
            conn.execute(
                """INSERT OR REPLACE INTO assessments
                (assessment_id, created_at, mbti,
                 ti_score, te_score, fe_score, fi_score, se_score, si_score, ne_score, ni_score,
                 m_score, s_score, l_score, h_score, a_score,
                 f1, f2, f3, f4, f5, f6,
                 logical_project,
                 recommended_faculties, faculty_match_scores, top_faculty, top_match_pct)
                VALUES (?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?,
                        ?,
                        ?, ?, ?, ?)""",
                (
                    assessment_id,
                    data.get("created_at", datetime.now().isoformat()),
                    data.get("mbti", ""),
                    data.get("ti_score", 0),
                    data.get("te_score", 0),
                    data.get("fe_score", 0),
                    data.get("fi_score", 0),
                    data.get("se_score", 0),
                    data.get("si_score", 0),
                    data.get("ne_score", 0),
                    data.get("ni_score", 0),
                    data.get("m_score", 0),
                    data.get("s_score", 0),
                    data.get("l_score", 0),
                    data.get("h_score", 0),
                    data.get("a_score", 0),
                    data.get("f1", "medium"),
                    data.get("f2", "stability"),
                    data.get("f3", "low"),
                    data.get("f4", "not_interested"),
                    data.get("f5", "flexible"),
                    data.get("f6", "medium"),
                    1 if data.get("logical_project", True) else 0,
                    json.dumps(data.get("recommended_faculties", []), ensure_ascii=False),
                    json.dumps(data.get("faculty_match_scores", {}), ensure_ascii=False),
                    data.get("top_faculty", ""),
                    data.get("top_match_pct", 0),
                ),
            )
            conn.commit()
            return assessment_id
        finally:
            conn.close()

    def get_assessment(self, assessment_id: str) -> dict | None:
        """ดึงผลการประเมิน"""
        conn = self._get_conn()
        try:
            row = conn.execute(
                "SELECT * FROM assessments WHERE assessment_id = ?", (assessment_id,)
            ).fetchone()
            if row is None:
                return None
            return dict(row)
        finally:
            conn.close()

    def get_all_assessments(self) -> list[dict]:
        """ดึงผลการประเมินทั้งหมด"""
        conn = self._get_conn()
        try:
            rows = conn.execute(
                "SELECT * FROM assessments ORDER BY created_at DESC"
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def get_count(self) -> int:
        """นับจำนวนการประเมิน"""
        conn = self._get_conn()
        try:
            row = conn.execute("SELECT COUNT(*) as cnt FROM assessments").fetchone()
            return row["cnt"] if row else 0
        finally:
            conn.close()

    def get_mbti_distribution(self) -> dict[str, int]:
        """นับสัดส่วน MBTI ที่พบ"""
        conn = self._get_conn()
        try:
            rows = conn.execute(
                "SELECT mbti, COUNT(*) as cnt FROM assessments GROUP BY mbti"
            ).fetchall()
            return {r["mbti"]: r["cnt"] for r in rows if r["mbti"]}
        finally:
            conn.close()

    def get_top_interest_distribution(self) -> dict[str, int]:
        """นับสัดส่วนหมวดความสนใจที่มีคะแนนสูงสุด"""
        conn = self._get_conn()
        try:
            all_rows = conn.execute("SELECT m_score, s_score, l_score, h_score, a_score FROM assessments").fetchall()
            dist = {"M": 0, "S": 0, "L": 0, "H": 0, "A": 0}
            for row in all_rows:
                scores = {"M": row["m_score"], "S": row["s_score"], "L": row["l_score"],
                          "H": row["h_score"], "A": row["a_score"]}
                top = max(scores, key=scores.get)
                dist[top] += 1
            return dist
        finally:
            conn.close()

    def get_faculty_distribution(self) -> dict[str, int]:
        """นับสัดส่วนคณะที่ถูกแนะนำ"""
        conn = self._get_conn()
        try:
            rows = conn.execute(
                "SELECT top_faculty FROM assessments WHERE top_faculty != ''"
            ).fetchall()
            dist = {}
            for r in rows:
                fac = r["top_faculty"]
                dist[fac] = dist.get(fac, 0) + 1
            return dist
        finally:
            conn.close()

    def get_average_match(self) -> float:
        """คำนวณค่าเฉลี่ย Match %"""
        conn = self._get_conn()
        try:
            row = conn.execute(
                "SELECT AVG(top_match_pct) as avg_match FROM assessments WHERE top_match_pct > 0"
            ).fetchone()
            return round(row["avg_match"], 1) if row and row["avg_match"] else 0
        finally:
            conn.close()
