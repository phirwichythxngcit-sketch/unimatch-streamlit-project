"""Helpers for keeping questionnaire answers after Streamlit changes pages.

Streamlit removes the state of a widget when that widget is not rendered on a
subsequent run. The answer store below is deliberately separate from widget
state so that navigating to the summary page never resets quiz responses.
"""

from __future__ import annotations

from collections.abc import Iterable, MutableMapping
from typing import Any


DEFAULT_RESPONSE = 3


def answer_key(section: str, category: str, number: int) -> str:
    """Return a stable key for one saved answer."""
    return f"{section}_{category}_{number}"


def widget_key(saved_answer_key: str) -> str:
    """Return a temporary Streamlit widget key for a saved answer."""
    return f"input_{saved_answer_key}"


def initialize_answer_store(
    session_state: MutableMapping[str, Any],
    store_name: str,
    answer_keys: Iterable[str],
) -> None:
    """Create missing saved answers, preserving values from the previous UI.

    Existing apps used the saved-answer key as the widget key. Reading that
    old key once makes this change safe for students who were mid-quiz when
    the new version was deployed.
    """
    answers = session_state.get(store_name)
    if not isinstance(answers, dict):
        answers = {}
        session_state[store_name] = answers

    for key in answer_keys:
        answers.setdefault(key, session_state.get(key, DEFAULT_RESPONSE))


def persist_widget_value(
    session_state: MutableMapping[str, Any],
    store_name: str,
    saved_answer_key: str,
    current_widget_key: str,
) -> None:
    """Copy a changed widget value into its page-independent answer store."""
    session_state[store_name][saved_answer_key] = session_state[current_widget_key]

