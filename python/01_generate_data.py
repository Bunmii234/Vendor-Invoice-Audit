import os, random
import pandas as pd
from datetime import date, timedelta
# I just loaded os (folders) and random (a random number generator), plus pandas to save the tables at the end. Also loaded date and timedelta (a length of time, like 30 days).


random.seed(21)
# I locked the random number generator to start point 21, so every run creates the exact same data (1,462 invoices) and my results match the guide.

os.makedirs("data/raw", exist_ok=True)
# Created the folder data where 3 CSV files will be stored. exist_ok=True is if the folder already exists, keep going instead of erroring.

START, END = date(2025, 1, 1), date(2025, 12, 31)
# Set the invoice date range to Jan 1, 2025 - Dec 31, 2025.
#       START and END are used later to pick a random invoice date inside 2025.

VENDORS = [  # name, category, contracted rate, unit type
    ("Apex IT Consulting", "IT Services", 145.00, "hourly"),
    ("Meridian Systems Group", "IT Services", 130.00, "hourly"),
    ("Staples Business Advantage", "Office Supplies", 1.00, "per_unit"),
    ("OfficeMax Direct", "Office Supplies", 1.00, "per_unit"),
    ("Reliant Facilities Mgmt", "Facilities", 62.00, "hourly"),
    ("ClearView Janitorial", "Facilities", 38.00, "hourly"),
    ("Hartwell Legal Advisors", "Professional Services", 310.00, "hourly"),
    ("Beacon Consulting Partners", "Professional Services", 220.00, "hourly"),
    ("Vantage Software Inc", "Software Licensing", 42.00, "per_seat"),
    ("CloudSuite Solutions", "Software Licensing", 55.00, "per_seat"),
    ("Swift Freight Logistics", "Logistics & Shipping", 18.50, "per_shipment"),
    ("Regional Courier Co", "Logistics & Shipping", 14.00, "per_shipment"),
]
# Created a list called VENDORS holding 12 vendors (the square brackets [ ] = a list).
#       Each vendor is a group of 4 facts in round brackets ( ) = a tuple:
#       1) vendor name, 2) spend category, 3) the rate we agreed to pay in the contract,
#       4) what the rate is per (hour, unit, seat, or shipment).
#       Example: Hartwell Legal Advisors charges $310 per hour.
#       This is the "contract" that every invoice gets checked against later.
invoices, usage, answer_key, n = [], [], [], 1
# NOTE: Created 3 empty lists to fill up: invoices (what vendors bill us),
#       usage (what our own records say was used), and answer_key (which problem I planted where).
#       n = 1 is a counter for invoice numbers.

