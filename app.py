import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Condensate Boiler Dashboard",
    layout="wide"
)

st.title("🏭 Condensate Boiler Dashboard")

# =========================
# โหลดข้อมูล
# =========================
file = "%CONDENSATE BOILER.xlsx"
df = pd.read_excel(file)

# เลือกเฉพาะข้อมูลที่จำเป็น
df = df.iloc[2:].copy()

df.columns = [
    "Date",
    "Soft Mark Up",
    "Boiler Water",
    "Condensate Return",
    "Date2",
    "Target",
    "%Condensate",
    "Date3",
    "Cond_BHS",
    "Cond_BHS_%",
    "Date4",
    "Steam_Total",
    "Date5",
    "AVG_DIFF",
    "x1",
    "DIFF",
    "x2"
]

df["Date"] = pd.to_datetime(df["Date"])
df["%Condensate"] = pd.to_numeric(df["%Condensate"], errors="coerce")
df["Steam_Total"] = pd.to_numeric(df["Steam_Total"], errors="coerce")

# =========================
# KPI
# =========================
col1, col2, col3 = st.columns(3)

col1.metric(
    "♻️ % Condensate เฉลี่ย",
    f"{df['%Condensate'].mean():.2%}"
)

col2.metric(
    "🔥 Steam ใช้รวม",
    f"{df['Steam_Total'].sum():,.0f} ton"
)

col3.metric(
    "🎯 Target",
    "80 %"
)

st.divider()

# =========================
# กราฟ % Condensate
# =========================
fig1 = px.line(
    df,
    x="Date",
    y="%Condensate",
    markers=True,
    title="% Condensate Return",
)

fig1.add_hline(
    y=0.8,
    line_dash="dash",
    annotation_text="Target 80%"
)

st.plotly_chart(fig1, use_container_width=True)

# =========================
# กราฟ Steam
# =========================
fig2 = px.bar(
    df,
    x="Date",
    y="Steam_Total",
    title="Steam Usage (ton/day)"
)

st.plotly_chart(fig2, use_container_width=True)

# =========================
# ตาราง
# =========================
st.subheader("📋 ตารางสรุป")
st.dataframe(
    df[["Date", "%Condensate", "Steam_Total"]],
    use_container_width=True
)
