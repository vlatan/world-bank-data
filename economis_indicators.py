import streamlit as st
from utils import write_data


def economic_indicators():

    st.title("Economic Indicators - North Macedonia")

    st.divider()  ###############################################################################

    title = "GDP (current US$)"
    description = """GDP at purchaser's prices is the sum of gross value added by all 
        resident producers in the economy plus any product taxes and minus 
        any subsidies not included in the value of the products. 
        It is calculated without making deductions for depreciation of 
        fabricated assets or for depletion and degradation of natural resources. 
        Data are in current U.S. dollars. Dollar figures for GDP are converted 
        from domestic currencies using single year official exchange rates."""
    write_data("NY.GDP.MKTP.CD", title=title, description=description)

    st.divider()  ###############################################################################

    title = "GDP per capita (current US$)"
    description = """GDP per capita is gross domestic product divided by midyear population. 
        GDP is the sum of gross value added by all resident producers in the economy 
        plus any product taxes and minus any subsidies not included in the value of the products. 
        It is calculated without making deductions for depreciation of fabricated assets or 
        for depletion and degradation of natural resources. Data are in current U.S. dollars."""
    write_data("NY.GDP.PCAP.CD", title=title, description=description)

    st.divider()  ###############################################################################

    title = "GDP growth (annual %)"
    description = """Annual percentage growth rate of GDP at market prices based on constant local currency. 
    Aggregates are based on constant 2015 prices, expressed in U.S. dollars. 
    GDP is the sum of gross value added by all resident producers in the economy 
    plus any product taxes and minus any subsidies not included in the value of the products. 
    It is calculated without making deductions for depreciation of fabricated assets or 
    for depletion and degradation of natural resources."""
    write_data("NY.GDP.MKTP.KD.ZG", title=title, description=description)

    st.divider()  ###############################################################################

    title = "Unemployment (% of total labor force)"
    description = """Unemployment refers to the share of the labor force that is 
    without work but available for and seeking employment."""
    write_data("SL.UEM.TOTL.ZS", title=title, description=description)

    st.divider()  ###############################################################################

    title = "Inflation, consumer prices (annual %)"
    description = """Inflation as measured by the consumer price index reflects 
    the annual percentage change in the cost to the average consumer of acquiring 
    a basket of goods and services that may be fixed or changed at specified intervals, 
    such as yearly. The Laspeyres formula is generally used."""
    write_data("FP.CPI.TOTL.ZG", title=title, description=description)

    st.divider()  ###############################################################################

    title = "Personal remittances, received (% of GDP)"
    description = """Personal remittances comprise personal transfers and compensation of employees. 
    Personal transfers consist of all current transfers in cash or in kind made or received by resident 
    households to or from nonresident households. Personal transfers thus include all current transfers 
    between resident and nonresident individuals. Compensation of employees refers to the income of border, 
    seasonal, and other short-term workers who are employed in an economy where they are not resident and
    of residents employed by nonresident entities. Data are the sum of two items defined in the sixth 
    edition of the IMF's Balance of Payments Manual: personal transfers and compensation of employees."""
    write_data("BX.TRF.PWKR.DT.GD.ZS", title=title, description=description)
