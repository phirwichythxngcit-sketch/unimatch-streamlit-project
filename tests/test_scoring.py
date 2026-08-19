"""Tests for Scoring Engine"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from logic.scoring import ScoringEngine


def test_compute_interest_scores():
    answers = {}
    for i in range(1, 21):
        answers[f"M_{i}"] = 5
        answers[f"S_{i}"] = 3
        answers[f"L_{i}"] = 1
        answers[f"H_{i}"] = 4
        answers[f"A_{i}"] = 2

    scores = ScoringEngine.compute_interest_scores(answers)
    assert scores["M"]["raw"] == 100
    assert scores["M"]["percentage"] == 100.0
    assert scores["S"]["raw"] == 60
    assert scores["S"]["percentage"] == 60.0
    assert scores["L"]["raw"] == 20
    assert scores["L"]["percentage"] == 20.0
    assert scores["H"]["raw"] == 80
    assert scores["H"]["percentage"] == 80.0
    assert scores["A"]["raw"] == 40
    assert scores["A"]["percentage"] == 40.0
    print("PASS: test_compute_interest_scores")


def test_get_interest_ranking():
    answers = {}
    for i in range(1, 21):
        answers[f"M_{i}"] = 5
        answers[f"S_{i}"] = 3
        answers[f"L_{i}"] = 1
        answers[f"H_{i}"] = 4
        answers[f"A_{i}"] = 2

    scores = ScoringEngine.compute_interest_scores(answers)
    ranking = ScoringEngine.get_interest_ranking(scores)
    assert ranking[0][0] == "M"
    assert ranking[1][0] == "H"
    assert ranking[-1][0] == "L"
    print("PASS: test_get_interest_ranking")


def test_get_top_interest():
    answers = {}
    for i in range(1, 21):
        answers[f"M_{i}"] = 5
        answers[f"S_{i}"] = 3
        answers[f"L_{i}"] = 1
        answers[f"H_{i}"] = 4
        answers[f"A_{i}"] = 2

    scores = ScoringEngine.compute_interest_scores(answers)
    top = ScoringEngine.get_top_interest(scores)
    assert top == "M"
    print("PASS: test_get_top_interest")


def test_compute_financial_profile():
    financial_answers = {
        "F1": "low",
        "F2": "income",
        "F3": "high",
        "F4": "interested",
        "F5": "limited",
        "F6": "flexible",
    }
    profile = ScoringEngine.compute_financial_profile(financial_answers)
    assert profile["F1"] == "low"
    assert profile["F2"] == "income"
    assert profile["F3"] == "high"
    assert profile["F4"] == "interested"
    assert profile["F5"] == "limited"
    assert profile["F6"] == "flexible"
    print("PASS: test_compute_financial_profile")


def test_empty_answers():
    scores = ScoringEngine.compute_interest_scores({})
    for cat in ("M", "S", "L", "H", "A"):
        assert scores[cat]["raw"] == 0
        assert scores[cat]["percentage"] == 0.0
    print("PASS: test_empty_answers")


if __name__ == "__main__":
    test_compute_interest_scores()
    test_get_interest_ranking()
    test_get_top_interest()
    test_compute_financial_profile()
    test_empty_answers()
    print("\nAll Scoring tests passed!")
