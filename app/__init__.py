import os
import streamlit as st
from redis import Redis
from dotenv import load_dotenv

from . import options as op
from .write import write_indicator
from .cache import redis_client_ctx
from .countries import get_countries
from .indicator import get_indicators_info


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

    # cursor pointer on dropdown select and h1 link style
    custom_style = """
        <style>
            div[data-baseweb='select'] > div:hover {cursor:pointer}
            h1.main-title > a {text-decoration:none;color:white}
        </style>
    """
    st.html(custom_style)

    # store Redis client object in a context variable
    # to be able to access it in threads down the line
    redis_client = init_redis_client()
    redis_client_ctx.set(redis_client)

    # logo and site title
    custom_h1 = f"<h1 class='main-title'>💢 <a href='/' target = '_self' title='Home'>World Bank Data</a></h1>"
    st.sidebar.markdown(custom_h1, unsafe_allow_html=True)

    st.sidebar.divider()

    # get all countries
    if not (countries := await get_countries()):
        msg = "Couldn't fetch and chart data right now due to World Bank API unavailability."
        st.error(msg)
        return

    if not (topics := op.get_topics()):
        st.error("Coulnd't fetch the topics from disk.")
        return

    topic_label, topic_key = "Select topic", "topic"
    topic_index = op.get_select_index(topic_key, topics.keys())

    # selec topic
    topic_title = st.sidebar.selectbox(
        label=f"{topic_label}:",
        options=topics.keys(),
        placeholder=topic_label,
        index=topic_index,
        key=topic_key,
        on_change=op.update_query_param,
        args=(topic_key,),
    )

    if not topic_title:
        st.error("Please select topic.")
        return

    # write topic title to page
    st.header(topic_title, anchor=False, divider="blue")
    # get indicator ids
    indicator_ids = topics[topic_title]

    # get info for every indicator
    if not (indicator_infos := await get_indicators_info(indicator_ids)):
        st.error("Couldn't fetch idnicators' titles/descriptions.")
        return

    # filter the indicator titles
    indicator_titles = [iid_info.get("title") for iid_info in indicator_infos]
    indicator_label, indicator_key = "Select indicator", "indicator"
    indicator_index = op.get_select_index(indicator_key, indicator_ids)

    # render indicator selectbox
    indicator_title = st.sidebar.selectbox(
        label=f"{indicator_label}:",
        options=indicator_titles,
        placeholder=indicator_label,
        index=indicator_index,
        key=indicator_key,
        on_change=op.update_query_param,
        args=(indicator_key, indicator_infos),
    )

    if not indicator_title:
        st.error("Please select an indicator.")
        return

    for indicator_info in indicator_infos:
        if indicator_title == indicator_info.get("title"):
            break

    # write title and desc to page
    st.subheader(indicator_title, anchor=False)
    st.write(indicator_info.get("description"))

    if not (indicator_id := indicator_info.get("id")):
        st.error("Unknown indicator id.")
        return

    await write_indicator(indicator_id, countries)

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
