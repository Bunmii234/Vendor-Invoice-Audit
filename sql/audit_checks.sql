-- THE 4 AUDIT CHECKS
-- Each check finds one kind of overbilling and gives back the same 4 columns:
-- invoice_id, vendor_name, issue, overbilled (how many dollars too much)
-- Same columns = I can stack all 4 results into one list in Python.


-- CHECK 1 - Rate above contract
-- Question: did the vendor charge a higher rate than we agreed to?
-- JOIN = bring in the contract rate for each invoice by matching vendor_name (like an XLOOKUP).
-- 1.005 = I let it be up to 0.5% over before flagging it, so tiny rounding doesn't count.
-- Overbilled = (billed rate - contract rate) x quantity.
SELECT i.invoice_id, i.vendor_name, 'Rate above contract' AS issue,
       ROUND((i.billed_rate - c.contracted_rate) * i.quantity_billed, 2) AS overbilled
FROM invoices i
JOIN contracts c ON c.vendor_name = i.vendor_name
WHERE i.billed_rate > c.contracted_rate * 1.005;


-- CHECK 2 - Quantity above usage
-- Question: did they bill for more than our own records say we used?
-- 2 JOINs: usage_log (by invoice_id) for what we used, contracts (by vendor) for the rate.
-- Overbilled = (billed quantity - used quantity) x contract rate.
SELECT i.invoice_id, i.vendor_name, 'Quantity above usage' AS issue,
       ROUND((i.quantity_billed - u.recorded_quantity) * c.contracted_rate, 2) AS overbilled
FROM invoices i
JOIN usage_log u ON u.invoice_id = i.invoice_id
JOIN contracts c ON c.vendor_name = i.vendor_name
WHERE i.quantity_billed > u.recorded_quantity;


-- CHECK 3 - Unexplained fee
-- Question: is the total more than rate x quantity?
-- If the math doesn't add up, there's an extra charge nobody explained.
-- No JOIN needed - everything is on the invoice itself. 0.01 = ignore 1-cent rounding.
SELECT invoice_id, vendor_name, 'Unexplained fee' AS issue,
       ROUND(amount_billed - billed_rate * quantity_billed, 2) AS overbilled
FROM invoices
WHERE amount_billed - billed_rate * quantity_billed > 0.01;


-- CHECK 4 - Likely duplicate
-- Question: did they send the same bill twice?
-- SELF-JOIN = join the invoices table to itself, so I can compare each invoice ("later")
-- to every other invoice ("earlier") from the same vendor.
-- It's a duplicate if: same vendor, same quantity, same amount, within 14 days,
-- AND the later one has no usage record (LEFT JOIN ... IS NULL = no matching row found).
-- That last rule matters - without it, real repeat orders got flagged by mistake.
-- Overbilled = the whole invoice, because the whole thing would be paid twice.
SELECT DISTINCT later.invoice_id, later.vendor_name, 'Likely duplicate' AS issue,
       later.amount_billed AS overbilled
FROM invoices later
LEFT JOIN usage_log u ON u.invoice_id = later.invoice_id
JOIN invoices earlier
  ON  earlier.vendor_name     = later.vendor_name
  AND earlier.quantity_billed = later.quantity_billed
  AND earlier.amount_billed   = later.amount_billed
  AND earlier.invoice_id      < later.invoice_id
  AND julianday(later.invoice_date) - julianday(earlier.invoice_date) BETWEEN 0 AND 14
WHERE u.invoice_id IS NULL;
