import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

# ---------------------------------------
# 1) เลือกโฟลเดอร์ที่เก็บไฟล์ Excel รายวัน
# ---------------------------------------
folder_path = "steam_daily/"      # แก้เป็นโฟลเดอร์ของคุณ เช่น "C:/data/steam/"
files = glob.glob(os.path.join(folder_path, "*.xlsx"))

print("พบไฟล์จำนวน:", len(files))

# ---------------------------------------
# 2) รวมไฟล์ทั้งหมดเข้าด้วยกัน
# ---------------------------------------
all_data = []

for f in files:
    df = pd.read_excel(f)
    all_data.append(df)

df = pd.concat(all_data, ignore_index=True)

print("รวมข้อมูลสำเร็จ จำนวนแถว:", len(df))

# ---------------------------------------
# 3) คำนวณ % Condensate
# ---------------------------------------
df["cond_percent"] = (df["Condensate_Return"] / df["Steam_Usage"]) * 100

# ---------------------------------------
# 4) สรุปผลราย Boiler
# ---------------------------------------
summary_boiler = df.groupby("Boiler").agg({
    "Steam_Usage": "sum",
    "Condensate_Return": "sum",
    "cond_percent": "mean"
})

# ---------------------------------------
# 5) สรุปผลรายวัน
# ---------------------------------------
daily = df.groupby("Date").sum()
daily["cond_percent"] = (daily["Condensate_Return"] / daily["Steam_Usage"]) * 100

# ---------------------------------------
# 6) ทำกราฟสรุป
# ---------------------------------------

# กราฟ Steam รายวัน
plt.figure(figsize=(12,5))
plt.plot(daily.index, daily["Steam_Usage"])
plt.title("Daily Steam Usage")
plt.xlabel("Date")
plt.ylabel("Steam Usage")
plt.grid()
plt.tight_layout()
plt.savefig("daily_steam_usage.png")
plt.show()

# กราฟ % Condensate รายวัน
plt.figure(figsize=(12,5))
plt.plot(daily.index, daily["cond_percent"])
plt.title("Daily Condensate (%)")
plt.ylabel("%")
plt.grid()
plt.tight_layout()
plt.savefig("daily_cond_percent.png")
plt.show()

# กราฟเปรียบเทียบ Boiler
plt.figure(figsize=(8,5))
plt.bar(summary_boiler.index, summary_boiler["cond_percent"])
plt.title("Average Condensate (%) by Boiler")
plt.ylabel("%")
plt.tight_layout()
plt.savefig("boiler_cond_percent.png")
plt.show()

# ---------------------------------------
# 7) Export เป็นรายงาน Excel
# ---------------------------------------
with pd.ExcelWriter("steam_all_report.xlsx") as writer:
    df.to_excel(writer, sheet_name="All_Data", index=False)
    summary_boiler.to_excel(writer, sheet_name="Summary_Boiler")
    daily.to_excel(writer, sheet_name="Summary_Daily")

print("\n รวมไฟล์ + สร้างรายงานสำเร็จ: steam_all_report.xlsx")
print("   และรูปกราฟถูกสร้างเรียบร้อยแล้ว")

