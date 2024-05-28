import json
import pathlib
import streamlit as st
from typing import Literal, Iterable


@st.cache_data(show_spinner=False)
def get_topics() -> dict[str, Iterable[str]]:
    """Get topics and their indicator ids from file."""

    topics_file = pathlib.Path(__file__).parent.resolve() / "topics.json"
    return json.loads(pathlib.Path(topics_file).read_text())


def get_select_index(key: str, options: Iterable[str]) -> int:
    """
    Get the current topic or indicator query param from URLS
    and determine its index in the options list.
    If no valid query in URL return index ZERO.
    """

    lower_case_options = [item.lower() for item in options]

    # if NO query_params AT ALL for a given key, index is zero
    # set query param value to first option
    if not (query_params := st.query_params.get_all(key)):
        st.query_params[key] = lower_case_options[0]
        return 0

    # if query param value is not in the options, index is zero
    # set query param value to first option
    if (value := query_params[0]) not in lower_case_options:
        st.query_params[key] = lower_case_options[0]
        return 0

    # return the index of the query param value in options
    return lower_case_options.index(value)


def update_query_param(
    key: Literal["topic", "indicator"], indicator_infos: Iterable[dict[str, str]] = []
) -> None:
    """
    Change topic or indicator query parameter
    based on the streamlit session state.
    """

    # check if there's a topic in question
    if key == "topic" and not indicator_infos:
        st.query_params[key] = st.session_state[key].lower()
        return

    # get indicator title from session
    indicator_title = st.session_state[key]

    # find the indicator id for a given indicator title
    for item in indicator_infos:
        if indicator_title == item.get("title"):
            indicator_id = item.get("id")
            break

    # update the indicator query param
    if indicator_id:
        st.query_params[key] = indicator_id.lower()
