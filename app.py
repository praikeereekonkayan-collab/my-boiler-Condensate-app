import streamlit as st
import pandas as pd
import plotly.express as px

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="Boiler Condensate Loss",
    page_icon="🔥",
    layout="wide"
)

st.title("🔥 Boiler Condensate Loss Dashboard")
st.caption("ระบบติดตาม Cost Loss จาก Condensate Return")

# =============================
# LOAD DATA
# =============================
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    return df

data = load_data()

# =============================
# SIDEBAR FILTER
# =============================
st.sidebar.header("🔎 ตัวกรองข้อมูล")

view_type = st.sidebar.selectbox(
    "รูปแบบการแสดงผล",
    ["รายวัน", "รายเดือน", "รายปี"]
)

boiler_select = st.sidebar.multiselect(
    "เลือก Boiler",
    options=data["boiler"].unique(),
    default=data["boiler"].unique()
)

data = data[data["boiler"].isin(boiler_select)]

start_date, end_date = st.sidebar.date_input(
    "ช่วงวันที่",
    [data["date"].min(), data["date"].max()]
)

mask = (data["date"] >= pd.to_datetime(start_date)) & (data["date"] <= pd.to_datetime(end_date))
data = data.loc[mask]

# =============================
# AGGREGATE
# =============================
if view_type == "รายวัน":
    data["period"] = data["date"]

elif view_type == "รายเดือน":
    data["period"] = data["date"].dt.to_period("M").dt.to_timestamp()

else:
    data["period"] = data["date"].dt.year

group_data = (
    data.groupby(["period", "boiler"], as_index=False)
    .agg({"cost_loss": "sum"})
)

# =============================
# KPI SECTION
# =============================
total_loss = group_data["cost_loss"].sum()
avg_loss = group_data.groupby("period")["cost_loss"].sum().mean()
top_boiler = (
    group_data.groupby("boiler")["cost_loss"]
    .sum()
    .idxmax()
)

col1, col2, col3 = st.columns(3)

col1.metric("💸 Cost Loss รวม", f"{total_loss:,.0f} บาท")
col2.metric("📊 ค่าเฉลี่ยต่อช่วง", f"{avg_loss:,.0f} บาท")
col3.metric("🔥 Boiler Loss สูงสุด", top_boiler)

st.divider()

# =============================
# TREND LINE
# =============================
fig_trend = px.line(
    group_data,
    x="period",
    y="cost_loss",
    color="boiler",
    markers=True,
    title="📈 แนวโน้ม Cost Loss แยกตาม Boiler",
    template="plotly_white"
)

fig_trend.update_layout(
    xaxis_title="เวลา",
    yaxis_title="Cost Loss (บาท)",
    font=dict(size=14),
    title_font_size=20
)

st.plotly_chart(fig_trend, use_container_width=True)

# =============================
# BAR COMPARISON
# =============================
bar_data = (
    group_data.groupby("boiler", as_index=False)["cost_loss"]
    .sum()
)

fig_bar = px.bar(
    bar_data,
    x="boiler",
    y="cost_loss",
    title="📊 เปรียบเทียบ Cost Loss ตาม Boiler",
    text_auto=".2s",
    template="plotly_white"
)

fig_bar.update_layout(
    xaxis_title="Boiler",
    yaxis_title="Cost Loss (บาท)",
    font=dict(size=14),
    title_font_size=20
)

st.plotly_chart(fig_bar, use_container_width=True)

# =============================
# DATA TABLE
# =============================
with st.expander("📄 ตารางข้อมูลสรุป"):
    st.dataframe(group_data, use_container_width=True)

