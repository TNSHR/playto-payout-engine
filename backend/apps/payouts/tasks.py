from celery import shared_task
from .models import Payout
from apps.ledger.models import LedgerEntry
import random
import time
from celery import shared_task


@shared_task
def process_payout(payout_id):
    payout = Payout.objects.get(id=payout_id)

    time.sleep(2)
     

    if random.choice([True, False]):
        payout.status = "completed"
    else:
        payout.status = "failed"

        # 🔥 REFUND MONEY
        LedgerEntry.objects.create(
            merchant=payout.merchant,
            amount_paise=payout.amount_paise,
            entry_type="credit",
            reference_id=str(payout.id)
        )

    payout.save()
