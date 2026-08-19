"""Tests for MBTI Engine"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from logic.mbti_engine import MBTIEngine


def test_compute_function_scores():
    answers = {}
    for i in range(1, 11):
        answers[f"Ti_{i}"] = 5
        answers[f"Te_{i}"] = 3
        answers[f"Fe_{i}"] = 2
        answers[f"Fi_{i}"] = 4
        answers[f"Se_{i}"] = 1
        answers[f"Si_{i}"] = 3
        answers[f"Ne_{i}"] = 4
        answers[f"Ni_{i}"] = 2

    scores = MBTIEngine.compute_function_scores(answers)
    assert scores["Ti"] == 50
    assert scores["Te"] == 30
    assert scores["Fe"] == 20
    assert scores["Fi"] == 40
    assert scores["Se"] == 10
    assert scores["Si"] == 30
    assert scores["Ne"] == 40
    assert scores["Ni"] == 20
    print("PASS: test_compute_function_scores")


def test_determine_mbti_intj():
    answers = {}
    for i in range(1, 11):
        answers[f"Ni_{i}"] = 5
        answers[f"Te_{i}"] = 5
        answers[f"Fi_{i}"] = 4
        answers[f"Se_{i}"] = 2
        answers[f"Ti_{i}"] = 3
        answers[f"Fe_{i}"] = 2
        answers[f"Si_{i}"] = 3
        answers[f"Ne_{i}"] = 3

    scores = MBTIEngine.compute_function_scores(answers)
    mbti = MBTIEngine.determine_mbti(scores)
    assert mbti == "INTJ", f"Expected INTJ, got {mbti}"
    print("PASS: test_determine_mbti_intj")


def test_determine_mbti_intp():
    answers = {}
    for i in range(1, 11):
        answers[f"Ti_{i}"] = 5
        answers[f"Ne_{i}"] = 5
        answers[f"Si_{i}"] = 4
        answers[f"Fe_{i}"] = 2
        answers[f"Te_{i}"] = 3
        answers[f"Fi_{i}"] = 3
        answers[f"Se_{i}"] = 2
        answers[f"Ni_{i}"] = 3

    scores = MBTIEngine.compute_function_scores(answers)
    mbti = MBTIEngine.determine_mbti(scores)
    assert mbti == "INTP", f"Expected INTP, got {mbti}"
    print("PASS: test_determine_mbti_intp")


def test_function_ranking():
    answers = {}
    for i in range(1, 11):
        answers[f"Ti_{i}"] = 5
        answers[f"Te_{i}"] = 1
        answers[f"Fe_{i}"] = 3
        answers[f"Fi_{i}"] = 2
        answers[f"Se_{i}"] = 4
        answers[f"Si_{i}"] = 3
        answers[f"Ne_{i}"] = 4
        answers[f"Ni_{i}"] = 2

    scores = MBTIEngine.compute_function_scores(answers)
    ranking = MBTIEngine.get_function_ranking(scores)
    assert ranking[0][0] == "Ti"
    assert ranking[-1][0] == "Te"
    print("PASS: test_function_ranking")


def test_empty_answers():
    scores = MBTIEngine.compute_function_scores({})
    mbti = MBTIEngine.determine_mbti(scores)
    assert mbti == "Unknown"
    print("PASS: test_empty_answers")


def test_mbti_description():
    desc = MBTIEngine.get_mbti_description("INTJ")
    assert desc["name"] == "The Architect"
    assert desc["name_th"] == "นักออกแบบ"

    desc2 = MBTIEngine.get_mbti_description("INVALID")
    assert desc2["name"] == "Unknown"
    print("PASS: test_mbti_description")


if __name__ == "__main__":
    test_compute_function_scores()
    test_determine_mbti_intj()
    test_determine_mbti_intp()
    test_function_ranking()
    test_empty_answers()
    test_mbti_description()
    print("\nAll MBTI tests passed!")
