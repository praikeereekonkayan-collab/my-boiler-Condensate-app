import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# =========================
# ตั้งค่าหน้าเว็บ
# =========================
st.set_page_config(
    page_title="Condensate Boiler Dashboard",
    layout="wide"
)

st.title("🏭 Condensate Boiler Dashboard")

# =========================
# โหลดข้อมูล
# =========================
file = "%CONDENSATE BOILER.xlsx"
df = pd.read_excel(file)

# ข้ามหัวตารางซ้อน
df = df.iloc[2:].copy()

df.columns = [
    "Date",
    "Soft",
    "BoilerWater",
    "CondReturn",
    "Date2",
    "Target",
    "CondPercent",
    "Date3",
    "CondBHS",
    "CondBHSPercent",
    "Date4",
    "SteamTotal",
    "Date5",
    "AVG_DIFF",
    "x1",
    "DIFF",
    "x2"
]

# =========================
# จัดการวันที่ (กันพัง)
# =========================
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date"])

df["CondPercent"] = pd.to_numeric(df["CondPercent"], errors="coerce")
df["SteamTotal"] = pd.to_numeric(df["SteamTotal"], errors="coerce")

# =========================
# Sidebar Filter
# =========================
st.sidebar.header("📅 เลือกช่วงเวลา")

current_year = datetime.now().year
year_list = sorted(df["Date"].dt.year.unique())

default_year = current_year if current_year in year_list else year_list[-1]

select_year = st.sidebar.selectbox(
    "เลือกปี",
    year_list,
    
)

view_mode = st.sidebar.radio(
    "รูปแบบการดูข้อมูล",
    ["รายวัน", "รายเดือน", "รายปี"],
    key="mode"
)

# =========================
# FILTER
# =========================
df_year = df[df["Date"].dt.year == select_year]

# =========================
# SUMMARY
# =========================
if view_mode == "รายวัน":

    summary = (
        df_year
        .groupby(df_year["Date"].dt.date)
        .agg(
            Condensate_Percent=("CondPercent", "mean"),
            Steam=("SteamTotal", "sum")
        )
        .reset_index()
    )

    x_col = "Date"
    title = f"% Condensate รายวัน ปี {select_year}"

elif view_mode == "รายเดือน":

    summary = (
        df_year
        .groupby(df_year["Date"].dt.month)
        .agg(
            Condensate_Percent=("CondPercent", "mean"),
            Steam=("SteamTotal", "sum")
        )
        .reset_index()
    )

    summary["เดือน"] = summary["Date"].astype(str)
    x_col = "เดือน"
    title = f"% Condensate รายเดือน ปี {select_year}"

else:  # รายปี

    summary = (
        df
        .groupby(df["Date"].dt.year)
        .agg(
            Condensate_Percent=("CondPercent", "mean"),
            Steam=("SteamTotal", "sum")
        )
        .reset_index()
    )

    summary["ปี"] = summary["Date"].astype(str)
    x_col = "ปี"
    title = "% Condensate รายปี (ย้อนหลังทั้งหมด)"

# =========================
# KPI
# =========================
st.subheader("📊 KPI Summary")

col1, col2, col3 = st.columns(3)

avg_cond = summary["Condensate_Percent"].mean()

col1.metric(
    "♻️ % Condensate เฉลี่ย",
    f"{avg_cond:.2%}"
)

col2.metric(
    "🔥 Steam รวม",
    f"{summary['Steam'].sum():,.0f}"
)

col3.metric(
    "🎯 Target",
    "80 %"
)

# =========================
# กราฟ
# =========================
fig = px.bar(
    summary,
    x=x_col,
    y="Condensate_Percent",
    text_auto=".2%",
    title=title
)

fig.update_yaxes(tickformat=".0%")

st.plotly_chart(fig, use_container_width=True)

# =========================
# ตาราง
# =========================
st.subheader("📋 ตารางสรุป")

st.dataframe(summary, use_container_width=True)
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Condensate Boiler Dashboard",
    layout="wide"
)

st.title("🏭 Condensate Boiler Dashboard")

TARGET = 0.80

# =========================
# LOAD DATA
# =========================
df = pd.read_excel("%CONDENSATE BOILER.xlsx")
df = df.iloc[2:].copy()

df.columns = [
    "Date","Soft","BoilerWater","CondReturn","Date2","Target",
    "CondPercent","Date3","CondBHS","CondBHSPercent",
    "Date4","SteamTotal","Date5","AVG","x1","DIFF","x2"
]

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date"])

df["CondPercent"] = pd.to_numeric(df["CondPercent"], errors="coerce")
df["SteamTotal"] = pd.to_numeric(df["SteamTotal"], errors="coerce")

# =========================
# SIDEBAR
# =========================
st.sidebar.header("📅 ตัวกรองข้อมูล")

current_year = datetime.now().year
year_list = sorted(df["Date"].dt.year.unique())
default_year = current_year if current_year in year_list else year_list[-1]

year = st.sidebar.selectbox(
    "เลือกปี",
    year_list,
    index=year_list.index(default_year),
    key="year"
)

view = st.sidebar.radio(
    "รูปแบบการแสดง",
    ["รายวัน", "รายเดือน", "รายปี"],
    key="view"
)

# =========================
# FILTER
# =========================
df_year = df[df["Date"].dt.year == year]

