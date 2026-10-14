# STEP 5 - Save the charts as pictures for the README
# Problem: GitHub can't show an Excel file, so anyone looking at my repo sees text but no chart.
#          Saving the charts as PNG images lets the README show them at the top.

import os
import pandas as pd
import matplotlib.pyplot as plt
# NOTE: matplotlib = the Python tool for drawing charts. pyplot (plt) is the part that draws them.

os.makedirs("images", exist_ok=True)
flags = pd.read_csv("output/flagged_invoices.csv")
pricing = flags[flags["issue"] != "Likely duplicate"]
# NOTE: Made an images folder, opened the flags from Step 3, and kept only the pricing problems
#       (duplicates are a different thing - the whole bill - so they're not in these charts).

BLUE = "#2a78d6"
DARK = "#0b0b0b"
GRAY = "#52514e"
# NOTE: The 3 colors I use - one blue for the bars, dark for titles, gray for labels.

# ---------- Chart 1: overbilling by vendor ----------
by_vendor = pricing.groupby("vendor_name")["overbilled"].sum().sort_values()
# NOTE: Total overbilled per vendor (a PivotTable), sorted smallest to biggest
#       so the biggest bar ends up at the TOP of a sideways bar chart.

fig, ax = plt.subplots(figsize=(9, 5.5))
ax.barh(by_vendor.index, by_vendor.values, color=BLUE, height=0.65)
for i, value in enumerate(by_vendor.values):
    ax.text(value + 600, i, f"${value:,.0f}", va="center", fontsize=9, color=GRAY)
# NOTE: barh = horizontal bars (vendor names are long, so sideways is easier to read).
#       The loop writes the dollar amount at the end of each bar. f"${value:,.0f}" = $58,673 format.

ax.set_title("Pricing overbilling by vendor - $225,120 total, top 5 vendors = 75%",
             loc="left", fontsize=12, color=DARK)
ax.set_xlabel("Overbilled ($)", color=GRAY)
ax.xaxis.set_major_formatter("${x:,.0f}")
ax.spines[["top", "right"]].set_visible(False)
ax.tick_params(colors=GRAY)
ax.set_xlim(0, by_vendor.max() * 1.15)
plt.tight_layout()
plt.savefig("images/overbilling_by_vendor.png", dpi=150)
plt.close()
# NOTE: Added the title and axis label, made the axis numbers show as $20,000 instead of 20000,
#       removed the top and right border lines (cleaner),
#       left extra room on the right for the labels, then saved it as a picture.

# ---------- Chart 2: overbilling by cause ----------
by_issue = pricing.groupby("issue")["overbilled"].sum().sort_values()
# NOTE: Same idea, but one bar per cause: rate, quantity, or unexplained fee.

fig, ax = plt.subplots(figsize=(9, 3))
ax.barh(by_issue.index, by_issue.values, color=BLUE, height=0.55)
for i, value in enumerate(by_issue.values):
    ax.text(value + 1500, i, f"${value:,.0f}", va="center", fontsize=9, color=GRAY)
ax.set_title("What's causing it - most overbilling is the rate, not the quantity",
             loc="left", fontsize=12, color=DARK)
ax.set_xlabel("Overbilled ($)", color=GRAY)
ax.xaxis.set_major_formatter("${x:,.0f}")
ax.spines[["top", "right"]].set_visible(False)
ax.tick_params(colors=GRAY)
ax.set_xlim(0, by_issue.max() * 1.18)
plt.tight_layout()
plt.savefig("images/overbilling_by_cause.png", dpi=150)
plt.close()
# NOTE: Same steps as chart 1, just a shorter chart because there are only 3 bars.

print("Saved images/overbilling_by_vendor.png and images/overbilling_by_cause.png")
