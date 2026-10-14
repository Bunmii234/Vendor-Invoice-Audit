-- SQL SERVER (T-SQL) VERSION of sql/audit_checks.sql and sql/summary_queries.sql
-- The project runs on SQLite. Most companies (like many finance teams) use SQL Server,
-- so this file shows the same queries written the SQL Server way.
-- I haven't run this file on a real SQL Server - it's written for reference.
--
-- What's different from SQLite:
--   julianday(b) - julianday(a)      ->  DATEDIFF(day, a, b)
--   LIMIT 5 (at the end)             ->  TOP 5 (right after SELECT)
--   strftime('%Y-%m', date)          ->  FORMAT(date, 'yyyy-MM')
--   ORDER BY inside a subquery needs TOP, so Q3 uses a CTE instead


-- CHECK 1 - Rate above contract (same in both)
SELECT i.invoice_id, i.vendor_name, 'Rate above contract' AS issue,
       ROUND((i.billed_rate - c.contracted_rate) * i.quantity_billed, 2) AS overbilled
FROM invoices i
JOIN contracts c ON c.vendor_name = i.vendor_name
WHERE i.billed_rate > c.contracted_rate * 1.005;


-- CHECK 2 - Quantity above usage (same in both)
SELECT i.invoice_id, i.vendor_name, 'Quantity above usage' AS issue,
       ROUND((i.quantity_billed - u.recorded_quantity) * c.contracted_rate, 2) AS overbilled
FROM invoices i
JOIN usage_log u ON u.invoice_id = i.invoice_id
JOIN contracts c ON c.vendor_name = i.vendor_name
WHERE i.quantity_billed > u.recorded_quantity;


-- CHECK 3 - Unexplained fee (same in both)
SELECT invoice_id, vendor_name, 'Unexplained fee' AS issue,
       ROUND(amount_billed - billed_rate * quantity_billed, 2) AS overbilled
FROM invoices
WHERE amount_billed - billed_rate * quantity_billed > 0.01;


-- CHECK 4 - Likely duplicate
-- Different: DATEDIFF(day, earlier, later) instead of julianday() math.
SELECT DISTINCT later.invoice_id, later.vendor_name, 'Likely duplicate' AS issue,
       later.amount_billed AS overbilled
FROM invoices later
LEFT JOIN usage_log u ON u.invoice_id = later.invoice_id
JOIN invoices earlier
  ON  earlier.vendor_name     = later.vendor_name
  AND earlier.quantity_billed = later.quantity_billed
  AND earlier.amount_billed   = later.amount_billed
  AND earlier.invoice_id      < later.invoice_id
  AND DATEDIFF(day, earlier.invoice_date, later.invoice_date) BETWEEN 0 AND 14
WHERE u.invoice_id IS NULL;


-- Q3 - Share of overbilling from the top 5 vendors
-- Different: TOP 5 instead of LIMIT 5, and a CTE (WITH) instead of a subquery with ORDER BY.
WITH by_vendor AS (
    SELECT vendor_name, SUM(overbilled) AS overbilled
    FROM flags
    WHERE issue <> 'Likely duplicate'
    GROUP BY vendor_name
),
top5 AS (
    SELECT TOP 5 vendor_name, overbilled
    FROM by_vendor
    ORDER BY overbilled DESC
)
SELECT ROUND(SUM(overbilled), 2) AS top5_overbilled,
       ROUND(100.0 * SUM(overbilled) / (SELECT SUM(overbilled) FROM by_vendor), 1) AS top5_share_pct
FROM top5;


-- Q5 - Pricing overbilling by month
-- Different: FORMAT(date, 'yyyy-MM') instead of strftime, and GROUP BY repeats the expression
-- (SQL Server doesn't let you GROUP BY a column alias).
SELECT FORMAT(i.invoice_date, 'yyyy-MM') AS month,
       COUNT(DISTINCT f.invoice_id) AS flagged_invoices,
       ROUND(SUM(f.overbilled), 2) AS overbilled
FROM flags f
JOIN invoices i ON i.invoice_id = f.invoice_id
WHERE f.issue <> 'Likely duplicate'
GROUP BY FORMAT(i.invoice_date, 'yyyy-MM')
ORDER BY month;


-- Q4 - Stop or recover
-- Different: GROUP BY repeats the CASE expression instead of using the alias.
SELECT CASE i.approval_status
         WHEN 'Pending Review' THEN 'Can still stop'
         WHEN 'Approved'       THEN 'Need to recover'
         ELSE 'Already rejected'
       END AS what_to_do,
       COUNT(DISTINCT f.invoice_id) AS flagged_invoices,
       ROUND(SUM(f.overbilled), 2) AS dollars
FROM flags f
JOIN invoices i ON i.invoice_id = f.invoice_id
GROUP BY CASE i.approval_status
           WHEN 'Pending Review' THEN 'Can still stop'
           WHEN 'Approved'       THEN 'Need to recover'
           ELSE 'Already rejected'
         END
ORDER BY dollars DESC;
