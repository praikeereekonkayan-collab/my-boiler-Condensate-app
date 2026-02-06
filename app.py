import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(
    page_title="Condensate Boiler Dashboard",
    layout="wide"
)

TARGET = 80
WARNING_GAP = 5

# -----------------------------
# LOAD GOOGLE SHEET (CSV)
# -----------------------------
SHEET_ID = "1G_ikK60FZUgctnM7SLZ4Ss0p6demBrlCwIre27fXsco"
SHEET_NAME = "CONDENSATE"

csv_url = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/"
    f"gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"
)

df = pd.read_csv(csv_url)

# -----------------------------
# CLEAN DATA
# -----------------------------
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.dropna(subset=["date"])

df["pct_condensate"] = (
    df["condensate_ton"] / df["steam_ton"] * 100
).where(df["steam_ton"] > 0)

df["pct_condensate"] = df["pct_condensate"].round(2)

def traffic_light(value):
    if pd.isna(value):
        return "⚪"
    elif value >= TARGET:
        return "🟢"
    elif value >= TARGET - WARNING_GAP:
        return "🟡"
    else:
        return "🔴"

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.header("🔎 ตัวกรอง")

view_mode = st.sidebar.radio(
    "รูปแบบการดู",
    ["รายวัน", "รายเดือน", "รายปี"]
)

year = st.sidebar.selectbox(
    "เลือกปี",
    sorted(df["date"].dt.year.unique())
)

filtered = df[df["date"].dt.year == year]

# -----------------------------
# SUMMARY
# -----------------------------
if view_mode == "รายวัน":
    summary = filtered.groupby(filtered["date"].dt.date).agg(
        steam_ton=("steam_ton", "sum"),
        condensate_ton=("condensate_ton", "sum"),
        pct_condensate=("pct_condensate", "mean")
    ).reset_index()

elif view_mode == "รายเดือน":
    summary = filtered.groupby(filtered["date"].dt.to_period("M")).agg(
        steam_ton=("steam_ton", "sum"),
        condensate_ton=("condensate_ton", "sum"),
        pct_condensate=("pct_condensate", "mean")
    ).reset_index()
    summary["date"] = summary["date"].astype(str)

else:
    summary = df.groupby(df["date"].dt.year).agg(
        steam_ton=("steam_ton", "sum"),
        condensate_ton=("condensate_ton", "sum"),
        pct_condensate=("pct_condensate", "mean")
    ).reset_index()
    summary.rename(columns={"date": "year"}, inplace=True)

summary["status"] = summary["pct_condensate"].apply(traffic_light)

# -----------------------------
# KPI
# -----------------------------
st.title("🏭 Condensate Boiler Dashboard")

avg_pct = summary["pct_condensate"].mean()

c1, c2, c3, c4 = st.columns(4)
c1.metric("💨 Steam (ตัน)", f"{summary['steam_ton'].sum():,.0f}")
c2.metric("💧 Condensate (ตัน)", f"{summary['condensate_ton'].sum():,.0f}")
c3.metric("📊 %Condensate", f"{avg_pct:.2f} %")
c4.metric("🚦 สถานะ", traffic_light(avg_pct))

# -----------------------------
# GRAPH
# -----------------------------
fig = px.scatter(
    summary,
    x=summary.columns[0],
    y="pct_condensate",
    color="status",
    color_discrete_map={
        "🟢": "green",
        "🟡": "orange",
        "🔴": "red"
    }
)

fig.add_hline(
    y=TARGET,
    line_dash="dash",
    annotation_text="Target 80%"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# TABLE
# -----------------------------
st.dataframe(summary, use_container_width=True)
st.sidebar.header("📅 เลือกช่วงวันที่")

min_date = df["date"].min()
max_date = df["date"].max()

date_range = st.sidebar.date_input(
    "เลือกช่วงวันที่ที่ต้องการดู",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])

filtered = df[
    (df["date"] >= start_date) &
    (df["date"] <= end_date)
]
daily = (
    filtered
    .groupby(filtered["date"].dt.date)
    .agg(
        pct_condensate=("pct_condensate", "mean")
    )
    .reset_index()
)
import plotly.express as px

fig = px.line(
    daily,
    x="date",
    y="pct_condensate",
    markers=True,
    title="📈 % Condensate ตามช่วงวันที่ที่เลือก"
)

# เส้น Target
fig.add_hline(
    y=80,
    line_dash="dash",
    line_color="red",
    annotation_text="Target 80%"
)

fig.update_layout(
    xaxis_title="วันที่",
    yaxis_title="% Condensate",
    hovermode="x unified",
    height=450
)

