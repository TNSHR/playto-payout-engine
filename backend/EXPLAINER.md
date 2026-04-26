# EXPLAINER.md

## 1. The Ledger

**Balance Calculation Query:**

```python
from django.db.models import Sum

credits = merchant.ledger_entries.filter(
    entry_type="credit"
).aggregate(total=Sum("amount_paise"))["total"] or 0

debits = merchant.ledger_entries.filter(
    entry_type="debit"
).aggregate(total=Sum("amount_paise"))["total"] or 0

balance = credits - debits
```

### Why this design?

Instead of storing a mutable balance field, I implemented a **ledger-based system** where every transaction is recorded as either a credit or a debit.

Balance is always derived:

```
balance = sum(credits) - sum(debits)
```

### Why this matters

* Prevents race conditions from concurrent updates
* Ensures full auditability (no data loss)
* Supports safe rollback via compensating entries (refunds)
* Matches how real financial systems maintain correctness

---

## 2. The Lock

**Code used:**

```python
merchant = Merchant.objects.select_for_update().get(id=merchant_id)
```

### What this does

This applies a **row-level lock** using PostgreSQL (`SELECT FOR UPDATE`) inside a transaction.

### Why it is required

Without locking:

```
Balance = 100
Request A → withdraw 60
Request B → withdraw 60
→ Both succeed (incorrect)
```

With locking:

```
Request A locks row
Request B waits
Request B sees updated balance → fails
```

### Guarantee

* Ensures only one transaction modifies a merchant at a time
* Prevents double-spend issues

---

## 3. The Idempotency

### Implementation

```python
class Meta:
    unique_together = ("merchant", "idempotency_key")
```

### API Handling

```python
try:
    payout = Payout.objects.create(...)
except IntegrityError:
    payout = Payout.objects.get(...)
```

### How it works

* Client sends `Idempotency-Key`
* DB enforces uniqueness per merchant
* Duplicate requests trigger `IntegrityError`
* Existing payout is returned instead of creating a new one

### Why this is important

Handles:

* network retries
* double-clicks
* duplicate API calls

---

## 4. The State Machine

### Valid transitions

```
pending → processing → completed
pending → processing → failed
```

### Enforcement

```python
if payout.status != "pending":
    return
```

### Refund Logic (critical)

```python
with transaction.atomic():
    payout.status = "failed"
    payout.save()

    LedgerEntry.objects.create(
        merchant=payout.merchant,
        amount_paise=payout.amount_paise,
        entry_type="credit",
        reference_id=str(payout.id)
    )
```

### Why this matters

* Refund happens atomically with state change
* No money loss or duplication
* Ledger remains consistent

---



## 6. The AI Audit

### Initial incorrect approach

```python
existing = Payout.objects.filter(...).first()
if existing:
    return existing
```

### Problem

This introduces a race condition:

```
Request A → checks → no record
Request B → checks → no record
→ both create payout (duplicate)
```

### Fix

```python
try:
    create payout
except IntegrityError:
    fetch existing payout
```

### Key insight

* Application-level checks are not reliable
* Database constraints must enforce correctness
* Always assume concurrent requests

---

## 7. Additional Notes

### Money Handling

* All amounts stored as integers (paise)
* No floating point usage
* Avoids rounding issues

### Ledger Integrity

* Ledger is append-only
* No updates or deletes
* Refunds handled via compensating entries

### Architecture Overview

```
API → DB (transaction + locking + processing)
    → immediate status update
```

---

## Final Note

This system prioritizes:

* Correctness over convenience
* Database guarantees over application assumptions
* Auditability and financial safety

The implementation is intentionally minimal but focuses on the core problems of real payment systems: concurrency, idempotency, and data integrity.

The system was initially designed with asynchronous processing using Celery and Redis.

However, due to deployment limitations on Render’s free tier (no background workers), the payout processing was switched to synchronous execution.

The architecture still supports async scaling, and the Celery-based design is preserved conceptually.
