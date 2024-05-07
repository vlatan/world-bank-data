import streamlit as st
from dotenv import load_dotenv

# meta title - set_page_config needs to be called first in the page
st.set_page_config(page_title="Data Indicators - North Macedonia")

from . import select_box as sb


# load the enviroment variables from an .env file
load_dotenv()


def create_app() -> None:
    """Create streamlit application"""

    # cursor pointer on dropdown select
    custom_style = "<style>div[data-baseweb='select']>div:hover{cursor:pointer}</style>"
    st.markdown(custom_style, unsafe_allow_html=True)

    topics = sb.get_topics()
    options = sb.make_options(topics)
    index = sb.get_topic_index(list(options.keys()))

    # render select box
    if selected_topic := st.sidebar.selectbox(
        label="Choose a Topic",
        options=options.keys(),
        placeholder="Choose a Topic",
        index=index,
        key="topic",
        on_change=sb.update_query_params,
    ):
        options[selected_topic]()
