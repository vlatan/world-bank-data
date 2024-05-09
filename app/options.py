import json
import pathlib
import streamlit as st
import functools as ft
from .intro import intro
from typing import Callable
from .utils import write_topic


@st.cache_data(show_spinner="Fetching topics...")
def get_topics() -> dict[str, list[str]]:
    topics_file = pathlib.Path(__file__).parent.resolve() / "topics.json"
    return json.loads(pathlib.Path(topics_file).read_text())


@st.cache_data(show_spinner="Fetching options...")
def make_options(topics: dict[str, list]) -> dict[str, Callable]:
    """
    Constructs a dictionary with key 'topic'
    and value callable for that topic given the input dictionary
    with key topic and value list of indicators.
    """

    options = {}
    for title, indicator_ids in topics.items():

        if (title := title.capitalize()) == "Home":
            options[title] = intro
            continue

        options[title] = ft.partial(write_topic, title, indicator_ids)

    return options


def get_topic_index(options: list[str]) -> int:
    """
    Get the current topic from a 'topic' url query parameter
    and determine its index in the options dictionary keys.
    """

    # if NO "topic" URL query parameters at all, index is zero, meaning home
    if not (query_params := st.query_params.get_all("topic")):
        st.query_params.clear()
        return 0  # Home

    # if "topic" URL query parameter is not in the options, index is zero, meaning home
    if (topic := query_params[0].capitalize()) not in options:
        st.query_params.clear()
        return 0  # Home

    # return the topic index
    return options.index(topic)


def update_query_params() -> None:
    """
    Change page query parameters
    based on the streamlit session state.
    """

    st.query_params.clear()

    if st.session_state.topic == "Home":
        return

    st.query_params.topic = st.session_state.topic.lower()