# =========================
# SUMMARY
# =========================
if view == "รายวัน":
    summary = df_year.groupby(df_year["Date"].dt.date).agg(
        CondPercent=("CondPercent", "mean"),
        Steam=("SteamTotal", "sum")
    ).reset_index()
    x = "Date"
    title = f"% Condensate รายวัน ปี {year}"

elif view == "รายเดือน":
    summary = df_year.groupby(df_year["Date"].dt.month).agg(
        CondPercent=("CondPercent", "mean"),
        Steam=("SteamTotal", "sum")
    ).reset_index()
    summary["Month"] = summary["Date"].astype(str)
    x = "Month"
    title = f"% Condensate รายเดือน ปี {year}"

else:
    summary = df.groupby(df["Date"].dt.year).agg(
        CondPercent=("CondPercent", "mean"),
        Steam=("SteamTotal", "sum")
    ).reset_index()
    summary["Year"] = summary["Date"].astype(str)
    x = "Year"
    title = "% Condensate รายปี (ย้อนหลัง)"

avg = summary["CondPercent"].mean()

# =========================
# KPI STATUS
# =========================
if avg >= TARGET:
    status = "🟢 ผ่านเป้าหมาย"
elif avg >= 0.70:
    status = "🟡 เฝ้าระวัง"
else:
    status = "🔴 ต่ำกว่าเป้า"

# =========================
# KPI
# =========================
st.subheader("📊 KPI Summary")

c1, c2, c3, c4 = st.columns(4)

c1.metric("♻️ % Condensate เฉลี่ย", f"{avg:.2%}")
c2.metric("🎯 Target", "80%")
c3.metric("🔥 Steam รวม", f"{summary['Steam'].sum():,.0f}")
c4.metric("สถานะ KPI", status)

# =========================
# GRAPH 1
# =========================
fig1 = px.bar(
    summary,
    x=x,
    y="CondPercent",
    text_auto=".2%",
    title=title
)

fig1.add_hline(
    y=TARGET,
    line_dash="dash",
    annotation_text="Target 80%"
)

fig1.update_yaxes(tickformat=".0%")
st.plotly_chart(fig1, use_container_width=True)

# =========================
# GRAPH 2
# =========================
st.subheader("📈 Steam vs Condensate")

fig2 = px.scatter(
    summary,
    x="Steam",
    y="CondPercent",
    size="Steam",
    title="ความสัมพันธ์ Steam กับ % Condensate"
)

fig2.update_yaxes(tickformat=".0%")
st.plotly_chart(fig2, use_container_width=True)

# =========================
# EXEC SUMMARY
# =========================
st.subheader("🧾 Executive Summary")

st.info(
    f"""
    ปี {year} มีค่า % Condensate เฉลี่ย **{avg:.2%}**
    
    สถานะ KPI: **{status}**

    แนวทาง:
    - ควรรักษาระดับการคืน Condensate ให้มากกว่า 80%
    - ตรวจสอบจุดสูญเสีย Steam และ Condensate Return
    - ใช้ข้อมูลนี้ในการติดตามประสิทธิภาพ Boiler รายวัน
    """
)

# =========================
# TABLE
# =========================
st.subheader("📋 ตารางสรุป")
st.dataframe(summary, use_container_width=True)
# =========================
# COST CALCULATION
# =========================
LOSS_TARGET = 0.80
STEAM_COST_PER_TON = 1200   # บาท/ตัน (แก้ได้)

summary["LossPercent"] = LOSS_TARGET - summary["CondPercent"]
summary["LossPercent"] = summary["LossPercent"].apply(lambda x: x if x > 0 else 0)

summary["SteamLossTon"] = summary["Steam"] * summary["LossPercent"]
summary["LossCost"] = summary["SteamLossTon"] * STEAM_COST_PER_TON
st.subheader("💰 Estimated Condensate Loss Cost")

c1, c2, c3 = st.columns(3)

c1.metric(
    "Steam สูญเสีย (ตัน)",
    f"{summary['SteamLossTon'].sum():,.1f}"
)

c2.metric(
    "ต้นทุนสูญเสีย (บาท)",
    f"{summary['LossCost'].sum():,.0f}"
)

c3.metric(
    "ต้นทุน Steam / ตัน",
    f"{STEAM_COST_PER_TON:,.0f} บาท"
)
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet

def export_pdf(summary, year, avg, status):
    file_name = f"Condensate_Report_{year}.pdf"

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(file_name)

    elements = []
    elements.append(Paragraph("Condensate Boiler Executive Report", styles["Title"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"Year: {year}", styles["Normal"]))
    elements.append(Paragraph(f"Average Condensate: {avg:.2%}", styles["Normal"]))
    elements.append(Paragraph(f"KPI Status: {status}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    table_data = [["Period", "%Condensate", "Steam", "Loss Cost (THB)"]]

    for _, r in summary.iterrows():
        table_data.append([
            str(r[0]),
            f"{r['CondPercent']:.2%}",
            f"{r['Steam']:,.0f}",
            f"{r['LossCost']:,.0f}"
        ])

    table = Table(table_data)
    elements.append(table)

    doc.build(elements)

    return file_name
st.subheader("📄 Export Report")

if st.button("📥 ดาวน์โหลดรายงาน PDF"):
    pdf_file = export_pdf(summary, year, avg, status)

    with open(pdf_file, "rb") as f:
        st.download_button(
            "ดาวน์โหลดไฟล์ PDF",
            f,
            file_name=pdf_file
        )



