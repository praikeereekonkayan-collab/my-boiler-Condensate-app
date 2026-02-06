import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.express as px

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
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", scope
)
client = gspread.authorize(creds)

SHEET_ID = "1G_ikK60FZUgctnM7SLZ4Ss0p6demBrlCwIre27fXsco"
sheet = client.open_by_key(SHEET_ID).worksheet("CONDENSATE")

data = sheet.get_all_records()
df = pd.DataFrame(data)

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