st.plotly_chart(fig, use_container_width=True)
daily["status"] = daily["pct_condensate"].apply(traffic_light)

fig = px.line(
    daily,
    x="date",
    y="pct_condensate",
    color="status",
    markers=True,
    color_discrete_map={
        "🟢": "green",
        "🟡": "orange",
        "🔴": "red"
    }
)
st.sidebar.subheader("⏱️ เลือกช่วงเวลาแบบเร็ว")

today = df["date"].max()

col_a, col_b, col_c = st.sidebar.columns(3)

if col_a.button("7 วัน"):
    start_date = today - pd.Timedelta(days=7)
    end_date = today

elif col_b.button("30 วัน"):
    start_date = today - pd.Timedelta(days=30)
    end_date = today

elif col_c.button("YTD"):
    start_date = pd.to_datetime(f"{today.year}-01-01")
    end_date = today

else:
    # fallback ใช้ date_input เดิม
    date_range = st.sidebar.date_input(
        "📅 เลือกช่วงวันที่",
        value=(df["date"].min(), df["date"].max()),
        min_value=df["date"].min(),
        max_value=df["date"].max()
    )
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
filtered = df[
    (df["date"] >= start_date) &
    (df["date"] <= end_date)
]
st.sidebar.subheader("📊 รูปแบบการแสดงผล")
view_mode = st.sidebar.radio(
    "เลือกมุมมอง",
    ["รายวัน", "รายเดือน"]
)
if view_mode == "รายวัน":
    summary = (
        filtered
        .groupby(filtered["date"].dt.date)
        .agg(pct_condensate=("pct_condensate", "mean"))
        .reset_index()
    )
    x_col = "date"

else:  # รายเดือน
    summary = (
        filtered
        .groupby(filtered["date"].dt.to_period("M"))
        .agg(pct_condensate=("pct_condensate", "mean"))
        .reset_index()
    )
    summary["date"] = summary["date"].dt.to_timestamp()
    x_col = "date"
import plotly.express as px

fig = px.line(
    summary,
    x=x_col,
    y="pct_condensate",
    markers=True,
    title=f"📈 % Condensate ({view_mode})"
)

fig.add_hline(
    y=80,
    line_dash="dash",
    line_color="red",
    annotation_text="Target 80%"
)

fig.update_layout(
    hovermode="x unified",
    yaxis_title="% Condensate",
    xaxis_title="วันที่",
    height=450
)

st.plotly_chart(fig, use_container_width=True)
def status(x):
    if x >= 80:
        return "🟢 ผ่าน"
    elif x >= 70:
        return "🟡 เฉียด"
    else:
        return "🔴 ไม่ผ่าน"

summary["status"] = summary["pct_condensate"].apply(status)

total = len(summary)
pass_ok = (summary["status"] == "🟢 ผ่าน").sum()
warn = (summary["status"] == "🟡 เฉียด").sum()
fail = (summary["status"] == "🔴 ไม่ผ่าน").sum()
st.subheader("📌 KPI สรุปช่วงที่เลือก")

c1, c2, c3, c4 = st.columns(4)

c1.metric("ทั้งหมด", f"{total} ช่วง")
c2.metric("🟢 ผ่าน", f"{pass_ok}", f"{pass_ok/total*100:.1f}%")
c3.metric("🟡 เฉียด", f"{warn}", f"{warn/total*100:.1f}%")
c4.metric("🔴 ไม่ผ่าน", f"{fail}", f"{fail/total*100:.1f}%")
st.sidebar.subheader("📅 เลือกวันที่ต้องการดู")

selected_date = st.sidebar.date_input(
    "เลือกวัน",
    value=df["date"].max(),
    min_value=df["date"].min(),
    max_value=df["date"].max()
)
day_df = df[
    df["date"].dt.date == pd.to_datetime(selected_date).date()
]
if day_df.empty:
    st.warning("❌ ไม่มีข้อมูลในวันที่เลือก")
    st.stop()
total_steam = day_df["steam_ton"].sum()
total_cond = day_df["condensate_ton"].sum()

pct_cond = (total_cond / total_steam) * 100 if total_steam > 0 else 0
TARGET = 80              # %
COST_PER_TON = 664      # บาท/ตัน steam (ตัวอย่าง)
loss_pct = max(0, TARGET - pct_cond)

steam_loss_ton = (loss_pct / 100) * total_steam
cost_loss = steam_loss_ton * COST_PER_TON
if pct_cond >= TARGET:
    status = "🟢 ผ่าน"
elif pct_cond >= TARGET - 10:
    status = "🟡 เฉียด"
