# ⚡ Smart Electricity Billing System (CLI)

A complete **Python-based electricity billing system** for managing multi-floor house billing with advanced features like PDF generation, Excel export, and monthly summaries.

---

## 🚀 Features

* ✅ Add electricity bill (multi-floor system)
* ✅ Auto unit & bill calculation
* ✅ Auto previous reading tracking
* ✅ Gas bill integration (selected floors)
* ✅ Monthly summary report
* ✅ Search by month & year
* ✅ Edit bill (update due)
* ✅ Delete bill
* ✅ Export to Excel
* ✅ Generate PDF bills (per flat)

---

## 🧠 How It Works

* Current reading → stored as next month's previous reading
* Unit = Current - Previous
* Electricity = Unit × 9 Tk
* Gas = 1080 Tk (selected flats only)
* Total = Electricity + Gas + Rent + Due

---

## 🏢 Supported Floors

* 1st floor (front, back)
* 2nd floor (front, back)
* 4th floor (front, back)
* 5th floor (front, back)

---

## ⛽ Gas Connection

Gas bill (1080 Tk) applies to:

* 1st floor back
* 2nd floor front & back
* 4th floor front

Other flats have **no gas bill (0 Tk)**

---

## 🛠️ Installation

```bash
pip install pandas reportlab openpyxl
```

---

## ▶️ Run the Program

```bash
python main.py
```

---

## 📊 Menu Options

```
1 Add Bill
2 View Data
3 Search (Month + Year)
4 Delete
5 Edit (Update Due)
6 Summary
7 Export Excel
8 Generate PDF
9 Exit
```

---

## 📁 Output Files

* `electricity_bill.db` → Database
* `bills.xlsx` → Excel export
* `*.pdf` → Individual flat bills

---

## ⚠️ Notes

* Ensure correct month spelling (e.g., April, May)
* Current reading must be greater than previous
* Data is stored permanently using SQLite

---

## 🔥 Future Improvements

* GUI (Desktop app)
* Web dashboard
* Mobile app (APK)
* Cloud sync system

---

## 👨‍💻 Author

Developed by **[Your Name]**

---

## ⭐ Support

If you like this project, give it a ⭐ on GitHub!
