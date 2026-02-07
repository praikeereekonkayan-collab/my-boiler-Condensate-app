import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse

st.set_page_config(
    page_title="Boiler Dashboard",
    layout="wide"
)

# =============================
# LOAD DATA FROM GOOGLE SHEET
# =============================
@st.cache_data
def load_data():
    sheet_id = "1G_ikK60FZUgctnM7SLZ4Ss0p6demBrlCwIre27fXsco"
    sheet_name = "condensate"
    sheet_name_encoded = urllib.parse.quote(sheet_name)

    url = (
        f"https://docs.google.com/spreadsheets/d/"
        f"{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name_encoded}"
    )

    df = pd.read_csv(url)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    return df

df = load_data()

# =============================
# SIDEBAR FILTER
# =============================
st.sidebar.header("🔎 Filter")

start_date, end_date = st.sidebar.date_input(
    "เลือกช่วงวันที่",
    [df["date"].min(), df["date"].max()]
)

con_min, con_max = st.sidebar.slider(
    "% Condensate",
    float(df["pct_condensate"].min()),
    float(df["pct_condensate"].max()),
    (float(df["pct_condensate"].min()), float(df["pct_condensate"].max()))
)

steam_min, steam_max = st.sidebar.slider(
    "Steam Loss",
    float(df["steam_loss"].min()),
    float(df["steam_loss"].max()),
    (float(df["steam_loss"].min()), float(df["steam_loss"].max()))
)

diff_min, diff_max = st.sidebar.slider(
    "DIFF",
    float(df["diff"].min()),
    float(df["diff"].max()),
    (float(df["diff"].min()), float(df["diff"].max()))
)

# =============================
# FILTER DATA
# =============================
filtered = df[
    (df["date"].between(pd.to_datetime(start_date), pd.to_datetime(end_date))) &
    (df["pct_condensate"].between(con_min, con_max)) &
    (df["steam_loss"].between(steam_min, steam_max)) &
    (df["diff"].between(diff_min, diff_max))
].copy()
if filtered.empty:
    st.warning("⚠️ ไม่มีข้อมูลในช่วงที่เลือก")
    st.stop()


# =============================
# TITLE
# =============================
st.title("🏭 Boiler & Condensate Dashboard")

# =============================
# KPI
# =============================
c1, c2, c3 = st.columns(3)
c1.metric("♻️ % Condensate Avg", f"{filtered['pct_condensate'].mean():.2f}%")
c2.metric("🔥 Steam Loss Avg", f"{filtered['steam_loss'].mean():.2f}")
c3.metric("💨 DIFF Avg", f"{filtered['diff'].mean():.2f}")

# =============================
# CHART
# =============================
fig = px.line(
    filtered,
    x="date",
    y=["pct_condensate", "steam_loss"],
    markers=True
)
st.plotly_chart(fig, use_container_width=True)

# =============================
# TABLE
# =============================
st.subheader("📋 Daily Report")
st.dataframe(filtered, use_container_width=True)



