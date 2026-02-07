import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Maintenance Daily Dashboard",
    layout="wide"
)

# =============================
# LOAD DATA FROM GOOGLE SHEET
# =============================
import urllib.parse
import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    sheet_id = "1G_ikK60FZUgctnM7SLZ4Ss0p6demBrlCwIre27fXsco"
    sheet_name = "รายงานประจำวัน"

    sheet_name_encoded = urllib.parse.quote(sheet_name)

    url = (
        f"https://docs.google.com/spreadsheets/d/"
        f"{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name_encoded}"
    )

    df = pd.read_csv(url)
    df["วันที่"] = pd.to_datetime(df["วันที่"], errors="coerce")
    df = df.dropna(subset=["วันที่"])
    return df


df = load_data()

st.title("🛠️ Maintenance Daily Report Dashboard")

# =============================
# FILTER SECTION
# =============================
with st.sidebar:
    st.header("🔎 ตัวกรองข้อมูล")

    start_date, end_date = st.date_input(
        "📅 เลือกวันที่",
        [df["วันที่"].min(), df["วันที่"].max()]
    )

    cond_min, cond_max = st.slider(
        "% การใช้ Condensate",
        float(df["% CON Return"].min()),
        float(df["% CON Return"].max()),
        (
            float(df["% CON Return"].min()),
            float(df["% CON Return"].max())
        )
    )

    steam_min, steam_max = st.slider(
        "การสิ้นเปลืองพลังงาน (Steam)",
        float(df["ยอดรวมการใช้ Steam"].min()),
        float(df["ยอดรวมการใช้ Steam"].max()),
        (
            float(df["ยอดรวมการใช้ Steam"].min()),
            float(df["ยอดรวมการใช้ Steam"].max())
        )
    )

    diff_min, diff_max = st.slider(
        "ประสิทธิภาพการรั่วสตีม (DIFF)",
        float(df["DIFF"].min()),
        float(df["DIFF"].max()),
        (
            float(df["DIFF"].min()),
            float(df["DIFF"].max())
        )
    )

# =============================
# APPLY FILTERS
# =============================
filtered = df[
    (df["วันที่"].between(pd.to_datetime(start_date), pd.to_datetime(end_date))) &
    (df["% CON Return"].between(cond_min, cond_max)) &
    (df["ยอดรวมการใช้ Steam"].between(steam_min, steam_max)) &
    (df["DIFF"].between(diff_min, diff_max))
]

# =============================
# KPI SECTION
# =============================
k1, k2, k3 = st.columns(3)

k1.metric(
    "♻️ Avg % Condensate",
    f"{filtered['% CON Return'].mean():.2f} %"
)

k2.metric(
    "🔥 Avg Steam Usage",
    f"{filtered['ยอดรวมการใช้ Steam'].mean():,.0f}"
)

k3.metric(
    "💨 Avg Steam Loss (DIFF)",
    f"{filtered['DIFF'].mean():.2f}"
)

# =============================
# CHARTS
# =============================
c1, c2 = st.columns(2)

with c1:
    fig1 = px.line(
        filtered,
        x="วันที่",
        y="% CON Return",
        markers=True,
        title="% Condensate Trend"
    )
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    fig2 = px.line(
        filtered,
        x="วันที่",
        y="ยอดรวมการใช้ Steam",
        markers=True,
        title="Steam Usage Trend"
    )
    st.plotly_chart(fig2, use_container_width=True)

fig3 = px.bar(
    filtered,
    x="วันที่",
    y=["ยอดรวมการใช้ Steam", "TARGET"],
    barmode="group",
    title="Steam Usage vs Target"
)
st.plotly_chart(fig3, use_container_width=True)

# =============================
# TABLE
# =============================
st.subheader("📋 รายละเอียดรายงานประจำวัน")
st.dataframe(filtered, use_container_width=True)

