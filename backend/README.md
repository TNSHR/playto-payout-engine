# Playto Payout Engine

A production-grade payout engine that simulates how modern fintech systems handle withdrawals with strong guarantees around **money integrity, concurrency, idempotency, and failure handling**.

---

## 🚀 Overview

This system allows merchants to:

* View their balance (derived from ledger entries)
* Request payouts
* Track payout status
* Handle failures and retries safely

The system is designed to mirror real-world payment infrastructure where correctness is more important than feature count.

---

## 🧠 Key Concepts Implemented

### 1. Ledger-Based Accounting

* No balance is stored directly
* All transactions are recorded as **credits** and **debits**
* Balance is computed dynamically

```
balance = sum(credits) - sum(debits)
```

---

### 2. Concurrency Safety (Row Locking)

* Uses `SELECT FOR UPDATE` to lock merchant rows
* Prevents double-spend during simultaneous payout requests

---

### 3. Idempotent API

* Supports `Idempotency-Key` header
* Same request returns the same response
* Enforced using database-level unique constraint

---

### 4. State Machine

Payout lifecycle:

```
pending → processing → completed
pending → processing → failed
```

Invalid transitions are prevented.

---

### 5. Async Processing (Celery + Redis)

* Payout processing handled in background
* Simulated bank behavior:

  * 70% success
  * 20% failure
  * 10% retry (hang)

---

### 6. Retry & Failure Handling

* Retries up to 3 times
* Failed payouts trigger **automatic refund**
* Refund is recorded as a credit entry (ledger-safe)

---

## 🏗️ Architecture

```
Client (Postman / React)
        ↓
Django API (DRF)
        ↓
PostgreSQL (Transactions + Locking)
        ↓
Redis (Queue)
        ↓
Celery Worker
        ↓
Database Updates (Payout Status + Ledger)
```

---

## ⚙️ Tech Stack

* **Backend:** Django, Django REST Framework
* **Database:** PostgreSQL
* **Queue:** Redis
* **Worker:** Celery
* **Language:** Python

---

## 📦 Setup Instructions

### 1. Clone repo

```
git clone https://github.com/your-username/playto-payout-engine.git
cd playto-payout-engine/backend
```

---

### 2. Create virtual environment

```
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install dependencies

```
pip install -r requirements.txt
```

---

### 4. Setup PostgreSQL

Update `settings.py`:

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'playto_db',
        'USER': 'playto_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5433',
    }
}
```

---

### 5. Run migrations

```
python manage.py migrate
```

---

### 6. Run Redis

```
sudo service redis-server start
```

---

### 7. Start Celery worker

```
celery -A config worker -l info
```

---

### 8. Run Django server

```
python manage.py runserver
```

---

## 🧪 API Testing

### Create Payout

**POST** `/api/v1/payouts/`

Headers:

```
Idempotency-Key: test123
```

Body:

```json
{
  "merchant_id": 1,
  "amount_paise": 2000
}
```

---

### Expected Behavior

* First request → creates payout
* Second request (same key) → returns same payout
* No duplicate entries

---

## 💡 Important Design Decisions

* All amounts stored as integers (paise) → avoids float errors
* Ledger is append-only → ensures auditability
* Refunds use compensating entries → no mutation of history
* Database enforces correctness → not application logic

---

## 📌 What This Demonstrates

This project focuses on:

* Handling money safely under concurrency
* Designing idempotent APIs
* Using database primitives for correctness
* Building async systems with retries
* Thinking like a production backend engineer

---

## 🚀 Future Improvements

* Frontend dashboard (React)
* Webhook system for payout updates
* Audit logs
* Docker setup
* Monitoring & alerting

---

## 👤 Author

Shrinath Sharma
Full Stack Developer | Embedded Systems | STEM Trainer

---

## 📄 Notes

This implementation prioritizes **correctness, reliability, and real-world system design** over UI or feature completeness.
