import random
from celery import shared_task
from django.db import transaction

from .models import Payout
from apps.ledger.models import LedgerEntry


@shared_task(bind=True, max_retries=3)
def process_payout(self, payout_id):
    try:
        payout = Payout.objects.get(id=payout_id)

        if payout.status != "pending":
            return

        payout.status = "processing"
        payout.save()

        # 🎲 simulate bank
        result = random.choices(
            ["success", "fail", "hang"],
            weights=[70, 20, 10]
        )[0]

        if result == "success":
            payout.status = "completed"
            payout.save()

        elif result == "fail":
            with transaction.atomic():
                payout.status = "failed"
                payout.save()

                # 🔁 return money
                LedgerEntry.objects.create(
                    merchant=payout.merchant,
                    amount_paise=payout.amount_paise,
                    entry_type="credit",
                    reference_id=str(payout.id)
                )

        else:
            # simulate stuck → retry
            raise Exception("Processing stuck")

    except Exception as e:
        raise self.retry(exc=e, countdown=5)