for _ in range(1400):
    # NOTE: Start a loop that repeats 1,400 times - one time per real job done by a vendor.
    #       Everything indented under this line happens on every repeat.

    name, cat, rate, unit = random.choice(VENDORS)
    # NOTE: Randomly picked 1 vendor from the VENDORS list and split its 4 facts into
    #       name, cat (category), rate (contract rate), and unit (hourly, per_unit, etc.).

    d = START + timedelta(days=random.randint(0, (END - START).days))
    # NOTE: Picked a random invoice date in 2025: START (Jan 1) + a random number of days
    #       between 0 and 364. (END - START).days = number of days in the year range.

    if unit == "hourly":
        qty = round(random.uniform(4, 80), 1)
    elif unit == "per_unit":
        qty = random.randint(20, 800)
    elif unit == "per_seat":
        qty = random.randint(5, 250)
    else:
        qty = random.randint(10, 400)
    # NOTE: Picked the TRUE quantity used, based on the unit type:
    #       hourly = 4 to 80 hours with 1 decimal (like 32.5), per_unit = 20-800 items,
    #       per_seat = 5-250 software seats, per_shipment = 10-400 shipments.
    #       random.uniform = decimal number, random.randint = whole number.

    fate = random.choices(["clean", "rate_small", "rate_large", "padding", "duplicate", "fee"],
                          weights=[0.68, 0.12, 0.05, 0.06, 0.04, 0.05])[0]
    # NOTE: Picked what kind of invoice this job turns into - most are clean (68%), the rest have a problem:
    #       rate_small = rate a little over contract (2-6%), rate_large = rate way over (15-40%),
    #       padding = billed for more than we used, duplicate = same bill sent twice, fee = random extra fee.
    #       This is the "answer key". It gets saved in its own file that the audit NEVER reads -
    #       only Step 4 opens it at the end, to check how many problems the audit actually caught.

    b_rate, b_qty = rate, qty
    if fate == "rate_small":   b_rate = round(rate * random.uniform(1.02, 1.06), 2)
    if fate == "rate_large":   b_rate = round(rate * random.uniform(1.15, 1.40), 2)
    if fate == "padding":      b_qty = round(qty * random.uniform(1.08, 1.25), 1)
    # NOTE: b_rate and b_qty = what the vendor BILLED. They start equal to the real rate and real quantity.
    #       Then if the fate is a rate problem I raised the rate, and if it's padding I raised the quantity 8-25%.

    amount = round(b_rate * b_qty, 2)
    if fate == "fee":          amount = round(amount + random.uniform(25, 150), 2)
    # NOTE: The invoice total = billed rate x billed quantity. For "fee" invoices I added $25-$150 on top
    #       that nothing explains - that's the hidden fee the audit has to catch.

    status = random.choices(["Approved", "Pending Review", "Rejected"], weights=[0.82, 0.13, 0.05])[0]
    # NOTE: Gave every invoice an approval status - 82% Approved, 13% Pending, 5% Rejected.
    #       Later this shows how much bad billing already got approved (paid out).

    inv = dict(invoice_id=f"INV{n:05d}", vendor_name=name, invoice_date=d, unit_type=unit,
               billed_rate=b_rate, quantity_billed=b_qty, amount_billed=amount, approval_status=status)
    invoices.append(inv)
    usage.append(dict(invoice_id=inv["invoice_id"], recorded_quantity=qty))
    if fate == "duplicate":
        answer_key.append(dict(invoice_id=inv["invoice_id"], planted_problem="clean"))
    else:
        answer_key.append(dict(invoice_id=inv["invoice_id"], planted_problem=fate))
    n += 1
    # NOTE: Built one invoice as a dict (a row with column names) and added it to the invoices list.
    #       f"INV{n:05d}" makes IDs like INV00001 (5 digits, zeros in front).
    #       Then I saved the TRUE quantity in the usage list - that's "our own records" to check the vendor against.
    #       The answer key gets what I planted. For a duplicate, the FIRST bill is clean - the copy is the problem.
    #       n += 1 moves the counter up so the next invoice gets the next number.

    if fate == "duplicate":
        dup = inv.copy()
        dup["invoice_id"] = f"INV{n:05d}"
        dup["invoice_date"] = d + timedelta(days=random.randint(2, 10))
        dup["approval_status"] = random.choices(["Approved", "Pending Review"], weights=[0.6, 0.4])[0]
        invoices.append(dup)
        answer_key.append(dict(invoice_id=dup["invoice_id"], planted_problem="duplicate"))
        n += 1
    # NOTE: For duplicates I made a copy of the same invoice (.copy()), then gave the copy a new ID,
    #       a date 2-10 days later, and its own approval status.
    #       I did NOT add a usage record for the copy - no new work happened, it's just the same bill twice.

mess = random.Random(99)
for inv in invoices:
    d = inv["invoice_date"]
    inv["invoice_date"] = d.strftime("%m/%d/%Y") if mess.random() < 0.25 else d.isoformat()
    r = mess.random()
    if r < 0.08:
        inv["vendor_name"] = inv["vendor_name"].upper()
    elif r < 0.15:
        inv["vendor_name"] = "  " + inv["vendor_name"] + " "
# NOTE: Made the data messy on purpose, like a real export. mess is its own random generator (seed 99)
#       so this part doesn't change the numbers above.
#       25% of dates come out as 03/14/2025 and the rest as 2025-03-14 (two formats in one column).
#       8% of vendor names go ALL CAPS and 7% get extra spaces around them - so 12 vendors turn into 36 spellings.

invoices_table = pd.DataFrame(invoices)
contracts_table = pd.DataFrame(VENDORS, columns=["vendor_name", "category", "contracted_rate", "unit_type"])
usage_table = pd.DataFrame(usage)
# NOTE: Turned my 3 Python lists into 3 tables (DataFrames) with pandas - basically 3 Excel sheets.
#       For the contracts I named the 4 columns in the same order as the facts in VENDORS.

invoices_table.to_csv("data/raw/invoices_raw.csv", index=False)
contracts_table.to_csv("data/raw/contracts.csv", index=False)
usage_table.to_csv("data/raw/usage_log.csv", index=False)
pd.DataFrame(answer_key).to_csv("data/answer_key.csv", index=False)
print("invoices:", len(invoices), "| contracts:", len(VENDORS), "| usage records:", len(usage))
# NOTE: Saved the 3 tables as CSV files - what vendors billed, what we agreed to pay, and what we actually used.
#       index=False = don't add an extra row-number column.
#       The answer key goes in data/answer_key.csv - NOT in data/raw, so it's clearly not part of the audit's input.
#       Then printed the counts so I know it worked: invoices: 1462 | contracts: 12 | usage records: 1400
