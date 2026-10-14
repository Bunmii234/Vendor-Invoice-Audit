# Vendor Invoice & Billing Discrepancy Audit

**Python (pandas, openpyxl) · SQL (SQLite) · Excel**

I built this to practice the kind of check I help with at work - making sure what we get billed matches what we agreed to pay and what was actually provided. I can't share any work data, so everything here is **fake data I generated**.

## The problem

A vendor should bill **contract rate x quantity used**. But in real life:

- the rate slowly creeps above the contract
- they bill for more than we used
- random fees show up
- the same bill gets sent twice

If you only look at whether an invoice total "looks about right," you miss all of that. You only catch it by checking every invoice against the contract AND against your own records.

## The data - 3 tables

| File | What it is | Rows |
|---|---|---|
| `data/raw/invoices_raw.csv` | what the vendors billed | 1,462 invoices |
| `data/raw/contracts.csv` | what we agreed to pay | 12 vendors |
| `data/raw/usage_log.csv` | what our own records say we used | 1,400 jobs |

Nothing in the invoices says which ones are wrong - the audit has to find them. The export is also messy on purpose: **36 spellings of 12 vendor names** and **2 date formats**, like a real system export.

## What I did - 4 steps

| Step | File | Tool | What it does |
|---|---|---|---|
| 1 | `python/01_generate_data.py` | Python | makes the 3 fake tables |
| 2 | `python/02_clean_invoices.py` | pandas | fixes vendor names (36 -> 12), reads both date formats, stops if anything fails a check |
| 3 | `python/03_run_audit.py` + `sql/` | SQL | runs 4 checks with JOINs and totals the results |
| 4 | `python/04_build_excel_report.py` | pandas + openpyxl | builds the Excel report with a chart and a dispute list |

### The 4 checks (`sql/audit_checks.sql`)

1. **Rate above contract** - JOIN invoices to contracts. Flag if the billed rate is more than 0.5% over the contract rate.
2. **Quantity above usage** - JOIN invoices to the usage log. Flag if they billed more than we used.
3. **Unexplained fee** - the total doesn't equal rate x quantity.
4. **Likely duplicate** - SELF-JOIN (the table joined to itself). Same vendor, same quantity, same amount within 14 days, and no usage record of its own.

## What I found

- **$225,120.73 overbilled** across **395 invoices** (about 27% of all invoices)
- **5 of the 12 vendors = 75.3%** of it. One vendor alone was $58,673
- By cause: rate above contract **$138,549** · quantity above usage **$80,856** · unexplained fees **$5,716**
- **62 likely duplicate invoices** - **$344,515** that could get paid twice
- Most of the flagged dollars were on invoices already **Approved** - so the money probably already went out. That's the case for checking before approval, not after.

## The hard part

Deciding where "a little high" ends and "overcharged" starts. A 0.5% buffer ignores rounding but still catches small 2-6% rate creep, which is the easiest kind to miss.

For duplicates, matching amounts alone wasn't enough - it flagged a few real repeat orders by mistake. Adding "no usage record" fixed that.

## Run it yourself

Open a terminal in this folder, then:

```
pip install -r requirements.txt
python python/01_generate_data.py
python python/02_clean_invoices.py
python python/03_run_audit.py
python python/04_build_excel_report.py
```

The report shows up at `output/Vendor_Billing_Audit.xlsx` with 4 sheets: **Summary · By Vendor (with chart) · By Issue · Dispute List**.

Every code file has notes under each block explaining what that part does - I wrote them as I learned it.
