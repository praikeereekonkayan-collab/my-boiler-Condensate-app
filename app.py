import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Steam & Condensate Dashboard",
    layout="wide"
)

# =============================
# GOOGLE SHEET CSV
# =============================
CSV_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1G_ikK60FZUgctnM7SLZ4Ss0p6demBrlCwIre27fXsco"
    "/gviz/tq?tqx=out:csv"
)

# =============================
# LOAD DATA
# =============================
@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(CSV_URL)

    # ลบคอลัมน์ขยะ
    df = df.loc[:, ~df.columns.str.contains("unnamed", case=False)]

    # clean column name
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # 🔥 หา column วันที่อัตโนมัติ
    date_col = None
    for c in df.columns:
        if "date" in c or "วัน" in c:
            date_col = c
            break

    if date_col:
        df["date"] = pd.to_datetime(df[date_col], errors="coerce")
    else:
        st.error("❌ ไม่พบคอลัมน์วันที่ (date)")
        st.stop()

    return df

# =============================
# SIDEBAR FILTER
# =============================
st.sidebar.header("📅 เลือกช่วงเวลา")

start = st.sidebar.date_input(
    "วันเริ่ม",
    df["date"].min()
)

end = st.sidebar.date_input(
    "วันสิ้นสุด",
    df["date"].max()
)

df = df[(df["date"] >= pd.to_datetime(start)) &
        (df["date"] <= pd.to_datetime(end))]

# =============================
# KPI COLOR LOGIC
# =============================
def status_color(actual, target):
    if actual >= target:
        return "🟢 ปกติ"
    elif actual >= target * 0.7:
        return "🟡 เฝ้าระวัง"
    else:
        return "🔴 ต่ำกว่าเป้า"

# =============================
# HEADER
# =============================
st.title("🏭 Steam & Condensate Dashboard")
st.caption("ข้อมูลจาก Google Sheet (Live)")

# =============================
# KPI
# =============================
col1, col2, col3 = st.columns(3)

avg_cond = df["condensate_pct"].mean()
target = df["target_pct"].mean()

col1.metric(
    "Condensate เฉลี่ย",
    f"{avg_cond*100:.1f} %",
    status_color(avg_cond, target)
)

col2.metric(
    "Steam รวม",
    f"{df['steam_total'].sum():,.1f}",
    "ton"
)

col3.metric(
    "Soft Mark Up",
    f"{df['soft_mark_up'].sum():,.0f}",
    "ครั้ง"
)

st.divider()

# =============================
# GRAPH 1 : STEAM
# =============================
st.subheader("📊 Steam Usage (ton/day)")
fig, ax = plt.subplots(figsize=(12,4))
ax.plot(df["date"], df["steam_total"], marker="o")
ax.set_ylabel("Ton/day")
ax.grid(True)
st.pyplot(fig)

# =============================
# GRAPH 2 : CONDENSATE
# =============================
st.subheader("📈 Condensate Return (ton/day)")
fig, ax = plt.subplots(figsize=(12,4))
ax.plot(df["date"], df["condensate_return"], marker="o")
ax.grid(True)
st.pyplot(fig)

# =============================
# GRAPH 3 : KPI %
# =============================
st.subheader("🎯 Condensate % vs Target")

fig, ax = plt.subplots(figsize=(12,4))
ax.plot(df["date"], df["condensate_pct"]*100, label="Actual %", marker="o")
ax.plot(df["date"], df["target_pct"]*100, linestyle="--", label="Target %")

ax.set_ylabel("%")
ax.legend()
ax.grid(True)

st.pyplot(fig)

# =============================
# TABLE
# =============================
st.subheader("📋 ตารางข้อมูล")
st.dataframe(df, use_container_width=True)
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Condensate Dashboard", layout="wide")

# -------------------------
# LOAD DATA
# -------------------------
df = pd.read_csv("steam_data.csv")

df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date")

# คำนวณ %
df["condensate_pct"] = df["condensate_return"] / df["steam_total"]

# -------------------------
# PHASE CLASS
# -------------------------
def phase(p):
    if p >= 0.9:
        return "PHASE 1"
    elif p >= 0.8:
        return "PHASE 2"
    elif p >= 0.6:
        return "PHASE 3"
    else:
        return "PHASE 4"

df["phase"] = df["condensate_pct"].apply(phase)

# -------------------------
# KPI
# -------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Condensate Avg", f"{df['condensate_pct'].mean()*100:.1f}%")
col2.metric("Target", "80%")
col3.metric("ผ่านเป้า", f"{(df['condensate_pct']>=0.8).sum()} วัน")
col4.metric("PHASE 4 🔴", f"{(df['phase']=='PHASE 4').sum()} วัน")

st.divider()

# -------------------------
# GRAPH 1 : Condensate %
# -------------------------
fig1 = px.scatter(
    df,
    x="date",
    y="condensate_pct",
    color="phase",
    title="Condensate Return % (Alarm Monitoring)",
)

fig1.add_hline(
    y=0.8,
    line_dash="dash",
    annotation_text="Target 80%"
)

fig1.update_yaxes(tickformat=".0%")

st.plotly_chart(fig1, use_container_width=True)

# -------------------------
# GRAPH 2 : Steam vs Condensate
# -------------------------
fig2 = px.bar(
    df,
    x="date",
    y=["steam_total", "condensate_return"],
    barmode="group",
    title="Steam vs Condensate Return"
)

st.plotly_chart(fig2, use_container_width=True)

