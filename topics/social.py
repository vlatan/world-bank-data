import streamlit as st
from utils import write_data


indicators = [
    "SI.POV.DDAY",  # Poverty headcount ratio at $2.15 a day (2017 PPP) (% of population)
    "SP.DYN.LE00.IN",  # "Life expectancy at birth, total (years)"
    "SP.POP.TOTL",  # Population, total
    "SP.POP.GROW",  # Population growth (annual %)
    "SM.POP.NETM",  # Net migration
    "HD.HCI.OVRL",  # Human Capital Index (HCI) (scale 0-1)
]


def social() -> None:
    st.title("Social")
    for indicator in indicators:
        st.divider()
        write_data(indicator)
