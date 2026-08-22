from response_state import answer_key, initialize_answer_store, persist_widget_value, widget_key


def test_answer_store_keeps_answer_after_widget_state_is_removed():
    saved_key = answer_key("cf", "Ne", 0)
    input_key = widget_key(saved_key)
    session_state = {saved_key: 5}  # value used by the previous app version

    initialize_answer_store(session_state, "cognitive_answers", [saved_key])
    assert session_state["cognitive_answers"][saved_key] == 5

    session_state[input_key] = 4
    persist_widget_value(session_state, "cognitive_answers", saved_key, input_key)
    del session_state[input_key]  # Streamlit removes widgets that are not rendered
    session_state.pop(saved_key)

    initialize_answer_store(session_state, "cognitive_answers", [saved_key])
    assert session_state["cognitive_answers"][saved_key] == 4

