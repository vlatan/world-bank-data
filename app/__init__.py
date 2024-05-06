from typing import Callable
import streamlit as st
import functools as ft
from .intro import intro
from dotenv import load_dotenv
from .utils import get_topics, write_topic


# load the enviroment variables from an .env file
load_dotenv()


def create_app() -> None:
    """Create streamlit application"""

    # meta title
    st.set_page_config(page_title="Data Indicators - North Macedonia")

    # cursor pointer on dropdown select
    custom_style = "<style>div[data-baseweb='select']>div:hover{cursor:pointer}</style>"
    st.markdown(custom_style, unsafe_allow_html=True)

    def make_options(topics: dict[str, list]) -> dict[str, Callable]:
        """
        Constructs a dictionary with key topic
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

    topics = get_topics()
    options = make_options(topics)
    topic = get_topic_from_query_params(options)
    index = list(options.keys()).index(topic)

    # render select box
    if selected_topic := st.sidebar.selectbox(
        label="Choose a Topic",
        options=options.keys(),
        placeholder="Choose a Topic",
        index=index,
        key="topic",
        on_change=update_query_params,
    ):
        options[selected_topic]()
