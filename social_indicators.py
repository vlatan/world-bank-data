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

    st.divider()  ###############################################################################

    title = "Population growth (annual %)"
    description = """
        Annual population growth rate for year t is the exponential rate of growth 
        of midyear population from year t-1 to t, expressed as a percentage. 
        Population is based on the de facto definition of population, which counts 
        all residents regardless of legal status or citizenship.
    """

    write_data("SP.POP.GROW", title=title, description=description)

    st.divider()  ###############################################################################

    title = "Net migration"
    description = """
        Net migration is the net total of migrants during the period, that is, 
        the number of immigrants minus the number of emigrants, 
        including both citizens and noncitizens.
    """

    write_data("SM.POP.NETM", title=title, description=description)

    st.divider()  ###############################################################################

    title = "Human Capital Index (HCI) (scale 0-1)"
    description = """
        The HCI calculates the contributions of health and education to worker productivity. 
        The final index score ranges from zero to one and measures the productivity as a 
        future worker of child born today relative to the benchmark of 
        full health and complete education.
    """

    write_data("HD.HCI.OVRL", title=title, description=description)
