import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Boiler Steam Dashboard",
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
# LOAD DATA (FINAL)
# =============================
@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(CSV_URL)

    # ทำความสะอาดชื่อคอลัมน์
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # 🔥 MAP ชื่อคอลัมน์ภาษาไทย → อังกฤษ
    df = df.rename(columns={
        "วันที่": "date",
        "รวมยอดใช้สตีม": "steam_total",
        "น้ำ_condensate_กลับ": "condensate_return",
        "target": "target_pct",
        "%__condensate": "condensate_pct"
    })

    # ลบคอลัมน์ unnamed
    df = df.loc[:, ~df.columns.str.contains("unnamed")]

    # แปลงวันที่
    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")

    return df



df = load_data()

if df.empty:
    st.error("❌ ไม่มีข้อมูลให้แสดง")
    st.stop()

# =============================
# SIDEBAR FILTER
# =============================
st.sidebar.header("📅 เลือกช่วงเวลา")

start = st.sidebar.date_input(
    "วันเริ่ม",
    value=df["date"].min()
)

end = st.sidebar.date_input(
    "วันสิ้นสุด",
    value=df["date"].max()
)

df = df[
    (df["date"] >= pd.to_datetime(start)) &
    (df["date"] <= pd.to_datetime(end))
]

# =============================
# DASHBOARD
# =============================
st.title("🏭 Steam & Condensate Dashboard")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Steam รวม (ton)",
    f"{df['steam_total'].sum():,.1f}"
)

col2.metric(
    "Condensate Return (ton)",
    f"{df['condensate_return'].sum():,.1f}"
)

col3.metric(
    "Condensate % เฉลี่ย",
    f"{df['condensate_pct'].mean()*100:.1f}%"
)

st.divider()

# =============================
# GRAPH
# =============================
fig, ax = plt.subplots(figsize=(12, 4))

ax.plot(df["date"], df["condensate_pct"] * 100, marker="o", label="Actual %")
ax.plot(df["date"], df["target_pct"] * 100, linestyle="--", label="Target %")

ax.set_ylabel("%")
ax.set_title("Condensate Return vs Target")
ax.grid(True)
ax.legend()

st.pyplot(fig)

# =============================
# TABLE
# =============================
st.subheader("📋 ข้อมูลรายวัน")
st.dataframe(df, use_container_width=True)
