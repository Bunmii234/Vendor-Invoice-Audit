-- The 3 tables the audit uses. DROP TABLE IF EXISTS deletes the old table first,
-- so every time I run the project it starts fresh instead of adding the same rows twice.

DROP TABLE IF EXISTS invoices;
DROP TABLE IF EXISTS contracts;
DROP TABLE IF EXISTS usage_log;

-- What the vendors billed us. One row per invoice.
CREATE TABLE invoices (
    invoice_id      TEXT PRIMARY KEY,   -- INV00001 (PRIMARY KEY = can't repeat)
    vendor_name     TEXT,
    invoice_date    TEXT,
    unit_type       TEXT,               -- hourly, per_unit, per_seat, per_shipment
    billed_rate     REAL,               -- REAL = a number with decimals
    quantity_billed REAL,
    amount_billed   REAL,
    approval_status TEXT                -- Approved, Pending Review, Rejected
);

-- What we agreed to pay. One row per vendor.
CREATE TABLE contracts (
    vendor_name     TEXT PRIMARY KEY,
    category        TEXT,
    contracted_rate REAL,
    unit_type       TEXT
);

-- What our own records say was used. One row per real job.
CREATE TABLE usage_log (
    invoice_id        TEXT PRIMARY KEY,
    recorded_quantity REAL
);
