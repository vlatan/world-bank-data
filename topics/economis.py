import streamlit as st
from utils import write_data


indicators = [
    "NY.GDP.MKTP.CD",  # GDP (current US$)
    "NY.GDP.PCAP.CD",  # GDP per capita (current US$)
    "NY.GDP.MKTP.KD.ZG",  # GDP growth (annual %)
    "SL.UEM.TOTL.ZS",  # Unemployment (% of total labor force)
    "FP.CPI.TOTL.ZG",  # Inflation, consumer prices (annual %)
    "BX.TRF.PWKR.DT.GD.ZS",  # Personal remittances, received (% of GDP)
]


def economics():
    st.title("Economics")
    for indicator in indicators:
        st.divider()
        write_data(indicator)
