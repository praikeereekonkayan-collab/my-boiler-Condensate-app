import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# =============================
# CONFIG
# =============================
st.set_page_config(
    page_title="Factory Dashboard",
    layout="wide"
)

# =============================
# GOOGLE SHEET
# =============================
SHEET_ID = CSV_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1G_ikK60FZUgctnM7SLZ4Ss0p6demBrlCwIre27fXsco"
    "/gviz/tq?tqx=out:csv"
)


CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

# =============================
# LOAD DATA
# =============================
@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip()

    # แปลงวันที่ (ถ้ามี)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    return df

df = load_data()

# =============================
# FUNCTION
# =============================
def plot_chart(df, y, title, unit=""):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df["date"], df[y], marker="o")
    ax.set_title(title)
    ax.set_ylabel(unit)
    ax.grid(True)
    st.pyplot(fig)

def kpi(title, value, unit=""):
    st.metric(title, f"{value:,.2f} {unit}")

# =============================
# SIDEBAR
# =============================
st.sidebar.header("📅 เลือกช่วงเวลา")

if "date" in df.columns:
    start = st.sidebar.date_input("วันเริ่ม", df["date"].min())
    end = st.sidebar.date_input("วันสิ้นสุด", df["date"].max())

    df = df[(df["date"] >= pd.to_datetime(start)) &
            (df["date"] <= pd.to_datetime(end))]

# =============================
# DASHBOARD
# =============================
st.title("🏭 Factory Dashboard (Google Sheet Live)")

st.success("เชื่อม Google Sheet สำเร็จ ✅")

# ===== KPI =====
col1, col2, col3 = st.columns(3)

if "steam" in df.columns:
    col1.metric("Steam รวม", f"{df['steam'].sum():,.0f}", "ton")

if "water" in df.columns:
    col2.metric("Water รวม", f"{df['water'].sum():,.0f}", "m³")

if "condensate" in df.columns:
    col3.metric("Condensate เฉลี่ย", f"{df['condensate'].mean():.1f}", "%")

st.divider()

# ===== GRAPH =====
if "steam" in df.columns:
    plot_chart(df, "steam", "Steam Usage", "ton/day")

if "water" in df.columns:
    plot_chart(df, "water", "Water Usage", "m³/day")

if "condensate" in df.columns:
    plot_chart(df, "condensate", "Condensate Return", "%")

st.divider()

# ===== TABLE =====
st.subheader("📋 ข้อมูลจาก Google Sheet")
st.dataframe(df, use_container_width=True)
