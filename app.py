import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Boiler Loss & Alert Dashboard",
    layout="wide"
)

st.title("🏭 BOILER LOSS • COST • ALERT DASHBOARD")

# ======================================================
# CONFIG
# ======================================================
COST_PER_TON = 350      # บาท/ตัน (แก้ได้)
TARGET = 80
WARNING = 70

# ======================================================
# LOAD DATA
# ======================================================
@st.cache_data
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1G_ikK60FZUgctnM7SLZ4Ss0p6demBrlCwIre27fXsco/export?format=csv&sheet=data_dashboard"
    return pd.read_csv(url)

df = load_data()

# ======================================================
# CLEAN DATA
# ======================================================
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.dropna(subset=["date"])

df["loss"] = df["steam_total"] - df["condensate_return"]
df["loss_cost"] = df["loss"] * COST_PER_TON

# ======================================================
# DATE FILTER
# ======================================================
st.sidebar.header("📅 เลือกช่วงวันที่")

start_date, end_date = st.sidebar.date_input(
    "เลือกช่วง",
    [df["date"].min(), df["date"].max()]
)

df = df[
    (df["date"] >= pd.to_datetime(start_date)) &
    (df["date"] <= pd.to_datetime(end_date))
]

# ======================================================
# VIEW MODE
# ======================================================
view = st.sidebar.radio(
    "📊 มุมมอง",
    ["รายวัน", "รายเดือน", "รายปี"]
)

# ======================================================
# GROUP
# ======================================================
if view == "รายวัน":
    df_g = df.groupby("date", as_index=False).sum(numeric_only=True)

elif view == "รายเดือน":
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df_g = df.groupby("month", as_index=False).sum(numeric_only=True)
    df_g.rename(columns={"month": "date"}, inplace=True)

else:
    df["year"] = df["date"].dt.year.astype(str)
    df_g = df.groupby("year", as_index=False).sum(numeric_only=True)
    df_g.rename(columns={"year": "date"}, inplace=True)

df_g["condensate_pct"] = (
    df_g["condensate_return"] / df_g["steam_total"] * 100
)

# ======================================================
# ALERT LOGIC
# ======================================================
df_g["status"] = df_g["condensate_pct"].apply(
    lambda x: "🟢 ปกติ" if x >= TARGET else
              "🟡 เฝ้าระวัง" if x >= WARNING else
              "🔴 แจ้งเตือน"
)

alert_rows = df_g[df_g["condensate_pct"] < WARNING]

# ======================================================
# KPI
# ======================================================
total_loss_cost = df_g["loss_cost"].sum()
avg_pct = df_g["condensate_pct"].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 เงินสูญเสียรวม", f"{total_loss_cost:,.0f} บาท")
col2.metric("🔥 Steam Loss รวม", f"{df_g['loss'].sum():,.0f} ตัน")
col3.metric("%Condensate เฉลี่ย", f"{avg_pct:.2f}%")
col4.metric("สถานะระบบ", 
            "🔴 ALERT" if not alert_rows.empty else "🟢 NORMAL")

st.divider()

# ======================================================
# GRAPH : LOSS TREND
# ======================================================
fig1 = px.line(
    df_g,
    x="date",
    y="loss_cost",
    markers=True,
    title="📉 แนวโน้มเงินสูญเสีย (Loss Trend)"
)

fig1.update_layout(
    yaxis_title="บาท",
    template="plotly_white"
)

st.plotly_chart(fig1, use_container_width=True)

# ======================================================
# GRAPH : CONDENSATE %
# ======================================================
fig2 = px.bar(
    df_g,
    x="date",
    y="condensate_pct",
    text_auto=".1f",
    title="% Condensate Return"
)

fig2.add_hline(y=TARGET, line_dash="dash", annotation_text="Target 80%")
fig2.add_hline(y=WARNING, line_dash="dot", annotation_text="Warning 70%")

fig2.update_layout(
    yaxis_range=[0, 100],
    template="plotly_white"
)

st.plotly_chart(fig2, use_container_width=True)

# ======================================================
# ALERT TABLE
# ======================================================
if not alert_rows.empty:
    st.error("🚨 พบช่วงเวลาที่ %Condensate ต่ำกว่า 70%")
    st.dataframe(alert_rows, use_container_width=True)
else:
    st.success("✅ ระบบอยู่ในเกณฑ์ปกติ")
# ================= COST CONFIG =================
COST_WATER = 35
COST_CHEM = 45
COST_FUEL = 270

# ================= LOSS CALC =================
df["loss"] = df["steam_total"] - df["condensate_return"]

df["loss_water"] = df["loss"] * COST_WATER
df["loss_chem"] = df["loss"] * COST_CHEM
df["loss_fuel"] = df["loss"] * COST_FUEL

df["loss_total"] = (
    df["loss_water"] +
    df["loss_chem"] +
    df["loss_fuel"]
)

# ================= LINE ALERT =================
import requests

def send_line(msg):
    token = st.secrets["LINE_TOKEN"]
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"message": msg}
    requests.post(url, headers=headers, data=data)

# ตรวจ ALERT
alert = df[df["condensate_pct"] < 70]

if not alert.empty:
    last = alert.iloc[-1]
    msg = f"""
🚨 BOILER ALERT

📅 วันที่: {last['date'].date()}
%Condensate: {last['condensate_pct']:.2f}%

💧 น้ำสูญเสีย: {last['loss_water']:,.0f} บาท
🧪 เคมีสูญเสีย: {last['loss_chem']:,.0f} บาท
🔥 เชื้อเพลิงสูญเสีย: {last['loss_fuel']:,.0f} บาท

รวมสูญเสีย: {last['loss_total']:,.0f} บาท
"""
    send_line(msg)
