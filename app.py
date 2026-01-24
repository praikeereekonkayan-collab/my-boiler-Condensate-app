import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# =============================
# CONFIG
# =============================
st.set_page_config(
    page_title="Condensate Dashboard",
    layout="wide"
)

# =============================
# GOOGLE SHEET (CSV)
# =============================
CSV_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1G_ikK60FZUgctnM7SLZ4Ss0p6demBrlCwIre27fXsco"
    "/gviz/tq?tqx=out:csv&gid=2037224655"
)

# =============================
# LOAD DATA
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
        .str.replace("%", "pct")
    )

    # เปลี่ยนชื่อคอลัมน์ภาษาไทย → ใช้ในโค้ด
    df = df.rename(columns={
        "วันที่": "date",
        "target": "target_pct",
        "pct__condensate": "condensate_pct",
        "น้ำ_condensate_กลับ": "condensate_return",
        "รวมยอดใช้สตีม": "steam_total"
    })

    # ลบคอลัมน์ unnamed
    df = df.loc[:, ~df.columns.str.contains("unnamed")]

    # แปลงวันที่
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    return df.dropna(subset=["date"])


df = load_data()

# =============================
# SAFETY
# =============================
if df.empty:
    st.error("❌ ไม่พบข้อมูลใน Google Sheet")
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
# TITLE
# =============================
st.title("🏭 Condensate Monitoring Dashboard")
st.success("เชื่อม Google Sheet สำเร็จ ✅")

# =============================
# KPI
# =============================
c1, c2, c3 = st.columns(3)

c1.metric("Steam รวม", f"{df['steam_total'].sum():,.0f}", "ton")
c2.metric("Condensate เฉลี่ย", f"{df['condensate_pct'].mean():.2f}", "%")
c3.metric("Target", f"{df['target_pct'].iloc[-1]:.2f}", "%")

st.divider()

# =============================
# GRAPH (RED / GREEN)
# =============================
fig, ax = plt.subplots(figsize=(12, 5))

# เส้น actual
ax.plot(
    df["date"],
    df["condensate_pct"],
    marker="o",
    label="Actual Condensate",
)

# เส้น target
ax.plot(
    df["date"],
    df["target_pct"],
    linestyle="--",
    label="Target",
)

# จุดเตือนสีแดง
low = df["condensate_pct"] < df["target_pct"]
ax.scatter(
    df.loc[low, "date"],
    df.loc[low, "condensate_pct"],
    color="red",
    s=60,
    label="ต่ำกว่า Target"
)

ax.set_title("Condensate Return vs Target")
ax.set_ylabel("% Condensate")
ax.grid(True)
ax.legend()

st.pyplot(fig)

# =============================
# TABLE
# =============================
st.subheader("📋 ข้อมูลจริงจาก Google Sheet")
st.dataframe(df, use_container_width=True)
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# =============================
# CONFIG
# =============================
st.set_page_config(
    page_title="Boiler Condensate Dashboard",
    layout="wide"
)

# =============================
# GOOGLE SHEET
# =============================
CSV_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1G_ikK60FZUgctnM7SLZ4Ss0p6demBrlCwIre27fXsco"
    "/gviz/tq?tqx=out:csv&gid=2037224655"
)

# =============================
# LOAD DATA
# =============================
@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(CSV_URL)

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("%", "pct")
    )

    df = df.rename(columns={
        "วันที่": "date",
        "target": "target_pct",
        "pct__condensate": "condensate_pct",
        "รวมยอดใช้สตีม": "steam_total"
    })

    df = df.loc[:, ~df.columns.str.contains("unnamed")]

    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    df = df.dropna(subset=["date"])

    return df


df = load_data()

if df.empty:
    st.error("❌ ไม่พบข้อมูล")
    st.stop()

# =============================
# SIDEBAR FILTER
# =============================
st.sidebar.header("📅 เลือกช่วงเวลา")

start = st.sidebar.date_input("วันเริ่ม", df["date"].min())
end = st.sidebar.date_input("วันสิ้นสุด", df["date"].max())

df = df[
    (df["date"] >= pd.to_datetime(start)) &
    (df["date"] <= pd.to_datetime(end))
]

# =============================
# CALC STATUS
# =============================
df["ratio"] = df["condensate_pct"] / df["target_pct"]

def status(x):
    if x >= 1:
        return "ปกติ"
    elif x >= 0.9:
        return "เฝ้าระวัง"
    else:
        return "อันตราย"

df["status"] = df["ratio"].apply(status)

# =============================
# TITLE
# =============================
st.title("🏭 Boiler Condensate Return Dashboard")

# =============================
# KPI
# =============================
c1, c2, c3, c4 = st.columns(4)

c1.metric("Steam รวม", f"{df['steam_total'].sum():,.0f}")
c2.metric("Condensate เฉลี่ย", f"{df['condensate_pct'].mean():.2f}")
c3.metric("Target", f"{df['target_pct'].iloc[-1]:.2f}")
c4.metric("วันที่ต่ำกว่า Target", int((df["ratio"] < 1).sum()))

st.divider()

# =============================
# GRAPH
# =============================
fig, ax = plt.subplots(figsize=(14, 5))

ax.plot(df["date"], df["condensate_pct"], label="Actual", marker="o")
ax.plot(df["date"], df["target_pct"], label="Target", linestyle="--")

# สีเตือน
danger = df["ratio"] < 0.9
warning = (df["ratio"] >= 0.9) & (df["ratio"] < 1)

ax.scatter(df.loc[danger, "date"], df.loc[danger, "condensate_pct"],
           color="red", s=70, label="อันตราย")

ax.scatter(df.loc[warning, "date"], df.loc[warning, "condensate_pct"],
           color="orange", s=70, label="เฝ้าระวัง")

ax.set_ylabel("% Condensate")
ax.set_title("Condensate Return Monitoring")
ax.grid(True)
ax.legend()

st.pyplot(fig)

# =============================
# TABLE
# =============================
st.subheader("📋 ตารางสถานะรายวัน")
st.dataframe(
    df[["date", "condensate_pct", "target_pct", "status"]],
    use_container_width=True
)
