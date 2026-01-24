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
