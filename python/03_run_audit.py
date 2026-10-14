# STEP 3 - Load the data into a SQL database and run the audit checks
# Problem: I need to compare every invoice to the contract and to our usage records.
#          That's matching 3 tables - which is exactly what SQL JOINs are for.
# The SQL lives in the sql/ folder. This script just runs it.

import sqlite3
import pandas as pd
# NOTE: sqlite3 = a small SQL database that lives in one file (built into Python, nothing to install).
#       Same SQL I'd write in SQL Server, just lighter.

con = sqlite3.connect("output/audit.db")
con.executescript(open("sql/schema.sql").read())
# NOTE: Created/opened the database file output/audit.db and connected to it (con = the connection).
#       Then ran schema.sql, which builds the 3 empty tables.

inv = pd.read_csv("output/invoices_clean.csv")
inv["invoice_date"] = pd.to_datetime(inv["invoice_date"]).dt.strftime("%Y-%m-%d")
inv.to_sql("invoices", con, if_exists="append", index=False)
pd.read_csv("data/raw/contracts.csv").to_sql("contracts", con, if_exists="append", index=False)
pd.read_csv("data/raw/usage_log.csv").to_sql("usage_log", con, if_exists="append", index=False)
# NOTE: Loaded the clean invoices, the contracts, and the usage log into the 3 tables.
#       I wrote dates as 2025-03-14 because SQLite needs that format to do date math later.

checks = open("sql/audit_checks.sql").read().split(";")
results = []
for query in checks:
    if query.strip() != "":
        results.append(pd.read_sql(query, con))
flags = pd.concat(results, ignore_index=True)
# NOTE: Opened audit_checks.sql and cut it into separate queries at every ";" (every query ends with one).
#       Ran the 4 checks one by one - each one gives back a small table of flagged invoices.
#       if query.strip() != "" skips the empty piece after the last ";".
#       pd.concat stacked all 4 tables into one list called flags (like pasting 4 lists under each other).

flags.to_sql("flags", con, if_exists="replace", index=False)
flags.to_csv("output/flagged_invoices.csv", index=False)
print("Flags found:", len(flags), "\n")
# NOTE: Saved the flags as a new table in the database AND as a CSV so Step 4 can use it.
#       Printed the count - 457 flags.

summaries = open("sql/summary_queries.sql").read().split(";")
for query in summaries:
    if query.strip() != "":
        print(pd.read_sql(query, con).to_string(index=False), "\n")
# NOTE: Same thing for the summary queries (by vendor, by issue, top 5 share, stop or recover, by month).
#       Ran each one and printed the result.

con.close()
# NOTE: Closed the database connection.
