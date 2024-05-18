import json
import pathlib
import streamlit as st
import functools as ft
from typing import Callable
from .utils import write_topic


@st.cache_data(show_spinner=False)
def get_topics() -> dict[str, list[str]]:
    topics_file = pathlib.Path(__file__).parent.resolve() / "topics.json"
    return json.loads(pathlib.Path(topics_file).read_text())


@st.cache_data(show_spinner=False)
def make_options(topics: dict[str, list]) -> dict[str, Callable]:
    """
    Constructs a dictionary with key 'topic'
    and value callable for that topic given the input dictionary
    with key topic and value list of indicators.
    """

    options = {}
    for title, indicator_ids in topics.items():
        title = title.capitalize()
        options[title] = ft.partial(write_topic, title, indicator_ids)
    return options


def get_topic_index(options: list[str]) -> int:
    """
    Get the current topic from a 'topic' url query parameter
    and determine its index in the options dictionary keys.
    If no valid topic query in URL se topuc query value to HOME.
    """

    # if NO "topic" URL query parameters at all index is zero
    # set topic query param value to first option
    if not (query_params := st.query_params.get_all("topic")):
        st.query_params.topic = options[0].lower()
        return 0

    # if "topic" URL query parameter is not in the options index is zero
    # set topic query param value to first option
    if (topic := query_params[0].capitalize()) not in options:
        st.query_params.topic = options[0].lower()
        return 0

    # return the topic index
    return options.index(topic)


def update_query_params() -> None:
    """
    Change topic query parameters
    based on the streamlit session state.
    """

    st.query_params.topic = st.session_state.topic.lower()
