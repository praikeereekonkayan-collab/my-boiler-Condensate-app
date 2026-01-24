# ======================
# IMPORT
# ======================
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import json
import os
import requests

st.set_page_config(page_title="CONDENSATE BOILER", layout="wide")

# ======================
# CONFIG
# ======================
KPI = 0.70

COST_WATER = 25     # บาท / m3
COST_CHEM = 8       # บาท / ton steam
COST_FUEL = 120     # บาท / ton steam

# ======================
# LOAD DATA (Google Sheet export CSV)
# ======================
sheet_url = "https://docs.google.com/spreadsheets/d/1G_ikK60FZUgctnM7SLZ4Ss0p6demBrlCwIre27fXsco/export?format=csv&gid=1778119668"

df = pd.read_csv(sheet_url)

df["date"] = pd.to_datetime(df["date"])

# ======================
# CALCULATION
# ======================
df["cond_loss_m3"] = df["steam_total"] - df["condensate_return"]
df["cond_loss_m3"] = df["cond_loss_m3"].clip(lower=0)

df["loss_water_baht"] = df["cond_loss_m3"] * COST_WATER
df["loss_chem_baht"] = df["steam_total"] * COST_CHEM
df["loss_fuel_baht"] = df["steam_total"] * COST_FUEL

df["loss_total_baht"] = (
    df["loss_water_baht"]
    + df["loss_chem_baht"]
    + df["loss_fuel_baht"]
)

# ======================
# MODE SELECT
# ======================
st.title("♻️ CONDENSATE RETURN DASHBOARD")

mode = st.radio(
    "เลือกรูปแบบรายงาน",
    ["รายวัน", "รายเดือน", "รายปี"],
    horizontal=True
)

if mode == "รายวัน":
    df_show = df.groupby("date").mean().reset_index()

elif mode == "รายเดือน":
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df_show = df.groupby("month").mean().reset_index()

else:
    df["year"] = df["date"].dt.year
    df_show = df.groupby("year").mean().reset_index()

# ======================
# KPI COLOR
# ======================
def kpi_color(val):
    if val >= 0.80:
        return "green"
    elif val >= 0.70:
        return "gold"
    else:
        return "red"

df_show["color"] = df_show["condensate_pct"].apply(kpi_color)

# ======================
# GRAPH 1 : % CONDENSATE
# ======================
fig1 = px.bar(
    df_show,
    x=df_show.columns[0],
    y="condensate_pct",
    color="color",
    title="% Condensate Return",
)

fig1.add_hline(
    y=KPI,
    line_dash="dash",
    line_color="red",
    annotation_text="KPI 70%"
)

st.plotly_chart(fig1, use_container_width=True)

# ======================
# GRAPH 2 : LOSS BAHT
# ======================
fig2 = px.line(
    df_show,
    x=df_show.columns[0],
    y="loss_total_baht",
    markers=True,
    title="💸 Loss Trend (Baht)"
)

st.plotly_chart(fig2, use_container_width=True)

# ======================
# ALERT
# ======================
latest = df.iloc[-1]

if latest["condensate_pct"] < KPI:
    st.error(
        f"""
🚨 CONDENSATE ต่ำกว่า KPI

% = {latest['condensate_pct']:.2f}
Loss = {latest['loss_total_baht']:,.0f} บาท
"""
    )
else:
    st.success("🟢 Condensate ผ่าน KPI")

# ======================
# TOP 10 LOSS
# ======================
st.subheader("🔥 TOP 10 วันที่สูญเสียสูงสุด")

top10 = (
    df.groupby("date")["loss_total_baht"]
    .sum()
    .reset_index()
    .sort_values("loss_total_baht", ascending=False)
    .head(10)
)

st.dataframe(top10.style.format({"loss_total_baht": "{:,.0f}"}))
st.divider()
st.subheader("📅 เลือกช่วงวันที่")

min_date = df["date"].min()
max_date = df["date"].max()

start_date, end_date = st.slider(
    "เลือกช่วงวันที่",
    min_value=min_date.date(),
    max_value=max_date.date(),
    value=(min_date.date(), max_date.date())
)

df_range = df[
    (df["date"].dt.date >= start_date)
    & (df["date"].dt.date <= end_date)
]
st.divider()
st.subheader("📊 KPI SUMMARY")

col1, col2, col3, col4 = st.columns(4)

