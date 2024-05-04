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

    options = {}  # functions to call when selecting from select box
    for title, indicators in get_topics().items():

        if (title := title.capitalize()) == "Home":
            options[title] = intro
            continue

        options[title] = ft.partial(write_topic, title, indicators)

    # render select box
    if topic := st.sidebar.selectbox(
        label="Choose a Topic",
        options=options.keys(),
        placeholder="Choose a Topic",
    ):
        options[topic]()
