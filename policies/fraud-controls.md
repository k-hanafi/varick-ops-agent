# Fraud Controls

These controls protect against erroneous or fraudulent payments. If any control
is triggered, the invoice must be placed on hold and escalated for investigation.

## Vendor standing

Do not pay any invoice from a vendor whose status is `under_review`. Payments to
vendors under review are blocked until the review clears.

## Purchase order mismatch

An invoice must not exceed the amount of its matching purchase order. If the
invoice amount is greater than the purchase order amount, hold the invoice and
investigate the discrepancy before any payment.

## Duplicate payment

Before paying, confirm the invoice has not already been settled. If a payment
already exists for the invoice, do not pay again; hold it as a suspected
duplicate.
