import os
import streamlit as st
from redis import Redis
from . import options as op
from dotenv import load_dotenv


# load the enviroment variables from an .env file
load_dotenv()


def create_app() -> None:
    """Create streamlit application"""

    # meta title - set_page_config needs to be called first in the page
    st.set_page_config(page_title="Data Indicators", initial_sidebar_state="expanded")

    # cursor pointer on dropdown select
    custom_style = "<style>div[data-baseweb='select']>div:hover{cursor:pointer}</style>"
    st.markdown(custom_style, unsafe_allow_html=True)

    @st.cache_resource(show_spinner=False)
    def init_redis_client() -> Redis:
        """Initialize Redis client."""

        return Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            password=os.getenv("REDIS_PASSWORD"),
            client_name="indicator",
        )

    # cache redis client and store it in session
    st.session_state.redis_client = init_redis_client()

    topics = op.get_topics()
    options = op.make_options(topics)
    index = op.get_topic_index(list(options.keys()))

    # render select box
    if selected_topic := st.sidebar.selectbox(
        label="Choose a Topic",
        options=options.keys(),
        placeholder="Choose a Topic",
        index=index,
        key="topic",
        on_change=op.update_query_params,
    ):
        options[selected_topic]()
