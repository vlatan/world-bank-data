import os
import streamlit as st
from redis import Redis
from . import options as op
from dotenv import load_dotenv
from .cache import redis_client_ctx


# load the enviroment variables from an .env file
load_dotenv()


async def create_app() -> None:
    """Create streamlit application"""

    # meta title - set_page_config needs to be called first in the page
    st.set_page_config(
        page_title="World Bank Data - Overview",
        initial_sidebar_state="expanded",
        page_icon=":anger:",
    )

    # cursor pointer on dropdown select
    custom_style = "<style>div[data-baseweb='select']>div:hover{cursor:pointer}</style>"
    st.html(custom_style)

    # store Redis client object in a context variable
    # to be able to access it in threads down the line
    redis_client = init_redis_client()
    redis_client_ctx.set(redis_client)

    topics = op.get_topics()
    options = op.make_options(topics)
    index = op.get_topic_index(list(options.keys()))

    st.sidebar.title(":anger:  World Bank Data")

    st.sidebar.divider()

    # render select box
    if selected_topic := st.sidebar.selectbox(
        label="Select topic:",
        options=options.keys(),
        placeholder="Choose a Topic",
        index=index,
        key="topic",
        on_change=op.update_query_params,
    ):
        await options[selected_topic]()

    st.sidebar.divider()

    st.sidebar.write("Source: https://data.worldbank.org")


@st.cache_resource(show_spinner=False)
def init_redis_client(client_name: str = "world_bank_cache") -> Redis:
    """Initialize Redis client."""

    return Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        password=os.getenv("REDIS_PASSWORD"),
        client_name=client_name,
    )
