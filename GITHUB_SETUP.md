# GitHub Upload Guide

## 📋 ไฟล์ที่ต้องอัปโหลด GitHub

### 🐍 Python Source Code (7 ไฟล์)
```
- app.py
- dashboard.py
- run_dashboard.py
- generate_report.py
- create_condensate_data.py
- add_condensate_data.py
- export_dashboard_html.py
```

### 📄 Documentation Files (8 ไฟล์)
```
- README.md
- INSTALL.md
- QUICKSTART.md
- DEPLOY.md
- INDEX.md
- SUMMARY.md
- FILEMANAGEMENT.md
- GITHUB_SETUP.md (ไฟล์นี้)
```

### ⚙️ Configuration Files (1 ไฟล์)
```
- requirements.txt
```

### ⛔ ไฟล์ที่ไม่อัปโหลด
```
- dashboard_*.html (ไฟล์ output ที่สร้างมา)
- condensate_report_*.txt (ไฟล์ report ที่สร้างมา)
- *.bat (Local environment specific)
- __pycache__/ (Python cache)
```

---

## 🚀 ขั้นตอนการอัปโหลด GitHub

### 1. สร้าง Repository ใหม่บน GitHub
- ไป https://github.com/new
- ตั้งชื่อ Repository (เช่น `dashboard-condensate`)
- เลือก `Public` (ถ้าต้องการให้คนอื่นดู)

### 2. Copy Repository URL
```bash
https://github.com/YOUR_USERNAME/dashboard-condensate.git
```

### 3. เปิด Terminal ในโฟลเดอร์ `test`
```bash
cd C:\Users\nb.boiler\OneDrive\Desktop\test
```

### 4. Initialize Git Repository
```bash
git init
git add .
git commit -m "Initial commit: Dashboard project"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/dashboard-condensate.git
git push -u origin main
```

---

## 📊 สรุปไฟล์

| ประเภท | จำนวน | ไฟล์ |
|--------|------|------|
| Python Code | 7 | app.py, dashboard.py, run_dashboard.py, generate_report.py, create_condensate_data.py, add_condensate_data.py, export_dashboard_html.py |
| Documentation | 8 | README.md, INSTALL.md, QUICKSTART.md, DEPLOY.md, INDEX.md, SUMMARY.md, FILEMANAGEMENT.md, GITHUB_SETUP.md |
| Configuration | 1 | requirements.txt |
| **รวมทั้งหมด** | **16** | - |

---

## 💾 .gitignore เอาไว้ข้ามไฟล์

```
dashboard_*.html
condensate_report_*.txt
*.bat
__pycache__/
*.pyc
.env
venv/
```

---

## ✅ Checklist ก่อนอัปโหลด

- [ ] ตรวจสอบ `requirements.txt` ครบถ้วน
- [ ] ตรวจสอบ `README.md` ถูกต้อง
- [ ] ตรวจสอบไฟล์ Python ไม่มี password/sensitive data
- [ ] ตรวจสอบ `.gitignore` อัพเดต
- [ ] สร้าง GitHub Repository ใหม่
- [ ] Run `git push`

---

**หมายเหตุ:** เปลี่ยน `YOUR_USERNAME` ด้วยชื่อ GitHub Account ของคุณ

