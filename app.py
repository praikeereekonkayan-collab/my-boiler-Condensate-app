import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(
    page_title="Condensate Boiler Dashboard",
    layout="wide"
)

TARGET = 80
WARNING_GAP = 5

# -----------------------------
# LOAD GOOGLE SHEET (CSV)
# -----------------------------
SHEET_ID = "1G_ikK60FZUgctnM7SLZ4Ss0p6demBrlCwIre27fXsco"
SHEET_NAME = "CONDENSATE"

csv_url = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/"
    f"gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"
)

df = pd.read_csv(csv_url)

# -----------------------------
# CLEAN DATA
# -----------------------------
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.dropna(subset=["date"])

df["pct_condensate"] = (
    df["condensate_ton"] / df["steam_ton"] * 100
).where(df["steam_ton"] > 0)

df["pct_condensate"] = df["pct_condensate"].round(2)

def traffic_light(value):
    if pd.isna(value):
        return "⚪"
    elif value >= TARGET:
        return "🟢"
    elif value >= TARGET - WARNING_GAP:
        return "🟡"
    else:
        return "🔴"

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.header("🔎 ตัวกรอง")

view_mode = st.sidebar.radio(
    "รูปแบบการดู",
    ["รายวัน", "รายเดือน", "รายปี"]
)

year = st.sidebar.selectbox(
    "เลือกปี",
    sorted(df["date"].dt.year.unique())
)

filtered = df[df["date"].dt.year == year]

# -----------------------------
# SUMMARY
# -----------------------------
if view_mode == "รายวัน":
    summary = filtered.groupby(filtered["date"].dt.date).agg(
        steam_ton=("steam_ton", "sum"),
        condensate_ton=("condensate_ton", "sum"),
        pct_condensate=("pct_condensate", "mean")
    ).reset_index()

elif view_mode == "รายเดือน":
    summary = filtered.groupby(filtered["date"].dt.to_period("M")).agg(
        steam_ton=("steam_ton", "sum"),
        condensate_ton=("condensate_ton", "sum"),
        pct_condensate=("pct_condensate", "mean")
    ).reset_index()
    summary["date"] = summary["date"].astype(str)

else:
    summary = df.groupby(df["date"].dt.year).agg(
        steam_ton=("steam_ton", "sum"),
        condensate_ton=("condensate_ton", "sum"),
        pct_condensate=("pct_condensate", "mean")
    ).reset_index()
    summary.rename(columns={"date": "year"}, inplace=True)

summary["status"] = summary["pct_condensate"].apply(traffic_light)

# -----------------------------
# KPI
# -----------------------------
st.title("🏭 Condensate Boiler Dashboard")

avg_pct = summary["pct_condensate"].mean()

c1, c2, c3, c4 = st.columns(4)
c1.metric("💨 Steam (ตัน)", f"{summary['steam_ton'].sum():,.0f}")
c2.metric("💧 Condensate (ตัน)", f"{summary['condensate_ton'].sum():,.0f}")
c3.metric("📊 %Condensate", f"{avg_pct:.2f} %")
c4.metric("🚦 สถานะ", traffic_light(avg_pct))

# -----------------------------
# GRAPH
# -----------------------------
fig = px.scatter(
    summary,
    x=summary.columns[0],
    y="pct_condensate",
    color="status",
    color_discrete_map={
        "🟢": "green",
        "🟡": "orange",
        "🔴": "red"
    }
)

fig.add_hline(
    y=TARGET,
    line_dash="dash",
    annotation_text="Target 80%"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# TABLE
# -----------------------------
st.dataframe(summary, use_container_width=True)