avg_pct = df_range["condensate_pct"].mean()
total_loss = df_range["loss_total_baht"].sum()
avg_steam = df_range["steam_total"].mean()
avg_return = df_range["condensate_return"].mean()

col1.metric("♻️ Avg %Cond", f"{avg_pct:.2f} %")
col2.metric("💸 Loss รวม", f"{total_loss:,.0f} บาท")
col3.metric("🔥 Steam เฉลี่ย", f"{avg_steam:.1f}")
col4.metric("💧 Cond Return", f"{avg_return:.1f}")
st.divider()

if avg_pct >= 0.80:
    st.success("🟢 ระบบ Condensate ดีมาก")
elif avg_pct >= 0.70:
    st.warning("🟡 เริ่มต่ำกว่าเป้า ควรติดตาม")
else:
    st.error("🔴 Condensate ต่ำกว่า KPI — ต้องแก้ไขด่วน")
loss_break = df_range[[
    "loss_water_baht",
    "loss_chem_baht",
    "loss_fuel_baht"
]].sum().reset_index()

loss_break.columns = ["type", "baht"]

fig_loss = px.pie(
    loss_break,
    names="type",
    values="baht",
    title="💸 สัดส่วนเงินสูญเสีย"
)

st.plotly_chart(fig_loss, use_container_width=True)
st.divider()
st.subheader("🧠 AI วิเคราะห์สาเหตุ Condensate ต่ำ")

def analyze_root_cause(df):
    last7 = df.tail(7)

    avg_pct = last7["condensate_pct"].mean()
    avg_return = last7["condensate_return"].mean()
    avg_steam = last7["steam_total"].mean()
    avg_diff = last7["diff"].mean()

    reasons = []

    if avg_pct < 0.70:
        reasons.append("❌ %Condensate ต่ำกว่ามาตรฐาน")

    if avg_return < df["condensate_return"].mean() * 0.9:
        reasons.append("💧 ปริมาณ Condensate กลับต่ำกว่าค่าเฉลี่ย")

    if avg_steam > df["steam_total"].mean() * 1.1:
        reasons.append("🔥 การใช้ Steam สูงผิดปกติ")

    if avg_diff < -0.05:
        reasons.append("⚠️ Diff ติดลบมาก อาจมีการรั่วหรือ Drain เปิดค้าง")

    if len(reasons) == 0:
        reasons.append("✅ ระบบปกติ ไม่พบความผิดปกติ")

    return reasons


for r in analyze_root_cause(df):
    st.write("•", r)
st.divider()
st.subheader("📈 Forecast Loss ล่วงหน้า")

df_forecast = df[["date", "loss_total_baht"]].copy()
df_forecast["ma7"] = df_forecast["loss_total_baht"].rolling(7).mean()

future = df_forecast.tail(7).copy()
future["date"] = future["date"] + pd.to_timedelta(7, unit="D")

forecast_df = pd.concat([df_forecast, future])

fig_forecast = px.line(
    forecast_df,
    x="date",
    y="ma7",
    title="🔮 คาดการณ์ Loss ล่วงหน้า (7 วัน)"
)

st.plotly_chart(fig_forecast, use_container_width=True)
def send_line(msg):
    token = st.secrets.get("LINE_TOKEN", None)
    if token is None:
        st.warning("⚠️ ยังไม่ได้ตั้ง LINE_TOKEN")
        return

    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"message": msg}

    try:
        requests.post(url, headers=headers, data=data, timeout=10)
    except:
        st.error("❌ ส่ง LINE ไม่สำเร็จ")
def alert_once_per_day(cond_pct, loss):
    today = str(date.today())
    file = "alert_log.json"

    try:
        with open(file, "r") as f:
            log = json.load(f)
    except:
        log = {}

    if cond_pct < 0.70:

        if log.get(today) != "sent":

            msg = f"""
🚨 CONDENSATE ALERT

📅 วันที่: {today}
%Condensate = {cond_pct:.2f} %
KPI = 70 %

💸 Loss = {loss:,.0f} บาท
"""

            send_line(msg)

            log[today] = "sent"
            with open(file, "w") as f:
                json.dump(log, f)

            st.error("🔔 ส่ง LINE แจ้งเตือนแล้ว (วันนี้ครั้งเดียว)")
        else:
            st.info("ℹ️ วันนี้แจ้งเตือนไปแล้ว")
latest = df.iloc[-1]

alert_once_per_day(
    latest["condensate_pct"],
    latest["loss_total_baht"]
)
