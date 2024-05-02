import indicators
import streamlit as st
import functools as ft
from intro import intro
from typing import Callable
from utils import write_topic

# meta title
st.set_page_config(page_title="Data Indicators - North Macedonia")

# cursor pointer on dropdown select
custom_style = "<style>div[data-baseweb='select']>div:hover{cursor:pointer}</style>"
st.markdown(custom_style, unsafe_allow_html=True)

# functions to call when selecting from select box
options: dict[str, Callable] = {
    "Home": intro,
    "Economics": ft.partial(write_topic, "Economics", indicators.economics),
    "Social": ft.partial(write_topic, "Social", indicators.social),
    "Environment": ft.partial(write_topic, "Environment", indicators.environment),
    "Institutions": ft.partial(write_topic, "Institutions", indicators.institutions),
}

# render select box
if topic := st.sidebar.selectbox(
    label="Choose a Topic",
    options=options.keys(),
    placeholder="Choose a Topic",
):
    options[topic]()
