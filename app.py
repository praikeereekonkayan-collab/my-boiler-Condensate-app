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
# =============================
# PHASE 5 : MONTHLY SUMMARY
# =============================

st.divider()
st.header("📊 สรุปรายเดือน (Manager View)")

df["month"] = df["date"].dt.to_period("M").astype(str)

monthly = (
    df.groupby("month")
    .agg(
        steam_total=("steam_total", "sum"),
        avg_condensate=("condensate_pct", "mean"),
        target=("target_pct", "mean"),
        low_day=("ratio", lambda x: (x < 1).sum())
    )
    .reset_index()
)

monthly["efficiency_pct"] = (
    monthly["avg_condensate"] / monthly["target"]
) * 100


def grade(x):
    if x >= 95:
        return "A 🟢"
    elif x >= 90:
        return "B 🟡"
    elif x >= 80:
        return "C 🟠"
    else:
        return "D 🔴"


monthly["grade"] = monthly["efficiency_pct"].apply(grade)

# ===== KPI MONTH =====
c1, c2, c3 = st.columns(3)

c1.metric("เดือนทั้งหมด", len(monthly))
c2.metric("Efficiency เฉลี่ย", f"{monthly['efficiency_pct'].mean():.1f} %")
c3.metric("เดือนต่ำกว่า Target", int((monthly["efficiency_pct"] < 100).sum()))

# ===== GRAPH =====
fig2, ax2 = plt.subplots(figsize=(14, 5))

ax2.plot(monthly["month"], monthly["efficiency_pct"], marker="o")
ax2.axhline(100, linestyle="--")

ax2.set_ylabel("Efficiency %")
ax2.set_title("Monthly Condensate Efficiency")
ax2.grid(True)

st.pyplot(fig2)

# ===== TABLE =====
st.subheader("📋 ตารางสรุปรายเดือน")
st.dataframe(monthly, use_container_width=True)
# =============================
# PHASE 6 : TIME VIEW SELECT
# =============================

st.divider()
st.header("📅 เลือกรูปแบบการดูข้อมูล")

view_mode = st.selectbox(
    "เลือกมุมมองข้อมูล",
    ["รายวัน", "รายเดือน", "รายปี"]
)

df_view = df.copy()

if view_mode == "รายเดือน":
    df_view["period"] = df_view["date"].dt.to_period("M").astype(str)
    df_view = (
        df_view.groupby("period")
        .agg(
            steam_total=("steam_total", "sum"),
            condensate_pct=("condensate_pct", "mean"),
            target_pct=("target_pct", "mean")
        )
        .reset_index()
    )
    df_view.rename(columns={"period": "date"}, inplace=True)

elif view_mode == "รายปี":
    df_view["period"] = df_view["date"].dt.year
    df_view = (
        df_view.groupby("period")
        .agg(
            steam_total=("steam_total", "sum"),
            condensate_pct=("condensate_pct", "mean"),
            target_pct=("target_pct", "mean")
        )
        .reset_index()
    )
    df_view.rename(columns={"period": "date"}, inplace=True)

st.success(f"📊 แสดงข้อมูลแบบ: {view_mode}")
# =============================
# PHASE 7 : STEAM LOSS
# =============================

st.divider()
st.header("🔥 Steam Loss Analysis")

df_view["loss_pct"] = (
    df_view["target_pct"] - df_view["condensate_pct"]
).clip(lower=0)

df_view["steam_loss_ton"] = (
    df_view["steam_total"] * df_view["loss_pct"]
)

c1, c2, c3 = st.columns(3)

c1.metric("Steam Loss รวม", f"{df_view['steam_loss_ton'].sum():,.1f} ton")
c2.metric("Loss เฉลี่ย", f"{df_view['loss_pct'].mean()*100:.1f} %")
c3.metric("วันที่เสียหาย", int((df_view["loss_pct"] > 0).sum()))
# =============================
# PHASE 8 : COST LOSS
# =============================

st.divider()
st.header("💰 มูลค่าความสูญเสีย (Cost Loss)")

steam_cost = st.number_input(
    "ต้นทุน Steam (บาท / ton)",
    value=700,
    step=100
)

df_view["loss_baht"] = df_view["steam_loss_ton"] * steam_cost

c1, c2, c3 = st.columns(3)

c1.metric("สูญเสียทั้งหมด", f"{df_view['loss_baht'].sum():,.0f} บาท")
c2.metric("เฉลี่ยต่อช่วง", f"{df_view['loss_baht'].mean():,.0f} บาท")
c3.metric("สูงสุด", f"{df_view['loss_baht'].max():,.0f} บาท")

