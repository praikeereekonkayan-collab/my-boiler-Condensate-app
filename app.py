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
st.subheader("📈 Trend by Date")

col1, col2, col3 = st.columns(3)

# % Condensate
with col1:
    fig1 = px.line(
        filtered,
        x="date",
        y="pct_condensate",
        markers=True,
        title="% Condensate"
    )

    fig1.add_hline(
        y=TARGET_COND,
        line_dash="dash",
        line_color="red",
        annotation_text="Target",
        annotation_position="top left"
    )

    st.plotly_chart(fig1, use_container_width=True)
fig2 = px.line(
    plot_df,
    x="date" if view_type != "รายปี" else "year",
    y="steam_loss",
    title="Steam Loss",
    markers=True
)

# Steam Loss

    fig2.add_hline(
        y=TARGET_STEAM_LOSS,
        line_dash="dash",
        line_color="red",
        annotation_text="Target",
        annotation_position="top left"
    )

    st.plotly_chart(fig2, use_container_width=True)

# DIFF
with col3:
    fig3 = px.line(
        filtered,
        x="date",
        y="diff",
        markers=True,
        title="DIFF"
    )
    st.plotly_chart(fig3, use_container_width=True)

# =============================
# TABLE
# =============================
st.subheader("📋 Daily Report")
st.dataframe(filtered, use_container_width=True)
st.subheader("📆 เลือกรูปแบบเวลา")

view_type = st.radio(
    "",
    ["รายวัน", "รายเดือน", "รายปี"],
    horizontal=True
)

plot_df = filtered.copy()

if view_type == "รายเดือน":
    plot_df = (
        plot_df
        .groupby(plot_df["date"].dt.to_period("M"))
        .mean()
        .reset_index()
    )
    plot_df["date"] = plot_df["date"].dt.to_timestamp()

elif view_type == "รายปี":
    plot_df = (
        plot_df
        .groupby(plot_df["date"].dt.year)
        .mean()
        .reset_index()
    )
    plot_df.rename(columns={"date": "year"}, inplace=True)
def kpi(label, value, low, high, unit=""):
    if value < low:
        color = "🔵"
    elif value > high:
        color = "🔴"
    else:
        color = "🟢"
    return f"{color} {value:.2f}{unit}"

c1, c2, c3 = st.columns(3)

c1.metric(
    "♻️ % Condensate Avg",
    kpi("% Condensate", filtered["pct_condensate"].mean(), 0.59, 1.22, "%")
)

c2.metric(
    "🔥 Steam Loss Avg",
    kpi("Steam Loss", filtered["steam_loss"].mean(), 0, 116)
)

c3.metric(
    "💨 DIFF Avg",
    kpi("DIFF", filtered["diff"].mean(), -0.26, 0.53)
)
st.subheader("📊 Overview Trend")

col1, col2, col3 = st.columns(3)

with col1:
    fig1 = px.line(
        plot_df,
        x="date" if view_type != "รายปี" else "year",
        y="pct_condensate",
        title="% Condensate",
        markers=True
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.line(
        plot_df,
        x="date" if view_type != "รายปี" else "year",
        y="steam_loss",
        title="Steam Loss",
        markers=True
    )
    st.plotly_chart(fig2, use_container_width=True)

with col3:
    fig3 = px.line(
        plot_df,
        x="date" if view_type != "รายปี" else "year",
        y="diff",
        title="DIFF",
        markers=True
    )
    st.plotly_chart(fig3, use_container_width=True)
# =============================
# TARGET / SPEC
# =============================
TARGET_COND = 0.90          # %
TARGET_STEAM_LOSS = 80      # unit ตามข้อมูลจริง
TARGET_DIFF = 0.00

    plot_df,
    x="date" if view_type != "รายปี" else "year",
    y="steam_loss",
    title="Steam Loss",
    markers=True
)

fig2.add_hline(
    y=TARGET_STEAM_LOSS,
    line_dash="dash",
    line_color="red",
    annotation_text="Target",
    annotation_position="top left"
)

st.plotly_chart(fig2, use_container_width=True)
fig3 = px.line(
    plot_df,
    x="date" if view_type != "รายปี" else "year",
    y="diff",
    title="DIFF",
    markers=True
)

fig3.add_hline(
    y=TARGET_DIFF,
    line_dash="dash",
    line_color="red",
    annotation_text="Target",
    annotation_position="top left"
)

st.plotly_chart(fig3, use_container_width=True)
# =============================
# COST SETTING
# =============================
COST_PER_UNIT_STEAM = 120   # บาท / หน่วย (พี่แก้ตามจริง)
filtered["excess_steam"] = (
    filtered["steam_loss"] - TARGET_STEAM_LOSS
).clip(lower=0)

filtered["cost_loss"] = (
    filtered["excess_steam"] * COST_PER_UNIT_STEAM
)
c1, c2, c3, c4 = st.columns(4)

c1.metric("♻️ % Condensate Avg", f"{filtered['pct_condensate'].mean():.2f}%")
c2.metric("🔥 Steam Loss Avg", f"{filtered['steam_loss'].mean():.2f}")
c3.metric("💨 DIFF Avg", f"{filtered['diff'].mean():.2f}")
c4.metric("💰 Cost Loss (฿)", f"{filtered['cost_loss'].sum():,.0f}")
