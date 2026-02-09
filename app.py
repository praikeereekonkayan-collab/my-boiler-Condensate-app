import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="Condensate Dashboard",
    layout="wide"
)

st.title("💧 Condensate Return Dashboard")

# =============================
# LOAD DATA
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


data = load_data()

# =============================
# DATE FILTER
# =============================
st.subheader("📅 เลือกช่วงเวลา")

start_date, end_date = st.date_input(
    "ช่วงวันที่",
    [data["date"].min(), data["date"].max()]
)

filtered = data[
    (data["date"] >= pd.to_datetime(start_date)) &
    (data["date"] <= pd.to_datetime(end_date))
]

# =============================
# VIEW TYPE
# =============================
view_type = st.radio(
    "รูปแบบการดูข้อมูล",
    ["รายวัน", "รายเดือน", "รายปี"],
    horizontal=True
)

if view_type == "รายเดือน":
    filtered["month"] = filtered["date"].dt.to_period("M").astype(str)
    group_col = "month"

elif view_type == "รายปี":
    filtered["year"] = filtered["date"].dt.year
    group_col = "year"

else:
    group_col = "date"

summary = filtered.groupby(group_col).agg({
    "steam_loss": "sum",
    "condensate_return": "sum",
    "pct_condensate": "mean"
}).reset_index()

# =============================
# KPI
# =============================
st.subheader("📊 สรุปภาพรวม")

col1, col2, col3 = st.columns(3)

col1.metric(
    "🔥 Steam Loss รวม",
    f"{summary['steam_loss'].sum():,.0f}"
)

col2.metric(
    "💧 Condensate Return รวม",
    f"{summary['condensate_return'].sum():,.0f}"
)

col3.metric(
    "📈 % Condensate Return เฉลี่ย",
    f"{summary['pct_condensate'].mean():.1f} %"
)

# =============================
# GRAPH 1 : STEAM vs CONDENSATE
# =============================
st.subheader("🔥 Steam Loss เทียบ 💧 Condensate Return")

fig1 = px.bar(
    summary,
    x=group_col,
    y=["steam_loss", "condensate_return"],
    barmode="group",
    labels={"value": "ปริมาณ", group_col: "เวลา"}
)

st.plotly_chart(fig1, use_container_width=True)

# =============================
# GRAPH 2 : % CONDENSATE
# =============================
st.subheader("📈 เปอร์เซ็นต์ Condensate Return")

fig2 = px.line(
    summary,
    x=group_col,
    y="pct_condensate",
    markers=True,
    labels={
        "pct_condensate": "% Condensate Return",
        group_col: "เวลา"
    }
)

st.plotly_chart(fig2, use_container_width=True)

# =============================
# TABLE
# =============================
st.subheader("📋 ตารางข้อมูล")

st.dataframe(summary, use_container_width=True)
st.subheader("📊 สรุปภาพรวมผู้บริหาร")

avg_pct = summary["pct_condensate"].mean()

if avg_pct >= TARGET_PCT:
    status = "🟢 ดีมาก (ผ่านเป้า)"
elif avg_pct >= TARGET_PCT - 5:
    status = "🟡 เฝ้าระวัง"
else:
    status = "🔴 ต่ำกว่าเป้า"

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "📈 % Condensate Return เฉลี่ย",
    f"{avg_pct:.1f} %"
)

col2.metric(
    "🎯 Target",
    f"{TARGET_PCT} %"
)

col3.metric(
    "🔥 Steam Loss รวม",
    f"{summary['steam_loss'].sum():,.0f}"
)

col4.metric(
    "🚦 สถานะระบบ",
    status
)
st.subheader("📈 เปอร์เซ็นต์ Condensate Return เทียบ Target")

fig2 = px.line(
    summary,
    x=group_col,
    y="pct_condensate",
    markers=True,
    labels={
        "pct_condensate": "% Condensate Return",
        group_col: "เวลา"
    }
)

# เส้น Target
fig2.add_hline(
    y=TARGET_PCT,
    line_dash="dash",
    annotation_text="Target",
    annotation_position="top left"
)

st.plotly_chart(fig2, use_container_width=True)



