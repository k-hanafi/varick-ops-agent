"""GraphQL schema = the business ontology. Types mirror the entities; resolvers
fetch related nodes on demand from SQLite."""

from typing import Optional

import strawberry

from db import get_conn


@strawberry.type
class Vendor:
    id: str
    name: str
    status: str


@strawberry.type
class Payment:
    id: str
    amount: float
    paid_date: str


@strawberry.type
class PurchaseOrder:
    id: str
    amount: float
    description: str
    vendor_id: strawberry.Private[str]

    @strawberry.field
    def vendor(self) -> Optional[Vendor]:
        return _get_vendor(self.vendor_id)


@strawberry.type
class Invoice:
    id: str
    amount: float
    status: str
    vendor_id: strawberry.Private[str]
    po_id: strawberry.Private[Optional[str]]

    @strawberry.field
    def vendor(self) -> Optional[Vendor]:
        return _get_vendor(self.vendor_id)

    @strawberry.field
    def purchase_order(self) -> Optional[PurchaseOrder]:
        return _get_po(self.po_id) if self.po_id else None

    @strawberry.field
    def payments(self) -> list[Payment]:
        return _get_payments(self.id)


def _get_vendor(vendor_id: str) -> Optional[Vendor]:
    conn = get_conn()
    row = conn.execute("SELECT * FROM vendors WHERE id = ?", (vendor_id,)).fetchone()
    conn.close()
    return Vendor(id=row["id"], name=row["name"], status=row["status"]) if row else None


def _get_po(po_id: str) -> Optional[PurchaseOrder]:
    conn = get_conn()
    row = conn.execute("SELECT * FROM purchase_orders WHERE id = ?", (po_id,)).fetchone()
    conn.close()
    if not row:
        return None
    return PurchaseOrder(
        id=row["id"],
        amount=row["amount"],
        description=row["description"],
        vendor_id=row["vendor_id"],
    )


def _get_payments(invoice_id: str) -> list[Payment]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM payments WHERE invoice_id = ?", (invoice_id,)
    ).fetchall()
    conn.close()
    return [
        Payment(id=r["id"], amount=r["amount"], paid_date=r["paid_date"]) for r in rows
    ]


def _build_invoice(row) -> Invoice:
    return Invoice(
        id=row["id"],
        amount=row["amount"],
        status=row["status"],
        vendor_id=row["vendor_id"],
        po_id=row["po_id"],
    )


@strawberry.type
class Query:
    @strawberry.field
    def invoice(self, id: str) -> Optional[Invoice]:
        conn = get_conn()
        row = conn.execute("SELECT * FROM invoices WHERE id = ?", (id,)).fetchone()
        conn.close()
        return _build_invoice(row) if row else None

    @strawberry.field
    def vendor(self, id: str) -> Optional[Vendor]:
        return _get_vendor(id)

    @strawberry.field
    def invoices(self) -> list[Invoice]:
        conn = get_conn()
        rows = conn.execute("SELECT * FROM invoices").fetchall()
        conn.close()
        return [_build_invoice(r) for r in rows]


schema = strawberry.Schema(query=Query)
