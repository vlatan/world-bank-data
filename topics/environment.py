import streamlit as st
from utils import write_data


def environment():

    st.title("Environment")

    st.divider()  ###############################################################################

    title = "CO2 emissions (metric tons per capita)"
    description = """
        Carbon dioxide emissions are those stemming from the burning of fossil 
        fuels and the manufacture of cement. They include carbon dioxide produced 
        during consumption of solid, liquid, and gas fuels and gas flaring.
    """
    write_data("EN.ATM.CO2E.PC", title=title, description=description)
