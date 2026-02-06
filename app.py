import streamlit as st
import pandas as pd
import plotly.express as px
import pandas as pd

SHEET_ID = "1G_ikK60FZUgctnM7SLZ4Ss0p6demBrlCwIre27fXsco"
SHEET_NAME = "CONDENSATE"

csv_url = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/"
    f"gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"
)

df = pd.read_csv(csv_url)

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(
    page_title="Condensate Boiler Dashboard",
    layout="wide"
)

# -----------------------------
# CONNECT GOOGLE SHEET
# -----------------------------

    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"



SHEET_ID = "1G_ikK60FZUgctnM7SLZ4Ss0p6demBrlCwIre27fXsco

# -----------------------------
# CLEAN DATA
# -----------------------------
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.dropna(subset=["date"])

df["pct_condensate"] = (
    df["condensate_ton"] / df["steam_ton"] * 100
).where(df["steam_ton"] > 0)

df["pct_condensate"] = df["pct_condensate"].round(2)

# -----------------------------
# SIDEBAR FILTER
# -----------------------------
st.sidebar.header("🔎 เลือกช่วงเวลา")

year = st.sidebar.selectbox(
    "เลือกปี",
    sorted(df["date"].dt.year.unique())
)

month = st.sidebar.selectbox(
    "เลือกเดือน",
    ["ทั้งหมด"] + list(range(1, 13))
)

filtered = df[df["date"].dt.year == year]

if month != "ทั้งหมด":
    filtered = filtered[filtered["date"].dt.month == month]

# -----------------------------
# KPI
# -----------------------------
st.title("🏭 Condensate Boiler Dashboard")

col1, col2, col3 = st.columns(3)

col1.metric(
    "💨 Steam (ตัน)",
    f"{filtered['steam_ton'].sum():,.0f}"
)

col2.metric(
    "💧 Condensate (ตัน)",
    f"{filtered['condensate_ton'].sum():,.0f}"
)

col3.metric(
    "📊 %Condensate เฉลี่ย",
    f"{filtered['pct_condensate'].mean():.2f} %"
)

# -----------------------------
# GRAPH
# -----------------------------
st.subheader("📈 % Condensate รายวัน")

daily = (
    filtered.groupby(filtered["date"].dt.date)["pct_condensate"]
    .mean()
    .reset_index()
)

fig = px.line(
    daily,
    x="date",
    y="pct_condensate",
    markers=True
)

fig.update_layout(
    xaxis_title="วันที่",
    yaxis_title="% Condensate",
    height=450
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# TABLE
# -----------------------------
st.subheader("📋 ตารางข้อมูล")
st.dataframe(filtered)

TARGET = 80  # % condensate target
def traffic_color(value, target):
    if pd.isna(value):
        return "⚪"
    if value >= target:
        return "🟢"
    elif value >= target - 5:
        return "🟡"
    else:
        return "🔴"
avg_pct = filtered["pct_condensate"].mean()
status_icon = traffic_color(avg_pct, TARGET)

col1, col2, col3, col4 = st.columns(4)

col1.metric("💨 Steam (ตัน)", f"{filtered['steam_ton'].sum():,.0f}")
col2.metric("💧 Condensate (ตัน)", f"{filtered['condensate_ton'].sum():,.0f}")
col3.metric("📊 %Condensate เฉลี่ย", f"{avg_pct:.2f} %")
col4.metric("🚦 สถานะ", status_icon)
daily = (
    filtered.groupby(filtered["date"].dt.date)["pct_condensate"]
    .mean()
    .reset_index()
)

daily["status"] = daily["pct_condensate"].apply(
    lambda x: "เขียว" if x >= TARGET else
              "เหลือง" if x >= TARGET - 5 else
              "แดง"
)
fig = px.scatter(
    daily,
    x="date",
    y="pct_condensate",
    color="status",
    color_discrete_map={
        "เขียว": "green",
        "เหลือง": "orange",
        "แดง": "red"
    }
)

fig.add_hline(
    y=TARGET,
    line_dash="dash",
    annotation_text="Target"
)

fig.update_layout(
    xaxis_title="วันที่",
    yaxis_title="% Condensate",
    height=450
)

st.plotly_chart(fig, use_container_width=True)
filtered["สถานะ"] = filtered["pct_condensate"].apply(
    lambda x: traffic_color(x, TARGET)
)
st.dataframe(
    filtered,
    use_container_width=True
)

