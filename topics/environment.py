import streamlit as st
from utils import write_data


indicators = [
    "EN.ATM.CO2E.PC",  # CO2 emissions (metric tons per capita)
]


def environment():
    st.title("Environment")
    for indicator in indicators:
        st.divider()
        write_data(indicator)
