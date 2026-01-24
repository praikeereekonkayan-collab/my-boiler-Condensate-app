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
