# STEP 4 - Check that the audit actually works
# Problem: anyone can write checks that flag stuff. The real question is - did they catch the RIGHT stuff?
#          Because I made this data, I know exactly which problems I planted (data/answer_key.csv).
#          So I can grade my own audit: what did it catch, what did it miss, and what did it flag by mistake?

import pandas as pd

flags = pd.read_csv("output/flagged_invoices.csv")
key = pd.read_csv("data/answer_key.csv")
# NOTE: Opened the audit's flags (from Step 3) and the answer key (from Step 1).
#       This is the ONLY step that opens the answer key - the audit itself never saw it.

WHAT_IT_SHOULD_FIND = {
    "rate_small": "Rate above contract",
    "rate_large": "Rate above contract",
    "padding": "Quantity above usage",
    "fee": "Unexplained fee",
    "duplicate": "Likely duplicate",
}
# NOTE: A lookup: for each problem I planted, which flag the audit should give it.
#       rate_small (2-6% over) and rate_large (15-40% over) should both show up as "Rate above contract".

results = []
for problem, issue in WHAT_IT_SHOULD_FIND.items():
    planted_ids = key[key["planted_problem"] == problem]["invoice_id"]
    flagged_ids = flags[flags["issue"] == issue]["invoice_id"]
    caught = planted_ids.isin(flagged_ids).sum()
    results.append({
        "planted_problem": problem,
        "should_be_flagged_as": issue,
        "planted": len(planted_ids),
        "caught": int(caught),
        "missed": int(len(planted_ids) - caught),
    })
# NOTE: For each planted problem: how many I planted, and how many of those invoices got the right flag.
#       .isin() = "is this ID in that other list?" - like a COUNTIF / XLOOKUP check in Excel.

clean_ids = key[key["planted_problem"] == "clean"]["invoice_id"]
false_alarms = clean_ids.isin(flags["invoice_id"]).sum()
# NOTE: A false alarm = a CLEAN invoice that got flagged anyway. That would mean a check is too strict.

results = pd.DataFrame(results)
total_planted = results["planted"].sum()
total_caught = results["caught"].sum()
print(results.to_string(index=False))
print()
print(f"Caught {total_caught} of {total_planted} planted problems ({100 * total_caught / total_planted:.1f}%)")
print(f"False alarms: {false_alarms} of {len(clean_ids)} clean invoices")
# NOTE: Printed the scorecard, then the 2 numbers that matter: catch rate and false alarms.

summary = pd.DataFrame([{"planted_problem": "TOTAL", "should_be_flagged_as": "",
                         "planted": total_planted, "caught": total_caught,
                         "missed": total_planted - total_caught}])
pd.concat([results, summary]).to_csv("output/accuracy_check.csv", index=False)
open("output/false_alarms.txt", "w").write(str(int(false_alarms)))
print("Saved output/accuracy_check.csv")
# NOTE: Saved the scorecard (with a TOTAL row at the bottom) so the Excel report and dashboard can show it.
#       The false-alarm count goes in a tiny text file.
