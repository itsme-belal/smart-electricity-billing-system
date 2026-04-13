import sqlite3
from datetime import datetime
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# -----------------------------
# SAFE INPUT
# -----------------------------
def get_float_input(prompt):
    while True:
        try:
            val = float(input(prompt))
            if val < 0:
                print("❌ Negative not allowed!")
                continue
            return val
        except:
            print("❌ Enter valid number!")

def get_month():
    months = ["January","February","March","April","May","June",
              "July","August","September","October","November","December"]
    while True:
        m = input("Enter month: ")
        if m in months:
            return m
        print("❌ Invalid month!")

def get_year():
    while True:
        try:
            y = int(input("Enter year: "))
            if 2000 <= y <= 2100:
                return y
            print("❌ Invalid year!")
        except:
            print("❌ Enter valid year!")

def confirm():
    return input("Confirm? (y/n): ").lower() == "y"

# -----------------------------
# DATABASE
# -----------------------------
conn = sqlite3.connect("electricity_bill.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    floor TEXT,
    date TEXT,
    month TEXT,
    year INTEGER,
    previous_reading REAL,
    current_reading REAL,
    unit_used REAL,
    electricity_bill REAL,
    gas_bill REAL,
    rent REAL,
    due REAL,
    total_bill REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS readings (
    floor TEXT PRIMARY KEY,
    last_reading REAL
)
""")

# -----------------------------
# FLOORS
# -----------------------------
floors = [
    "1st floor front","1st floor back",
    "2nd floor front","2nd floor back",
    "4th floor front","4th floor back",
    "5th floor front","5th floor back"
]

gas_floors = [
    "1st floor back","2nd floor front",
    "2nd floor back","4th floor front"
]

# -----------------------------
# ADD BILL (NO SKIP)
# -----------------------------
def add_bill():
    now = datetime.now()
    date = now.strftime("%d-%m-%Y")
    month = now.strftime("%B")
    year = now.year

    print(f"\n📅 Billing: {month} {year}")

    for floor in floors:
        print(f"\n--- {floor.upper()} ---")

        while True:
            cursor.execute("SELECT last_reading FROM readings WHERE floor=?", (floor,))
            res = cursor.fetchone()

            if res:
                previous = res[0]
                print(f"Previous: {previous}")
            else:
                previous = get_float_input("Previous reading: ")

            current = get_float_input("Current reading: ")
            rent = get_float_input("Rent: ")
            due = get_float_input("Due: ")

            if current < previous:
                print("❌ Current must be greater than previous!")
                continue

            unit = current - previous
            electricity = unit * 9
            gas = 1080 if floor in gas_floors else 0
            total = electricity + gas + rent + due

            print(f"➡ Total: {total} Tk")

            if confirm():
                cursor.execute("""
                INSERT INTO bills (
                    floor,date,month,year,
                    previous_reading,current_reading,
                    unit_used,electricity_bill,gas_bill,
                    rent,due,total_bill
                )
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                """, (floor,date,month,year,
                      previous,current,unit,electricity,
                      gas,rent,due,total))

                cursor.execute("""
                INSERT INTO readings VALUES (?,?)
                ON CONFLICT(floor) DO UPDATE SET last_reading=excluded.last_reading
                """, (floor,current))

                break
            else:
                print("🔁 Re-enter data...")

    conn.commit()
    print("✅ All bills saved!")

# -----------------------------
# VIEW
# -----------------------------
def view():
    df = pd.read_sql_query("SELECT * FROM bills", conn)
    print(df)

# -----------------------------
# SEARCH
# -----------------------------
def search():
    m = get_month()
    y = get_year()
    df = pd.read_sql_query(
        "SELECT * FROM bills WHERE month=? AND year=?",
        conn, params=(m,y))
    print(df if not df.empty else "❌ No data found!")

# -----------------------------
# DELETE
# -----------------------------
def delete_bill():
    id = int(input("Enter ID: "))
    if confirm():
        cursor.execute("DELETE FROM bills WHERE id=?", (id,))
        conn.commit()
        print("✅ Deleted!")

# -----------------------------
# EDIT
# -----------------------------
def edit_bill():
    id = int(input("Enter ID: "))
    
    cursor.execute("SELECT due, total_bill FROM bills WHERE id=?", (id,))
    row = cursor.fetchone()

    if not row:
        print("❌ Not found!")
        return

    old_due = row[0]
    total = row[1]

    new_due = get_float_input("New Due: ")

    new_total = total - old_due + new_due

    if confirm():
        cursor.execute("""
        UPDATE bills 
        SET due=?, total_bill=?
        WHERE id=?
        """, (new_due, new_total, id))
        
        conn.commit()
        print("✅ Updated!")

# -----------------------------
# SUMMARY
# -----------------------------
def summary():
    m = get_month()
    y = get_year()

    df = pd.read_sql_query(
        "SELECT * FROM bills WHERE month=? AND year=?",
        conn, params=(m,y))

    if df.empty:
        print("❌ No data!")
        return

    print("\n===== MONTHLY SUMMARY =====")
    print("Units:", df['unit_used'].sum())
    print("Electricity:", df['electricity_bill'].sum())
    print("Gas:", df['gas_bill'].sum())
    print("Rent:", df['rent'].sum())
    print("Due:", df['due'].sum())
    print("---------------------------")
    print("Grand Total:", df['total_bill'].sum())

# -----------------------------
# EXPORT EXCEL
# -----------------------------
def export_excel():
    df = pd.read_sql_query("SELECT * FROM bills", conn)
    df.to_excel("bills.xlsx", index=False)
    print("✅ Excel exported!")

# -----------------------------
# PDF (ALL FLATS)
# -----------------------------
def print_all_bills_pdf():
    m = get_month()
    y = get_year()

    cursor.execute("SELECT * FROM bills WHERE month=? AND year=?", (m,y))
    rows = cursor.fetchall()

    if not rows:
        print("❌ No data!")
        return

    styles = getSampleStyleSheet()

    for row in rows:
        filename = f"{row[1]}_{m}_{y}.pdf"
        pdf = SimpleDocTemplate(filename)

        content = []

        content.append(Paragraph("<b>Electricity Bill</b>", styles['Title']))
        content.append(Spacer(1,10))

        content.append(Paragraph(f"Floor: {row[1]}", styles['Normal']))
        content.append(Paragraph(f"Month: {row[3]} {row[4]}", styles['Normal']))
        content.append(Spacer(1,10))

        content.append(Paragraph(f"Previous: {row[5]}", styles['Normal']))
        content.append(Paragraph(f"Current: {row[6]}", styles['Normal']))
        content.append(Paragraph(f"Units: {row[7]}", styles['Normal']))
        content.append(Spacer(1,10))

        content.append(Paragraph(f"Electricity: {row[8]} Tk", styles['Normal']))
        content.append(Paragraph(f"Gas: {row[9]} Tk", styles['Normal']))
        content.append(Paragraph(f"Rent: {row[10]} Tk", styles['Normal']))
        content.append(Paragraph(f"Due: {row[11]} Tk", styles['Normal']))
        content.append(Spacer(1,10))

        content.append(Paragraph(f"<b>Total: {row[12]} Tk</b>", styles['Heading2']))

        pdf.build(content)

    print("✅ All PDF bills created!")

# -----------------------------
# MENU
# -----------------------------
while True:
    print("\n===== MENU =====")
    print("1 Add Bill")
    print("2 View")
    print("3 Search")
    print("4 Delete")
    print("5 Edit")
    print("6 Summary")
    print("7 Export Excel")
    print("8 Print PDF (All Flats)")
    print("9 Exit")

    ch = input("Choice: ")

    if ch == "1": add_bill()
    elif ch == "2": view()
    elif ch == "3": search()
    elif ch == "4": delete_bill()   # ✅ FIXED
    elif ch == "5": edit_bill()
    elif ch == "6": summary()
    elif ch == "7": export_excel()
    elif ch == "8": print_all_bills_pdf()
    elif ch == "9": break
    else: print("❌ Invalid!")

conn.close()