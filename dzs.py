import requests
import pandas as pd
import altair as alt
import streamlit as st


st.markdown(
    "<style>div[data-baseweb='select']>div:hover{cursor:pointer}</style>",
    unsafe_allow_html=True,
)

st.title("Бруто-домашен производ")

api_url = "https://makstat.stat.gov.mk/PXWeb/api/v1/mk/MakStat"
url = f"{api_url}/BDP/BDPTrimesecni/BDPsporedESS2010/375_NacSmA_Mk_06RasKv_SA_KA_ml.px"


@st.cache_data
def get_quarters() -> list[str]:
    response = requests.get(url)
    data = response.json()
    data = data["variables"][2]["valueTexts"]
    return [item[:6] for item in data]


@st.cache_data
def get_bdp() -> list[int]:
    payload = {
        "query": [
            {"code": "Категории", "selection": {"filter": "item", "values": ["BDP"]}},
            {"code": "Мерки", "selection": {"filter": "item", "values": ["CP"]}},
        ],
        "response": {"format": "json"},
    }
    response = requests.post(url, json=payload)
    data = response.json()
    return [item["values"][0] for item in data["data"]]


quarters, bdp = get_quarters(), get_bdp()

idx = pd.Index(quarters, name="Тримесечје")
df = pd.DataFrame(data={"БДП": bdp}, index=idx, dtype=int)

# df = df.transpose().reset_index(drop=True)
# df.set_index("Квартал", drop=True, inplace=True)
# df = df.index.set_names("Квартал")
# df.reset_index(drop=True)
# df.reset_index(drop=True, inplace=True)


st.write(
    "#### Бруто-домашен производ според трошочниот метод, по тримесечја, сезонски и календарски прилагодени"
)

st.dataframe(df.transpose())
# st.line_chart(df)

chart = (
    alt.Chart(data=df.reset_index(), title="Тековни цени (мил. денари)")
    .mark_area(opacity=0.3)
    .encode(x="Тримесечје", y="БДП")
)

st.altair_chart(chart, use_container_width=True)