else:
    status = "🔴 ไม่ผ่าน"
st.subheader(f"📌 สรุปผลวันที่ {selected_date}")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Steam (ตัน)", f"{total_steam:,.1f}")
c2.metric("Condensate (ตัน)", f"{total_cond:,.1f}")
c3.metric("% Condensate", f"{pct_cond:.1f}%", status)
c4.metric("💸 Cost Loss", f"{cost_loss:,.0f} บาท")
TARGET = 80          # %
COST_PER_TON = 664  # บาท/ตัน
daily = (
    df.groupby(df["date"].dt.date)
    .agg(
        steam=("steam_ton", "sum"),
        condensate=("condensate_ton", "sum")
    )
    .reset_index()
)

daily["pct_cond"] = (daily["condensate"] / daily["steam"]) * 100
daily["loss_pct"] = (TARGET - daily["pct_cond"]).clip(lower=0)
daily["steam_loss"] = (daily["loss_pct"] / 100) * daily["steam"]
daily["cost_loss"] = daily["steam_loss"] * COST_PER_TON
st.subheader("📅 เลือกช่วงวันที่ (รายวัน)")

start, end = st.date_input(
    "ช่วงวันที่",
    [daily["date"].min(), daily["date"].max()]
)

daily_plot = daily[
    (daily["date"] >= start) & (daily["date"] <= end)
]
st.subheader("📈 Cost Loss รายวัน")

st.line_chart(
    daily_plot.set_index("date")["cost_loss"]
)
monthly = (
    df.groupby(df["date"].dt.to_period("M"))
    .agg(
        steam=("steam_ton", "sum"),
        condensate=("condensate_ton", "sum")
    )
    .reset_index()
)

monthly["month"] = monthly["date"].astype(str)

monthly["pct_cond"] = (monthly["condensate"] / monthly["steam"]) * 100
monthly["loss_pct"] = (TARGET - monthly["pct_cond"]).clip(lower=0)
monthly["steam_loss"] = (monthly["loss_pct"] / 100) * monthly["steam"]
monthly["cost_loss"] = monthly["steam_loss"] * COST_PER_TON
st.subheader("📆 เลือกปี (รายเดือน)")

year = st.selectbox(
    "เลือกปี",
    sorted(df["date"].dt.year.unique(), reverse=True)
)

monthly_plot = monthly[
    monthly["month"].str.startswith(str(year))
]
st.subheader("📊 Cost Loss รายเดือน")

st.bar_chart(
    monthly_plot.set_index("month")["cost_loss"]
)
TARGET = 80            # %
COST_PER_TON = 664    # บาท/ตัน

YELLOW_LIMIT = 10      # % ต่ำกว่า Target = เหลือง
daily = (
    df.groupby(df["date"].dt.date)
    .agg(
        steam=("steam_ton", "sum"),
        condensate=("condensate_ton", "sum")
    )
    .reset_index()
)

daily["pct_cond"] = (daily["condensate"] / daily["steam"]) * 100
daily["loss_pct"] = (TARGET - daily["pct_cond"]).clip(lower=0)
daily["steam_loss"] = (daily["loss_pct"] / 100) * daily["steam"]
daily["cost_loss"] = daily["steam_loss"] * COST_PER_TON
def loss_color(loss_pct):
    if loss_pct == 0:
        return "green"
    elif loss_pct <= YELLOW_LIMIT:
        return "orange"
    else:
        return "red"

daily["color"] = daily["loss_pct"].apply(loss_color)
daily["target_cost"] = 0
import plotly.express as px

fig_daily = px.bar(
    daily,
    x="date",
    y="cost_loss",
    color="color",
    color_discrete_map={
        "green": "#2ecc71",
        "orange": "#f1c40f",
        "red": "#e74c3c"
    },
    title="📈 Cost Loss รายวัน"
)

fig_daily.add_scatter(
    x=daily["date"],
    y=daily["target_cost"],
    mode="lines",
    name="Target Cost",
    line=dict(color="red", dash="dash")
)

st.plotly_chart(fig_daily, use_container_width=True)
daily["year"] = pd.to_datetime(daily["date"]).dt.year

year = st.selectbox(
    "📆 เลือกปี",
    sorted(daily["year"].unique(), reverse=True)
)

ytd = daily[daily["year"] == year].copy()
ytd["ytd_cost"] = ytd["cost_loss"].cumsum()
fig_ytd = px.line(
    ytd,
    x="date",
    y="ytd_cost",
    markers=True,
    title=f"📉 YTD Cost Loss ปี {year}"
)

st.plotly_chart(fig_ytd, use_container_width=True)

