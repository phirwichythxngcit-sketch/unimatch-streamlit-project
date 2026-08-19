"""Tests for Database"""

import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from logic.database import Database


def test_save_and_get_assessment():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        db = Database(db_path)

        data = {
            "assessment_id": "TEST-001",
            "created_at": "2026-01-01T00:00:00",
            "mbti": "INTP",
            "ti_score": 50, "te_score": 30,
            "fe_score": 20, "fi_score": 40,
            "se_score": 10, "si_score": 30,
            "ne_score": 40, "ni_score": 20,
            "m_score": 80.0, "s_score": 60.0,
            "l_score": 40.0, "h_score": 50.0,
            "a_score": 30.0,
            "f1": "medium", "f2": "stability",
            "f3": "low", "f4": "not_interested",
            "f5": "flexible", "f6": "medium",
            "logical_project": True,
            "recommended_faculties": ["Computer Science", "Mathematics"],
            "faculty_match_scores": {"Computer Science": 92, "Mathematics": 88},
            "top_faculty": "Computer Science",
            "top_match_pct": 92,
        }

        aid = db.save_assessment(data)
        assert aid == "TEST-001"

        result = db.get_assessment("TEST-001")
        assert result is not None
        assert result["mbti"] == "INTP"
        assert result["top_match_pct"] == 92
        print("PASS: test_save_and_get_assessment")


def test_get_all_assessments():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        db = Database(db_path)

        for i in range(3):
            db.save_assessment({
                "assessment_id": f"TEST-{i:03d}",
                "created_at": f"2026-01-0{i+1}T00:00:00",
                "mbti": "INTP",
            })

        all_assessments = db.get_all_assessments()
        assert len(all_assessments) == 3
        print("PASS: test_get_all_assessments")


def test_get_count():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        db = Database(db_path)

        assert db.get_count() == 0

        db.save_assessment({"assessment_id": "TEST-001", "mbti": "INTP"})
        assert db.get_count() == 1
        print("PASS: test_get_count")


def test_get_mbti_distribution():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        db = Database(db_path)

        db.save_assessment({"assessment_id": "T1", "mbti": "INTP"})
        db.save_assessment({"assessment_id": "T2", "mbti": "INTP"})
        db.save_assessment({"assessment_id": "T3", "mbti": "INTJ"})

        dist = db.get_mbti_distribution()
        assert dist["INTP"] == 2
        assert dist["INTJ"] == 1
        print("PASS: test_get_mbti_distribution")


def test_get_top_interest_distribution():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        db = Database(db_path)

        db.save_assessment({"assessment_id": "T1", "m_score": 80, "s_score": 60, "l_score": 40, "h_score": 50, "a_score": 30})
        db.save_assessment({"assessment_id": "T2", "m_score": 30, "s_score": 90, "l_score": 40, "h_score": 50, "a_score": 30})

        dist = db.get_top_interest_distribution()
        assert dist["M"] == 1
        assert dist["S"] == 1
        print("PASS: test_get_top_interest_distribution")


def test_get_faculty_distribution():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        db = Database(db_path)

        db.save_assessment({"assessment_id": "T1", "top_faculty": "Computer Science"})
        db.save_assessment({"assessment_id": "T2", "top_faculty": "Computer Science"})
        db.save_assessment({"assessment_id": "T3", "top_faculty": "Mathematics"})

        dist = db.get_faculty_distribution()
        assert dist["Computer Science"] == 2
        assert dist["Mathematics"] == 1
        print("PASS: test_get_faculty_distribution")


def test_get_average_match():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        db = Database(db_path)

        db.save_assessment({"assessment_id": "T1", "top_match_pct": 80})
        db.save_assessment({"assessment_id": "T2", "top_match_pct": 90})

        avg = db.get_average_match()
        assert avg == 85.0
        print("PASS: test_get_average_match")


if __name__ == "__main__":
    test_save_and_get_assessment()
    test_get_all_assessments()
    test_get_count()
    test_get_mbti_distribution()
    test_get_top_interest_distribution()
    test_get_faculty_distribution()
    test_get_average_match()
    print("\nAll Database tests passed!")
