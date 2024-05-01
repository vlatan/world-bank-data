import streamlit as st
from utils import write_data


def social_indicators() -> None:

    st.title("Social Indicators")

    st.divider()  ###############################################################################

    title = "Poverty headcount ratio at $2.15 a day (2017 PPP) (% of population)"
    description = """
        Poverty headcount ratio at \$2.15 a day is the percentage of the population 
        living on less than \$2.15 a day at 2017 purchasing power adjusted prices. 
        As a result of revisions in PPP exchange rates, poverty rates for individual 
        countries cannot be compared with poverty rates reported in earlier editions.
    """

    write_data("SI.POV.DDAY", title=title, description=description)

    st.divider()  ###############################################################################

    title = "Life expectancy at birth, total (years)"
    description = """
        Life expectancy at birth indicates the number of years a newborn infant would 
        live if prevailing patterns of mortality at the time of its birth were to stay 
        the same throughout its life.
    """

    write_data("SP.DYN.LE00.IN", title=title, description=description)

    st.divider()  ###############################################################################

    title = "Population, total"
    description = """
        Total population is based on the de facto definition of population, 
        which counts all residents regardless of legal status or citizenship. 
        The values shown are midyear estimates.
    """

    write_data("SP.POP.TOTL", title=title, description=description)
