import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="Boiler & Condensate Dashboard",
    layout="wide"
)

# =============================
# LOAD DATA
# =============================
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

    # แปลงวันที่
    df["วันที่"] = pd.to_datetime(df["วันที่"], errors="coerce")
    df = df.dropna(subset=["วันที่"])

    return df

df = load_data()

# =============================
# TITLE
# =============================
st.title("🏭 Boiler & Condensate Performance Dashboard")
st.caption("ข้อมูลจากรายงานประจำวัน (Google Sheet)")

# =============================
# SIDEBAR FILTER
# =============================
with st.sidebar:
    st.header("🔎 ตัวกรองข้อมูล")

    # Date filter
    start_date, end_date = st.date_input(
        "📅 เลือกช่วงวันที่",
        [df["วันที่"].min(), df["วันที่"].max()]
    )

    # % Condensate
    con_min, con_max = st.slider(
        "% คอนเดนเสท (CON Return)",
        float(df["% CON Return"].min()),
        float(df["% CON Return"].max()),
        (
            float(df["% CON Return"].min()),
            float(df["% CON Return"].max())
        )
    )

    # Steam usage
    steam_min, steam_max = st.slider(
        "การใช้สตีม (รวม)",
        float(df["สรุปยอดรวมการใช้สตีม"].min()),
        float(df["สรุปยอดรวมการใช้สตีม"].max()),
        (
            float(df["สรุปยอดรวมการใช้สตีม"].min()),
            float(df["สรุปยอดรวมการใช้สตีม"].max())
        )
    )

    # DIFF
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
# APPLY FILTER
# =============================
filtered = df[
    (df["วันที่"].between(pd.to_datetime(start_date), pd.to_datetime(end_date))) &
    (df["% CON Return"].between(con_min, con_max)) &
    (df["สรุปยอดรวมการใช้สตีม"].between(steam_min, steam_max)) &
    (df["DIFF"].between(diff_min, diff_max))
]

# =============================
# KPI SECTION
# =============================
k1, k2, k3 = st.columns(3)

k1.metric(
    "♻️ % คอนเดนเสท เฉลี่ย",
    f"{filtered['% CON Return'].mean():.2f} %"
)

k2.metric(
    "🔥 การใช้สตีมเฉลี่ย",
    f"{filtered['สรุปยอดรวมการใช้สตีม'].mean():,.0f}"
)

k3.metric(
    "💨 Steam Loss (DIFF)",
    f"{filtered['DIFF'].mean():.2f}"
)

st.divider()

# =============================
# CHARTS
# =============================
c1, c2 = st.columns(2)

with c1:
    fig_con = px.line(
        filtered,
        x="วันที่",
        y="% CON Return",
        markers=True,
        title="% Condensate Return Trend"
    )
    st.plotly_chart(fig_con, use_container_width=True)

with c2:
    fig_steam = px.line(
        filtered,
        x="วันที่",
        y="สรุปยอดรวมการใช้สตีม",
        markers=True,
        title="Steam Usage Trend"
    )
    st.plotly_chart(fig_steam, use_container_width=True)

# Steam vs Target
fig_target = px.bar(
    filtered,
    x="วันที่",
    y=["สรุปยอดรวมการใช้สตีม", "TARGET"],
    barmode="group",
    title="Steam Usage vs Target"
)
st.plotly_chart(fig_target, use_container_width=True)

# =============================
# DATA TABLE
# =============================
st.subheader("📋 ตารางรายละเอียดรายงานประจำวัน")
st.dataframe(filtered, use_container_width=True)


