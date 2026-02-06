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
# -----------------------------
# CONFIG
# -----------------------------
TARGET = 80          # % target
YELLOW_LIMIT = 70    # % ต่ำกว่า target เริ่มเหลือง
COST_PER_TON = 664

TARGET = 80
COST_PER_TON = 664   # <<< ใส่ตรงนี้
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
st.sidebar.header("📅 เลือกช่วงวันที่")

min_date = df["date"].min()
max_date = df["date"].max()







daily = (
    df.groupby(df["date"].dt.date)
    .agg(
        steam=("steam_ton", "sum"),
        condensate=("condensate_ton", "sum")
    )
    .reset_index()
)

daily["pct_cond"] = (daily["condensate"] / daily["steam"]) * 100
daily["loss_pct"] = (TARGET - daily["pct_cond"]).clip(lower=0)
daily["steam_loss"] = (daily["loss_pct"] / 100) * daily["steam"]
daily["cost_loss"] = daily["steam_loss"] * COST_PER_TON
def loss_color(loss_pct):
    if loss_pct == 0:
        return "green"
    elif loss_pct <= YELLOW_LIMIT:
        return "orange"
    else:
        return "red"

daily["color"] = daily["loss_pct"].apply(loss_color)
daily["target_cost"] = 0
import plotly.express as px

fig_daily = px.bar(
    daily,
    x="date",
    y="cost_loss",
    color="color",
    color_discrete_map={
        "green": "#2ecc71",
        "orange": "#f1c40f",
        "red": "#e74c3c"
    },
    title="📈 Cost Loss รายวัน"
)

fig_daily.add_scatter(
    x=daily["date"],
    y=daily["target_cost"],
    mode="lines",
    name="Target Cost",
    line=dict(color="red", dash="dash")
)

st.plotly_chart(fig_daily, use_container_width=True)
daily["year"] = pd.to_datetime(daily["date"]).dt.year

year = st.selectbox(
    "📆 เลือกปี",
    sorted(daily["year"].unique(), reverse=True)
)

ytd = daily[daily["year"] == year].copy()
ytd["ytd_cost"] = ytd["cost_loss"].cumsum()
fig_ytd = px.line(
    ytd,
    x="date",
    y="ytd_cost",
    markers=True,
    title=f"📉 YTD Cost Loss ปี {year}"
)

st.plotly_chart(fig_ytd, use_container_width=True)

