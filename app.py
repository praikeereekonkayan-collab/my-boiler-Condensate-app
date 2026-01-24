import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Factory Steam Dashboard",
    layout="wide"
)

# =============================
# GOOGLE SHEET
# =============================
CSV_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1G_ikK60FZUgctnM7SLZ4Ss0p6demBrlCwIre27fXsco"
    "/gviz/tq?tqx=out:csv&sheet=data_dashboard"
)

# =============================
# LOAD DATA
# =============================
@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.lower().str.strip()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    return df

df = load_data()

st.write("คอลัมน์ที่อ่านได้จาก Google Sheet 👇")
st.write(df.columns.tolist())
st.stop()

# =============================
# SIDEBAR
# =============================
st.sidebar.header("📅 เลือกช่วงเวลา")

start = st.sidebar.date_input("วันเริ่ม", df["date"].min())
end = st.sidebar.date_input("วันสิ้นสุด", df["date"].max())

df = df[
    (df["date"] >= pd.to_datetime(start)) &
    (df["date"] <= pd.to_datetime(end))
]

# =============================
# MONTHLY SUMMARY
# =============================
df["month"] = df["date"].dt.to_period("M")

monthly = df.groupby("month").agg({
    "steam_total": "sum",
    "condensate_return": "mean",
    "target_pct": "mean"
}).reset_index()

monthly["month"] = monthly["month"].astype(str)

# =============================
# DASHBOARD
# =============================
st.title("🏭 Factory Steam Dashboard")
st.success("เชื่อม Google Sheet สำเร็จ ✅")

# KPI
col1, col2, col3 = st.columns(3)

col1.metric("🔥 Steam รวม", f"{df['steam_total'].sum():,.0f}", "ton")
col2.metric("💧 Condensate เฉลี่ย", f"{df['condensate_return'].mean():.1f}", "%")
col3.metric("🎯 Target", f"{df['target_pct'].mean()*100:.0f}", "%")

st.divider()

# =============================
# GRAPH DAILY
# =============================
fig1, ax1 = plt.subplots(figsize=(12, 4))
ax1.plot(df["date"], df["steam_total"], marker="o")
ax1.set_title("Steam Usage (Daily)")
ax1.set_ylabel("Ton/day")
ax1.grid(True)
st.pyplot(fig1)

fig2, ax2 = plt.subplots(figsize=(12, 4))
ax2.plot(df["date"], df["condensate_return"], marker="o")
ax2.axhline(df["target_pct"].mean()*100, linestyle="--")
ax2.set_title("Condensate Return (Daily)")
ax2.set_ylabel("%")
ax2.grid(True)
st.pyplot(fig2)

st.divider()

# =============================
# MONTHLY TREND
# =============================
st.subheader("📈 แนวโน้มรายเดือน")

fig3, ax3 = plt.subplots(figsize=(12, 4))
ax3.plot(monthly["month"], monthly["steam_total"], marker="o")
ax3.set_title("Steam Monthly Trend")
ax3.set_ylabel("Ton")
ax3.grid(True)
st.pyplot(fig3)

st.dataframe(monthly, use_container_width=True)
import plotly.graph_objects as go

target = df["target_pct"].iloc[0]

def status_color(val):
    if val >= target:
        return "green"
    elif val >= target - 5:
        return "orange"
    else:
        return "red"

colors = df["condensate_pct"].apply(status_color)

fig = go.Figure()

# Actual line
fig.add_trace(go.Scatter(
    x=df["date"],
    y=df["condensate_pct"],
    mode="lines+markers",
    name="Actual %",
    marker=dict(color=colors, size=8),
    line=dict(width=3)
))

# Target line
fig.add_trace(go.Scatter(
    x=df["date"],
    y=df["target_pct"],
    mode="lines",
    name="Target %",
    line=dict(dash="dash", color="blue", width=2)
))

fig.update_layout(
    title="Condensate Return Efficiency (%)",
    xaxis_title="Date",
    yaxis_title="Percent (%)",
    template="plotly_white",
    height=450
)

st.plotly_chart(fig, use_container_width=True)
fig2 = go.Figure()

fig2.add_trace(go.Bar(
    x=df["date"],
    y=df["steam_total"],
    name="Steam Total",
))

fig2.add_trace(go.Bar(
    x=df["date"],
    y=df["condensate_return"],
    name="Condensate Return",
))

fig2.update_layout(
    barmode="group",
    title="Steam vs Condensate Return",
    height=450
)

st.plotly_chart(fig2, use_container_width=True)
avg_pct = df["condensate_pct"].mean()

fig3 = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=avg_pct,
    delta={"reference": target},
    gauge={
        "axis": {"range": [0, 100]},
        "steps": [
            {"range": [0, target-5], "color": "red"},
            {"range": [target-5, target], "color": "yellow"},
            {"range": [target, 100], "color": "green"},
        ],
        "threshold": {
            "line": {"color": "blue", "width": 4},
            "value": target
        }
    },
    title={"text": "Average Condensate Return (%)"}
))

st.plotly_chart(fig3, use_container_width=True)
import streamlit as st

avg_pct = df["condensate_pct"].mean()
total_steam = df["steam_total"].sum()
total_cond = df["condensate_return"].sum()
target = df["target_pct"].iloc[0]

col1, col2, col3, col4 = st.columns(4)

col1.metric("🔥 Steam Total", f"{total_steam:,.1f} ton")
col2.metric("💧 Condensate Return", f"{total_cond:,.1f} ton")
col3.metric("📊 Avg Return %", f"{avg_pct:.1f}%")

if avg_pct >= target:
    col4.success("🟢 STATUS : NORMAL")
elif avg_pct >= target - 5:
    col4.warning("🟡 STATUS : WATCH")
else:
    col4.error("🔴 STATUS : ALARM")
import plotly.express as px

fig = px.density_heatmap(
    df,
    x=df["date"].dt.day,
    y=df["date"].dt.month,
    z="condensate_pct",
    color_continuous_scale="RdYlGn",
    title="Condensate Return Heatmap"
)

st.plotly_chart(fig, use_container_width=True)
df["loss"] = df["steam_total"] - df["condensate_return"]

top_loss = df.sort_values("loss", ascending=False).head(10)

st.subheader("🔻 TOP 10 Steam Loss Days")
st.dataframe(top_loss[[
    "date",
    "steam_total",
    "condensate_return",
    "loss",
    "condensate_pct"
]])
monthly = df.resample("M", on="date").mean(numeric_only=True)

fig = px.line(
    monthly,
    y="condensate_pct",
    markers=True,
    title="Monthly Condensate Efficiency Trend"
)

st.plotly_chart(fig, use_container_width=True)
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)
