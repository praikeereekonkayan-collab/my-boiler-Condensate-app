import streamlit as st
import pandas as pd
import plotly.express as px

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="Boiler Condensate Dashboard",
    layout="wide"
)

st.title("🏭 Boiler Condensate & Cost Loss Dashboard")

# =============================
# CONFIG
# =============================
TARGET_PCT = 80          # %
YELLOW_LIMIT = 70        # %
COST_PER_TON = 664       # บาท/ตัน

# =============================
# LOAD DATA FROM GOOGLE SHEET
# =============================
@st.cache_data
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1G_ikK60FZUgctnM7SLZ4Ss0p6demBrlCwIre27fXsco/export?format=csv&gid=181659687"
    df = pd.read_csv(url)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    return df

df = load_data()

# =============================
# SIDEBAR FILTER
# =============================
st.sidebar.header("🔎 ตัวกรอง")

view_type = st.sidebar.radio(
    "รูปแบบการดู",
    ["รายวัน", "รายเดือน", "รายปี"]
)

year = st.sidebar.selectbox(
    "เลือกปี",
    sorted(df["date"].dt.year.unique())
)

df_year = df[df["date"].dt.year == year]

# เลือกช่วงวันที่ (เฉพาะรายวัน)
if view_type == "รายวัน":
    min_date = df_year["date"].min()
    max_date = df_year["date"].max()

    start_date, end_date = st.sidebar.date_input(
        "📅 เลือกช่วงวันที่",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    df_filtered = df_year[
        (df_year["date"] >= pd.to_datetime(start_date)) &
        (df_year["date"] <= pd.to_datetime(end_date))
    ]
else:
    df_filtered = df_year

# =============================
# VIEW & FILTER
# =============================
if view_type == "รายวัน":
    data = (
        df_filtered
        .groupby("date", as_index=False)
        .sum(numeric_only=True)
    )

elif view_type == "รายเดือน":
    data = (
        df_year
        .groupby(df_year["date"].dt.to_period("M"))
        .sum(numeric_only=True)
        .reset_index()
    )
    data["date"] = data["date"].dt.to_timestamp()

else:  # รายปี
    data = (
        df
        .groupby(df["date"].dt.year)
        .sum(numeric_only=True)
        .reset_index()
    )
    data.rename(columns={"date": "year"}, inplace=True)

# =============================
# COLOR FUNCTION
# =============================
def loss_color(pct):
    if pct >= TARGET_PCT:
        return "green"
    elif pct >= YELLOW_LIMIT:
        return "yellow"
    else:
        return "red"

data["color"] = data["loss_pct"].apply(loss_color)

# =============================
# DAILY / MONTHLY COST GRAPH
# =============================
st.subheader("📈 Cost Loss")

fig_cost = px.line(
    data,
    x="date" if view_type != "รายปี" else "year",
    y="cost_loss",
    markers=True,
    title="Cost Loss"
)

st.plotly_chart(fig_cost, use_container_width=True)

# =============================
# YTD COST LOSS
# =============================
if view_type != "รายปี":
    data = data.sort_values("date")
    data["ytd_cost"] = data["cost_loss"].cumsum()

    fig_ytd = px.line(
        data,
        x="date",
        y="ytd_cost",
        markers=True,
        title=f"📉 YTD Cost Loss ปี {year}"
    )

    st.plotly_chart(fig_ytd, use_container_width=True)

# =============================
# TABLE
# =============================
st.subheader("📊 ตารางข้อมูล")
st.dataframe(data)


