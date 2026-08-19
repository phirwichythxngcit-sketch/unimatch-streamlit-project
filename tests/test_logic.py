"""Tests for Logic Engine"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from logic.logic_engine import LogicEngine, Proposition


def test_and_true():
    engine = LogicEngine()
    P = Proposition("P", True)
    Q = Proposition("Q", True)
    result = engine.AND(P, Q)
    assert result.value is True
    print("PASS: test_and_true")


def test_and_false():
    engine = LogicEngine()
    P = Proposition("P", True)
    Q = Proposition("Q", False)
    result = engine.AND(P, Q)
    assert result.value is False
    print("PASS: test_and_false")


def test_or_true():
    engine = LogicEngine()
    P = Proposition("P", False)
    Q = Proposition("Q", True)
    result = engine.OR(P, Q)
    assert result.value is True
    print("PASS: test_or_true")


def test_or_false():
    engine = LogicEngine()
    P = Proposition("P", False)
    Q = Proposition("Q", False)
    result = engine.OR(P, Q)
    assert result.value is False
    print("PASS: test_or_false")


def test_not():
    engine = LogicEngine()
    P = Proposition("P", True)
    result = engine.NOT(P)
    assert result.value is False
    assert result.name == "¬P"

    P2 = Proposition("Q", False)
    result2 = engine.NOT(P2)
    assert result2.value is True
    print("PASS: test_not")


def test_evaluate_condition():
    engine = LogicEngine()
    result = engine.evaluate_condition(70, ">", 65)
    assert result.value is True

    result2 = engine.evaluate_condition(50, ">", 65)
    assert result2.value is False

    result3 = engine.evaluate_condition(60, ">=", 60)
    assert result3.value is True
    print("PASS: test_evaluate_condition")


def test_evaluate_mbti_condition():
    engine = LogicEngine()
    result = engine.evaluate_mbti_condition("INTP", ["INTJ", "INTP", "ISTP"])
    assert result.value is True

    result2 = engine.evaluate_mbti_condition("ESFJ", ["INTJ", "INTP", "ISTP"])
    assert result2.value is False
    print("PASS: test_evaluate_mbti_condition")


def test_evaluate_academic_condition():
    engine = LogicEngine()
    result = engine.evaluate_academic_condition(70, 60, "M")
    assert result.value is True

    result2 = engine.evaluate_academic_condition(50, 60, "M")
    assert result2.value is False
    print("PASS: test_evaluate_academic_condition")


def test_truth_table():
    engine = LogicEngine()
    table = engine.get_truth_table()
    assert len(table) == 4

    assert table[0]["P"] is True
    assert table[0]["Q"] is True
    assert table[0]["P ∧ Q"] is True
    assert table[0]["P ∨ Q"] is True
    assert table[0]["¬P"] is False

    assert table[3]["P"] is False
    assert table[3]["Q"] is False
    assert table[3]["P ∧ Q"] is False
    assert table[3]["P ∨ Q"] is False
    assert table[3]["¬P"] is True
    print("PASS: test_truth_table")


def test_complex_expression():
    engine = LogicEngine()
    P = engine.evaluate_condition(70, ">=", 60)
    Q = engine.evaluate_condition(55, ">=", 45)
    R = engine.evaluate_mbti_condition("INTP", ["INTJ", "INTP", "ISTP", "ENTP", "ISTJ"])
    result = engine.AND(P, Q, R)
    assert result.value is True

    R2 = engine.evaluate_mbti_condition("ESFJ", ["INTJ", "INTP", "ISTP", "ENTP", "ISTJ"])
    result2 = engine.AND(P, Q, R2)
    assert result2.value is False
    print("PASS: test_complex_expression")


def test_format_proposition_result():
    engine = LogicEngine()
    P = Proposition("M >= 65", True)
    result = engine.format_proposition_result(P)
    assert "✅" in result
    assert "True" in result

    Q = Proposition("S >= 45", False)
    result2 = engine.format_proposition_result(Q)
    assert "❌" in result2
    assert "False" in result2
    print("PASS: test_format_proposition_result")


if __name__ == "__main__":
    test_and_true()
    test_and_false()
    test_or_true()
    test_or_false()
    test_not()
    test_evaluate_condition()
    test_evaluate_mbti_condition()
    test_evaluate_academic_condition()
    test_truth_table()
    test_complex_expression()
    test_format_proposition_result()
    print("\nAll Logic tests passed!")
