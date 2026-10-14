# STEP 7 - Build the dashboard web page
# Problem: people who don't read code (Finance, managers) need to SEE the results with one link.
# How: the page design lives in dashboard/template.html. It has a spot that says __DATA__.
#      This script works out the numbers, drops them into that spot, and saves docs/index.html.
#      GitHub Pages then shows docs/index.html as a website.

import os
import json
import pandas as pd
# NOTE: json = a way to write Python data (lists, dicts) as text a web page can read.

flags = pd.read_csv("output/flagged_invoices.csv")
inv = pd.read_csv("output/invoices_clean.csv")
pricing = flags[flags["issue"] != "Likely duplicate"]
dups = flags[flags["issue"] == "Likely duplicate"]
# NOTE: Same start as Step 4 - open the flags and invoices, split pricing problems from duplicates.

# ---------- the 4 headline numbers ----------
by_vendor_total = pricing.groupby("vendor_name")["overbilled"].sum().sort_values(ascending=False)
kpis = {
    "invoices": len(inv),
    "overbilled": round(pricing["overbilled"].sum(), 2),
    "pricing_invoices": pricing["invoice_id"].nunique(),
    "pricing_pct": round(100 * pricing["invoice_id"].nunique() / len(inv)),
    "duplicates": len(dups),
    "duplicate_dollars": round(dups["overbilled"].sum(), 2),
    "top5_pct": round(100 * by_vendor_total.head(5).sum() / by_vendor_total.sum(), 1),
}
# NOTE: A dict of the numbers for the 4 tiles at the top of the page.
#       head(5) = the top 5 vendors, so top5_pct = their share of all overbilling (75.3%).

# ---------- by vendor ----------
by_vendor = []
for vendor, dollars in by_vendor_total.items():
    rows = pricing[pricing["vendor_name"] == vendor]
    by_vendor.append({
        "vendor": vendor,
        "overbilled": round(dollars, 2),
        "invoices": rows["invoice_id"].nunique(),
        "share": round(100 * dollars / by_vendor_total.sum(), 1),
    })
# NOTE: One entry per vendor (biggest first): dollars, how many invoices, and % of the total.

# ---------- by problem type ----------
by_issue = []
issue_totals = pricing.groupby("issue")["overbilled"].agg(["sum", "count"]).sort_values("sum", ascending=False)
for issue, row in issue_totals.iterrows():
    by_issue.append({"issue": issue, "dollars": round(row["sum"], 2), "invoices": int(row["count"])})
# NOTE: One entry per problem type. agg(["sum", "count"]) gets the dollars AND the number of invoices at once.

# ---------- stop it or get it back ----------
ACTIONS = {"Pending Review": "Can still stop", "Approved": "Need to recover", "Rejected": "Already rejected"}
with_status = flags.merge(inv[["invoice_id", "approval_status"]], on="invoice_id")
with_status["action"] = with_status["approval_status"].map(ACTIONS)
stop_recover = []
for action in ["Need to recover", "Can still stop", "Already rejected"]:
    rows = with_status[with_status["action"] == action]
    stop_recover.append({"action": action, "dollars": round(rows["overbilled"].sum(), 2),
                         "invoices": rows["invoice_id"].nunique()})
# NOTE: Turned each flag's approval status into an action (Pending = can still stop, Approved = need to recover),
#       then for each action added up the dollars and counted the invoices.
#       nunique = count each invoice once, because one invoice can have 2 problems.

# ---------- by month ----------
by_month = []
with_dates = pricing.merge(inv[["invoice_id", "invoice_date"]], on="invoice_id")
with_dates["month"] = pd.to_datetime(with_dates["invoice_date"]).dt.strftime("%Y-%m")
for month, dollars in with_dates.groupby("month")["overbilled"].sum().items():
    label = pd.to_datetime(month + "-01").strftime("%b")
    by_month.append({"label": label, "dollars": round(dollars, 2)})
# NOTE: Pricing overbilling per month. The label turns "2025-03" into "Mar".

# ---------- did the audit catch the right things? ----------
accuracy = pd.read_csv("output/accuracy_check.csv").fillna("")
accuracy_rows = accuracy.to_dict("records")
false_alarms = int(open("output/false_alarms.txt").read())
# NOTE: The scorecard from Step 4. to_dict("records") turns the table into a list of rows the page can read.

# ---------- the dispute list ----------
table = flags.merge(inv[["invoice_id", "invoice_date", "amount_billed", "approval_status"]], on="invoice_id")
table = table.sort_values("overbilled", ascending=False)
disputes = []
for _, row in table.iterrows():
    disputes.append({
        "invoice_id": row["invoice_id"],
        "vendor": row["vendor_name"],
        "date": str(row["invoice_date"])[:10],
        "issue": row["issue"],
        "overbilled": round(row["overbilled"], 2),
        "amount": round(row["amount_billed"], 2),
        "status": row["approval_status"],
        "action": ACTIONS[row["approval_status"]],
    })
# NOTE: Every flagged invoice with its details, biggest first - this becomes the searchable table.
#       str(...)[:10] keeps just the date part (2025-03-14).

# ---------- put it in the page ----------
data = {"kpis": kpis, "by_vendor": by_vendor, "by_issue": by_issue,
        "stop_recover": stop_recover, "by_month": by_month,
        "accuracy": accuracy_rows, "false_alarms": false_alarms, "disputes": disputes}
template = open("dashboard/template.html").read()
page = template.replace("__DATA__", json.dumps(data))
os.makedirs("docs", exist_ok=True)
open("docs/index.html", "w").write(page)
open("docs/.nojekyll", "w").write("")
print("Saved docs/index.html -", len(disputes), "invoices in the dispute list")
# NOTE: Packed everything into one dict, turned it into text with json.dumps,
#       and swapped it in where the template says __DATA__. Then saved the finished page.
#       .nojekyll is an empty file that tells GitHub Pages to show my page exactly as it is.
