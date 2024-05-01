import streamlit as st
from typing import Callable
from intro import intro
from social_indicators import social_indicators
from economis_indicators import economic_indicators

# meta title
st.set_page_config(page_title="Data Indicators - North Macedonia")

# cursor pointer on dropdown select
custom_style = "<style>div[data-baseweb='select']>div:hover{cursor:pointer}</style>"
st.markdown(custom_style, unsafe_allow_html=True)

# functions to call when selecting from select box
options: dict[str, Callable] = {
    "Home": intro,
    "Economic Indicators": economic_indicators,
    "Social Indicators": social_indicators,
}

# render select box
if topic := st.sidebar.selectbox(
    label="Choose a Topic",
    options=options.keys(),
    placeholder="Choose a Topic",
):
    options[topic]()
