import pandas as pd
import streamlit as st

# 1) โหลดข้อมูลก่อน
data = pd.read_csv("your_file.csv")  
# หรือถ้ามาจาก Google Sheets / st.connection ก็ได้

# 2) แปลงคอลัมน์ date
data["date"] = pd.to_datetime(data["date"], errors="coerce")

# 3) ลบแถวที่ date ว่าง
data = data.dropna(subset=["date"])
conn = st.connection("gsheets", type=GSheetsConnection)
data = conn.read(worksheet="Sheet1")

data["date"] = pd.to_datetime(data["date"], errors="coerce")
data = data.dropna(subset=["date"])
import pandas as pd
import plotly.express as px
import streamlit as st

data["date"] = pd.to_datetime(data["date"], errors="coerce")
data = data.dropna(subset=["date"])

data["day"] = data["date"].dt.date
data["month"] = data["date"].dt.to_period("M").astype(str)
data["year"] = data["date"].dt.year
min_date = data["date"].min().date()
max_date = data["date"].max().date()

start_date, end_date = st.date_input(
    "📅 เลือกช่วงวันที่",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

df_filter = data[
    (data["date"].dt.date >= start_date) &
    (data["date"].dt.date <= end_date)
]
daily = (
    df_filter.groupby("day", as_index=False)["cost_loss"]
    .sum()
)

monthly = (
    df_filter.groupby("month", as_index=False)["cost_loss"]
    .sum()
)

yearly = (
    df_filter.groupby("year", as_index=False)["cost_loss"]
    .sum()
)
st.subheader("📊 Cost Loss Summary")

col1, col2, col3 = st.columns(3)

with col1:
    fig_day = px.line(
        daily,
        x="day",
        y="cost_loss",
        markers=True,
        title="รายวัน"
    )
    st.plotly_chart(fig_day, use_container_width=True)

with col2:
    fig_month = px.bar(
        monthly,
        x="month",
        y="cost_loss",
        title="รายเดือน"
    )
    st.plotly_chart(fig_month, use_container_width=True)

with col3:
    fig_year = px.bar(
        yearly,
        x="year",
        y="cost_loss",
        title="รายปี"
    )
    st.plotly_chart(fig_year, use_container_width=True)

