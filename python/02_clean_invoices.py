# STEP 2 - Clean the invoices with pandas
# Problem: the raw export is messy - 36 spellings of 12 vendors and 2 date formats.
#          If I total it like this, one vendor gets split into 3 and every number after this is wrong.
# Same thing at work: I check the data BEFORE it goes into a report, not after.

import pandas as pd
# NOTE: Loaded pandas and called it pd (short name everyone uses). pandas = Excel inside Python.

inv = pd.read_csv("data/raw/invoices_raw.csv")
contracts = pd.read_csv("data/raw/contracts.csv")
print("Raw invoices:", len(inv))
print("Distinct vendor spellings before:", inv["vendor_name"].nunique())
# NOTE: Opened the invoices and the contracts as 2 tables (DataFrames - basically 2 sheets).
#       Printed how many invoices there are and how many different vendor spellings - 36 before cleaning.

inv["vendor_name"] = inv["vendor_name"].str.strip()
# NOTE: .str.strip() removed the extra spaces before and after every vendor name ("  Apex IT " -> "Apex IT").
#       Same as TRIM() in Excel.

official = {}
for name in contracts["vendor_name"]:
    official[name.upper()] = name
inv["vendor_name"] = inv["vendor_name"].str.upper().map(official)
print("Distinct vendor spellings after:", inv["vendor_name"].nunique())
# NOTE: Built a lookup list (a dict) from the contracts: "APEX IT CONSULTING" -> "Apex IT Consulting".
#       The loop goes through the 12 official names and saves each one under its UPPERCASE version.
#       Then I made every invoice name uppercase and matched it to the official name with .map().
#       It's an XLOOKUP - look up the messy name, bring back the clean one. 36 spellings -> 12.

unmatched = inv["vendor_name"].isna().sum()
assert unmatched == 0, f"{unmatched} invoices have a vendor with no contract"
# NOTE: If a name didn't match anything it comes back empty (NaN). I counted those.
#       assert = a stop sign. If even 1 vendor has no contract, the script stops and tells me,
#       instead of quietly leaving that invoice out of the audit.

inv["invoice_date"] = pd.to_datetime(inv["invoice_date"], format="mixed")
print("Date range:", inv["invoice_date"].min().date(), "to", inv["invoice_date"].max().date())
# NOTE: Turned the date text into real dates. format="mixed" reads both 03/14/2025 and 2025-03-14.
#       Printed the first and last date as a sanity check: 2025-01-01 to 2026-01-01.
#       (A couple of duplicate bills land in early January because they're dated a few days after the original.)

assert (inv["amount_billed"] > 0).all(), "Found a zero or negative invoice"
assert inv["invoice_id"].is_unique, "Invoice IDs should be unique"
# NOTE: 2 more checks: no invoice is $0 or negative, and no invoice ID shows up twice.

inv.to_csv("output/invoices_clean.csv", index=False)
print("Saved output/invoices_clean.csv")
# NOTE: Saved the clean table as a new file. I never change the raw file - so I can always go back to it.
#       index=False = don't add an extra row-number column.
