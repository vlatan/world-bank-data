import streamlit as st
from typing import Callable
from intro import intro
from topics.social import social
from topics.economis import economics
from topics.environment import environment

# meta title
st.set_page_config(page_title="Data Indicators - North Macedonia")

# cursor pointer on dropdown select
custom_style = "<style>div[data-baseweb='select']>div:hover{cursor:pointer}</style>"
st.markdown(custom_style, unsafe_allow_html=True)

# functions to call when selecting from select box
options: dict[str, Callable] = {
    "Home": intro,
    "Economics": economics,
    "Social": social,
    "Environment": environment,
}

# render select box
if topic := st.sidebar.selectbox(
    label="Choose a Topic",
    options=options.keys(),
    placeholder="Choose a Topic",
):
    options[topic]()
