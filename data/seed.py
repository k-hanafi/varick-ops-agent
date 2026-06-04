"""Build the SQLite ontology store and populate it with mock data."""

from db import DB_PATH, get_conn

SCHEMA = """
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS invoices;
DROP TABLE IF EXISTS purchase_orders;
DROP TABLE IF EXISTS vendors;

CREATE TABLE vendors (
    id     TEXT PRIMARY KEY,
    name   TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('active', 'under_review'))
);

CREATE TABLE purchase_orders (
    id          TEXT PRIMARY KEY,
    vendor_id   TEXT NOT NULL REFERENCES vendors(id),
    amount      REAL NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE invoices (
    id        TEXT PRIMARY KEY,
    vendor_id TEXT NOT NULL REFERENCES vendors(id),
    po_id     TEXT REFERENCES purchase_orders(id),
    amount    REAL NOT NULL,
    status    TEXT NOT NULL
);

CREATE TABLE payments (
    id         TEXT PRIMARY KEY,
    invoice_id TEXT NOT NULL REFERENCES invoices(id),
    amount     REAL NOT NULL,
    paid_date  TEXT NOT NULL
);
"""

VENDORS = [
    ("V-001", "Acme Office Supplies", "active"),
    ("V-002", "Globex Logistics", "under_review"),
]

PURCHASE_ORDERS = [
    ("PO-5001", "V-001", 4200.0, "Office chairs"),
    ("PO-5002", "V-002", 9000.0, "Freight services"),
    ("PO-5003", "V-001", 10000.0, "Laptops"),
    ("PO-5004", "V-001", 4500.0, "Monitors"),
    ("PO-5005", "V-001", 800.0, "Misc supplies"),
]

INVOICES = [
    ("INV-1007", "V-001", "PO-5001", 4200.0, "received"),
    ("INV-1042", "V-002", "PO-5002", 12400.0, "received"),
    ("INV-1051", "V-001", "PO-5003", 10000.0, "received"),
    ("INV-1063", "V-001", "PO-5004", 4500.0, "received"),
    ("INV-1078", "V-001", "PO-5005", 800.0, "received"),
]

PAYMENTS = [
    ("PAY-9001", "INV-1063", 4500.0, "2026-05-20"),
]


def seed() -> None:
    conn = get_conn()
    conn.executescript(SCHEMA)
    conn.executemany("INSERT INTO vendors VALUES (?, ?, ?)", VENDORS)
    conn.executemany("INSERT INTO purchase_orders VALUES (?, ?, ?, ?)", PURCHASE_ORDERS)
    conn.executemany("INSERT INTO invoices VALUES (?, ?, ?, ?, ?)", INVOICES)
    conn.executemany("INSERT INTO payments VALUES (?, ?, ?, ?)", PAYMENTS)
    conn.commit()
    conn.close()
    print(f"Seeded {DB_PATH}")
    print(f"  {len(VENDORS)} vendors, {len(PURCHASE_ORDERS)} POs, "
          f"{len(INVOICES)} invoices, {len(PAYMENTS)} payments")


if __name__ == "__main__":
    seed()
