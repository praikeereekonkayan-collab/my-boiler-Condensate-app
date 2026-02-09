import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="Boiler Dashboard",
    layout="wide"
)

# =============================
# LOAD DATA
# =============================
@st.cache_data
def load_data():
    sheet_id = "1G_ikK60FZUgctnM7SLZ4Ss0p6demBrlCwIre27fXsco"
    sheet_name = "condensate"
    sheet_name_encoded = urllib.parse.quote(sheet_name)

    url = (
        f"https://docs.google.com/spreadsheets/d/"
        f"{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name_encoded}"
    )

    df= pd.read_csv(url)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    data["cost_loss"] = data["steam_loss"] * data["mark_up"]

    return df


data = load_data()
# =============================
# SELECT VIEW
# =============================
view = st.radio(
    "🔘 เลือกมุมมอง",
    ["ผู้บริหาร", "วิศวกร", "ช่าง"],
    horizontal=True
)

# =============================
# EXECUTIVE VIEW
# =============================
if view == "ผู้บริหาร":
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("💰 Cost Loss รวม", f"{data['cost_loss'].sum():,.0f} บาท")
    col2.metric("📊 Avg Condensate", f"{data['pct_condensate'].mean():.2%}")
    col3.metric("⚠️ ต่ำกว่า Target", (data["pct_condensate"] < 0.90).sum())
    col4.metric("📅 จำนวนวัน", len(data))

    data["month"] = data["date"].dt.to_period("M").astype(str)
    monthly = data.groupby("month")["cost_loss"].sum().reset_index()

    fig = px.line(monthly, x="month", y="cost_loss", markers=True)
    st.plotly_chart(fig, use_container_width=True)

# =============================
# ENGINEERING VIEW
# =============================
elif view == "วิศวกร":
    col1, col2 = st.columns(2)

    fig1 = px.line(data, x="date", y="pct_condensate", markers=True)
    fig1.add_hline(y=0.90, line_dash="dash", line_color="red")
    col1.plotly_chart(fig1, use_container_width=True)

    fig2 = px.line(data, x="date", y="steam_loss", markers=True)
    col2.plotly_chart(fig2, use_container_width=True)

    st.dataframe(
        data[["date", "pct_condensate", "steam_loss", "diff", "cost_loss"]],
        use_container_width=True
    )

# =============================
# MAINTENANCE VIEW
# =============================
elif view == "ช่าง":
    today = data.sort_values("date").iloc[-1]
    status = "🟢 ปกติ" if today["pct_condensate"] >= 0.90 else "🔴 ผิดปกติ"

    st.metric("สถานะวันนี้", status)

    c1, c2, c3 = st.columns(3)
    c1.metric("Condensate Today", f"{today['pct_condensate']:.2%}")
    c2.metric("Steam Loss Today", f"{today['steam_loss']:.1f}")
    c3.metric("Cost Loss Today", f"{today['cost_loss']:,.0f}")

    alert = data[data["pct_condensate"] < 0.90]
    st.dataframe(
        alert[["date", "pct_condensate", "steam_loss", "cost_loss"]],
        use_container_width=True
    )

# =============================
# TARGET / COST SETTING
# =============================
TARGET_COND = 0.90
TARGET_STEAM_LOSS = 80
TARGET_DIFF = 0.00
COST_PER_UNIT_STEAM = 664  # บาท / หน่วย

# =============================
# SIDEBAR FILTER
# =============================
st.sidebar.header("🔎 Filter")

start_date, end_date = st.sidebar.date_input(
    "เลือกช่วงวันที่",
    [data["date"].min(), data["date"].max()]
)

# =============================
# FILTER BY DATE
# =============================
filtered = data[
    data["date"].between(
        pd.to_datetime(start_date),
        pd.to_datetime(end_date)
    )
].copy()

if filtered.empty:
    st.warning("⚠️ ไม่มีข้อมูลในช่วงที่เลือก")
    st.stop()

# =============================
# TIME VIEW
# =============================
st.subheader("📆 เลือกรูปแบบเวลา")

view_type = st.radio(
    "",
    ["รายวัน", "รายเดือน", "รายปี"],
    horizontal=True
)

# =============================
# PREPARE PLOT DATA
# =============================
plot_df = filtered.copy()

if view_type == "รายเดือน":
    plot_data["month"] = plot_data["date"].dt.to_period("M")
    plot_data = plot_data.groupby("month", as_index=False).mean()
    plot_data["date"] = plot_data["month"].dt.to_timestamp()

elif view_type == "รายปี":
    plot_data["year"] = plot_data["date"].dt.year
    plot_data = plot_data.groupby("year", as_index=False).mean()



# =============================
# KPI
# =============================
st.title("🏭 Boiler & Condensate Dashboard")

c1, c2, c3, c4 = st.columns(4)

c1.metric("♻️ % Condensate Avg", f"{filtered['pct_condensate'].mean():.2f}%")
c2.metric("🔥 Steam Loss Avg", f"{filtered['steam_loss'].mean():.2f}")
c3.metric("💨 DIFF Avg", f"{filtered['diff'].mean():.2f}")
c4.metric("💰 Cost Loss (฿)", f"{filtered['cost_loss'].sum():,.0f}")

# =============================
# GRAPHS
# =============================
st.subheader("📈 Trend")

x_col = "date" if view_type != "รายปี" else "year"

col1, col2, col3 = st.columns(3)

with col1:
    fig1 = px.line(
        plot_df,
        x=x_col,
        y="pct_condensate",
        title="% Condensate",
        markers=True
    )
    fig1.add_hline(y=TARGET_COND, line_dash="dash", line_color="red")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.line(
        plot_df,
        x=x_col,
        y="steam_loss",
        title="Steam Loss",
        markers=True
    )
    fig2.add_hline(y=TARGET_STEAM_LOSS, line_dash="dash", line_color="red")
    st.plotly_chart(fig2, use_container_width=True)

with col3:
    fig3 = px.line(
        plot_df,
        x=x_col,
        y="diff",
        title="DIFF",
        markers=True
    )
    fig3.add_hline(y=TARGET_DIFF, line_dash="dash", line_color="red")
    st.plotly_chart(fig3, use_container_width=True)

# =============================
# COST LOSS GRAPH
# =============================
st.subheader("💸 Cost Loss")

fig_cost = px.bar(
    filtered,
    x="date",
    y="cost_loss",
    title="Cost Loss"
)

st.plotly_chart(fig_cost, use_container_width=True)

# =============================
# TABLE
# =============================
st.subheader("📋 Daily Report")
st.dataframe(filtered, use_container_width=True)


