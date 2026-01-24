# ======================
# 1️⃣ IMPORT (บนสุดไฟล์)
# ======================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests
import os
import json
from datetime import date


# ======================
# 2️⃣ SETTING
# ======================
KPI = 70
COST_WATER = 18
COST_CHEM = 6
COST_FUEL = 320


# ======================
# 3️⃣ LINE ALERT FUNCTION
# ======================
def send_alert(msg):
    is_cloud = os.getenv("STREAMLIT_RUNTIME") is not None

    if is_cloud:
        st.warning("⚠️ โหมด Cloud ไม่สามารถส่ง LINE ได้")
        return

    try:
        token = st.secrets.get("LINE_TOKEN", None)
        if token is None:
            st.error("❌ ไม่พบ LINE_TOKEN")
            return

        url = "https://notify-api.line.me/api/notify"
        headers = {"Authorization": f"Bearer {token}"}
        data = {"message": msg}

        requests.post(url, headers=headers, data=data, timeout=10)

    except:
        st.error("❌ ส่ง LINE ไม่สำเร็จ")


# ======================
# 4️⃣ LOAD DATA (สำคัญมาก)
# ======================
# ❗ แก้ตรงนี้ให้ตรงกับชีตจริงของพี่
df = pd.read_csv("data_dashboard.csv")
# หรือโค้ด Google Sheet เดิมของพี่


# ======================
# 5️⃣ PREPARE DATA
# ======================
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.dropna(subset=["date"])


# ======================
# 6️⃣ CALCULATION
# ======================
df["cond_percent"] = (df["cond_return"] / df["steam_use"]) * 100
df["cond_percent"] = df["cond_percent"].fillna(0)

df["cond_loss_m3"] = df["steam_use"] - df["cond_return"]
df["cond_loss_m3"] = df["cond_loss_m3"].clip(lower=0)

df["loss_water_baht"] = df["cond_loss_m3"] * COST_WATER
df["loss_chem_baht"] = df["steam_use"] * COST_CHEM
df["loss_fuel_baht"] = df["steam_use"] * COST_FUEL

df["loss_total_baht"] = (
    df["loss_water_baht"]
    + df["loss_chem_baht"]
    + df["loss_fuel_baht"]
)


# ======================
# 7️⃣ SELECT MODE
# ======================
mode = st.radio(
    "เลือกรูปแบบรายงาน",
    ["รายวัน", "รายเดือน", "รายปี"],
    horizontal=True
)

if mode == "รายวัน":
    df_show = df.groupby("date").mean(numeric_only=True).reset_index()

elif mode == "รายเดือน":
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df_show = df.groupby("month").mean(numeric_only=True).reset_index()

else:
    df["year"] = df["date"].dt.year
    df_show = df.groupby("year").mean(numeric_only=True).reset_index()


# ======================
# 8️⃣ KPI COLOR
# ======================
def kpi_color(val):
    if val >= 80:
        return "green"
    elif val >= 70:
        return "gold"
    else:
        return "red"

df_show["color"] = df_show["cond_percent"].apply(kpi_color)


# ======================
# 9️⃣ GRAPH
# ======================
fig = px.bar(
    df_show,
    x=df_show.columns[0],
    y="cond_percent",
    color="color",
    title="% Condensate Return"
)
st.plotly_chart(fig, use_container_width=True)

fig2 = px.line(
    df_show,
    x=df_show.columns[0],
    y="loss_total_baht",
    title="💸 Condensate Loss (Baht)"
)
st.plotly_chart(fig2, use_container_width=True)


# ======================
# 🔟 KPI TARGET LINE
# ======================
fig_kpi = px.line(
    df_show,
    x=df_show.columns[0],
    y="cond_percent",
    markers=True,
    title="% Condensate พร้อมเส้น KPI"
)

fig_kpi.add_hline(
    y=KPI,
    line_dash="dash",
    line_color="red",
    annotation_text="KPI 70%"
)

st.plotly_chart(fig_kpi, use_container_width=True)


# ======================
# 1️⃣1️⃣ TOP 10 LOSS
# ======================
top10 = (
    df.groupby("date")["loss_total_baht"]
    .sum()
    .reset_index()
    .sort_values("loss_total_baht", ascending=False)
    .head(10)
)

st.subheader("🔥 TOP 10 วันที่สูญเสียเงินสูงสุด")
st.dataframe(top10.style.format({"loss_total_baht": "{:,.0f}"}))


# ======================
# 1️⃣2️⃣ HEATMAP
# ======================
if "time" in df.columns:
    df["hour"] = pd.to_datetime(df["time"]).dt.hour

    heat = df.pivot_table(
        index="hour",
        columns=df["date"].dt.day_name(),
        values="cond_loss_m3",
        aggfunc="sum"
    )

    fig_heat = px.imshow(
        heat,
        title="🔥 Heatmap การสูญเสีย Condensate",
        aspect="auto"
    )

    st.plotly_chart(fig_heat, use_container_width=True)


# ======================
# 1️⃣3️⃣ ALERT ONCE PER DAY
# ======================
def alert_once_per_day(cond_percent, loss_baht, alert_limit=70):
    today = str(date.today())
    file = "alert_log.json"

    try:
        with open(file, "r") as f:
            log = json.load(f)
    except:
        log = {}

    if cond_percent < alert_limit:
        if log.get(today) != "sent":

            msg = f"""
🚨 CONDENSATE ALERT
วันที่: {today}
%Condensate = {cond_percent:.1f}%
Loss = {loss_baht:,.0f} บาท
"""

            send_alert(msg)
            log[today] = "sent"

            with open(file, "w") as f:
                json.dump(log, f)

            st.error("🔔 แจ้งเตือนแล้ว (วันนี้ครั้งเดียว)")
        else:
            st.info("ℹ️ วันนี้แจ้งเตือนไปแล้ว")
    else:
        st.success("🟢 Condensate ผ่าน KPI")


latest = df.iloc[-1]
alert_once_per_day(
    cond_percent=latest["cond_percent"],
    loss_baht=latest["loss_total_baht"]
)
