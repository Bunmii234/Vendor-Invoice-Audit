-- SUMMARY QUERIES - turning the list of flags into answers.
-- They all use the "flags" table that 03_run_audit.py creates.
-- Pattern for almost every business question: filter (WHERE) -> group (GROUP BY) -> total (SUM) -> sort (ORDER BY)


-- Q1 - Which vendors overbill us the most?
-- GROUP BY vendor = one row per vendor (a PivotTable). Duplicates left out - they're counted separately.
SELECT vendor_name,
       COUNT(DISTINCT invoice_id) AS flagged_invoices,
       ROUND(SUM(overbilled), 2) AS overbilled
FROM flags
WHERE issue <> 'Likely duplicate'
GROUP BY vendor_name
ORDER BY overbilled DESC;


-- Q2 - What is causing the overbilling?
-- Same idea, one row per issue type.
SELECT issue,
       COUNT(*) AS invoices,
       ROUND(SUM(overbilled), 2) AS dollars
FROM flags
GROUP BY issue
ORDER BY dollars DESC;


-- Q3 - How much of the overbilling comes from just the top 5 vendors?
-- Inside part: total per vendor, sorted biggest first, LIMIT 5 = keep only the top 5.
-- Outside part: add those 5 up and divide by the total of ALL vendors.
SELECT ROUND(SUM(overbilled), 2) AS top5_overbilled,
       ROUND(100.0 * SUM(overbilled) /
             (SELECT SUM(overbilled) FROM flags WHERE issue <> 'Likely duplicate'), 1) AS top5_share_pct
FROM (
    SELECT vendor_name, SUM(overbilled) AS overbilled
    FROM flags
    WHERE issue <> 'Likely duplicate'
    GROUP BY vendor_name
    ORDER BY overbilled DESC
    LIMIT 5
);


-- Q4 - Can we still stop the money, or do we need to get it back?
-- JOIN flags back to invoices to get each one's approval status.
-- CASE WHEN turns the status into an action:
--   Pending Review = not paid yet, so we can still STOP it
--   Approved       = probably already paid, so we need to RECOVER it
--   Rejected       = already stopped
SELECT CASE i.approval_status
         WHEN 'Pending Review' THEN 'Can still stop'
         WHEN 'Approved'       THEN 'Need to recover'
         ELSE 'Already rejected'
       END AS what_to_do,
       COUNT(DISTINCT f.invoice_id) AS flagged_invoices,
       ROUND(SUM(f.overbilled), 2) AS dollars
FROM flags f
JOIN invoices i ON i.invoice_id = f.invoice_id
GROUP BY what_to_do
ORDER BY dollars DESC;


-- Q5 - Is the overbilling getting worse? (pricing problems by month)
-- strftime('%Y-%m', date) pulls out just the year and month, like 2025-03.
-- In SQL Server it would be FORMAT(i.invoice_date, 'yyyy-MM') instead.
SELECT strftime('%Y-%m', i.invoice_date) AS month,
       COUNT(DISTINCT f.invoice_id) AS flagged_invoices,
       ROUND(SUM(f.overbilled), 2) AS overbilled
FROM flags f
JOIN invoices i ON i.invoice_id = f.invoice_id
WHERE f.issue <> 'Likely duplicate'
GROUP BY month
ORDER BY month;
