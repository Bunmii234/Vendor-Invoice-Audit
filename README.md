# Vendor Invoice Audit

**Python (pandas) · SQL · Excel** · fake data I generated - no real company data

**[Open the live dashboard](https://bunmii234.github.io/vendor-invoice-audit/)**

## What it does

Checks 1,462 vendor invoices against the contract rate and our own usage records to find overbilling.

![Overbilling by vendor](images/overbilling_by_vendor.png)

## Results

- **$225,120 overbilled** across 395 invoices - 5 of 12 vendors = 75%
- **62 duplicate bills** - $344,515 that could be paid twice
- **$189,842 can still be stopped** (pending) - $367,398 was already approved and needs to be recovered
- Happens **every month** (~$18,760 a month) - a process problem, not one bad invoice
- **Audit caught 457 of 457 planted problems, 0 false alarms**

## How it works

1. **Generate** - fake invoices, contracts, usage log + an answer key the audit never sees
2. **Clean** (pandas) - fix vendor names, read mixed dates, stop if a check fails
3. **Audit** (SQL) - 4 checks: rate above contract, quantity above usage, unexplained fee, duplicate
4. **Grade** - compare the flags to the answer key
5. **Report** - 7-sheet Excel file, 3 charts, and the live dashboard

## Problems I hit and how I fixed them

| Problem | Fix |
|---|---|
| 12 vendors showed up as 36 spellings (caps, extra spaces) | Trimmed spaces, then matched every name to the official contract name |
| Two date formats in one column | `pd.to_datetime(format="mixed")` reads both |
| Duplicate check flagged real repeat orders | Added a rule: a duplicate also has no usage record of its own |
| Had to decide where "a little high" becomes overcharged | 0.5% buffer - ignores rounding, still catches 2-6% rate creep |
| No way to prove the checks were right | Saved an answer key and graded the audit against it |
| Duplicates mixed in with pricing problems | Kept separate - a duplicate is the whole bill, not just the extra part |
| GitHub can't show Excel, so nobody could see results | Added chart images and a live dashboard anyone can open |

## Limitations

Fake data, so 100% caught is expected - real data would be messier. The 0.5% buffer and "approved = paid" are my assumptions.

## Run it

```
pip install -r requirements.txt
python run_all.py
```

SQL Server versions of the queries are in [`sql_server/`](sql_server/). Every code file has notes under each block explaining what it does.
