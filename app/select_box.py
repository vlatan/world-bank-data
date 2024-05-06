import json
import pathlib
import functools
import streamlit as st
import functools as ft
from .intro import intro
from typing import Callable
from .utils import write_topic


@functools.cache
def get_topics() -> dict[str, list[str]]:
    topics_file = pathlib.Path(__file__).parent.resolve() / "topics.json"
    return json.loads(pathlib.Path(topics_file).read_text())


def make_options(topics: dict[str, list]) -> dict[str, Callable]:
    """
    Constructs a dictionary with key 'topic'
    and value callable for that topic given the input dictionary
    with key topic and value list of indicators.
    """

    options = {}
    for title, indicators in topics.items():

        if (title := title.capitalize()) == "Home":
            options[title] = intro
            continue

        options[title] = ft.partial(write_topic, title, indicators)

    return options


def get_topic_from_query_params(options: dict[str, Callable]) -> str:
    """Gets the current topic from a 'topic' url query parameter."""

    query_params = st.query_params.get_all("topic")
    topic = query_params[0].capitalize() if query_params else "Home"
    topic = topic if topic in options.keys() else "Home"
    return topic


def update_query_params() -> None:
    """
    Change page query parameters
    based on the streamlit session state.
    """

    if not st.session_state.topic:
        return

    if st.session_state.topic == "Home":
        st.query_params.clear()
        return

    st.query_params.topic = st.session_state.topic.lower()
