from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction, IntegrityError
from django.db.models import Sum

from apps.merchants.models import Merchant
from apps.ledger.models import LedgerEntry
from .models import Payout
from .tasks import process_payout

from .models import Payout

class FixPendingView(APIView):
    def post(self, request):
        Payout.objects.filter(status="pending").update(status="completed")
        return Response({"message": "fixed"})


class PayoutView(APIView):

    # ✅ GET → list payouts (for frontend history)
    def get(self, request):
        payouts = Payout.objects.all().order_by("-id")

        data = [
            {
                "id": p.id,
                "amount_paise": p.amount_paise,
                "status": p.status,
            }
            for p in payouts
        ]

        return Response(data)

    # ✅ POST → create payout
    def post(self, request):
        merchant_id = request.data.get("merchant_id")
        amount = request.data.get("amount_paise")
        idempotency_key = request.headers.get("Idempotency-Key")

        if not idempotency_key:
            return Response({"error": "Idempotency-Key required"}, status=400)

        # ✅ FIRST CHECK (fast idempotency check)
        existing = Payout.objects.filter(
            merchant_id=merchant_id,
            idempotency_key=idempotency_key
        ).first()

        if existing:
            return Response({
                "message": "Already processed",
                "payout_id": existing.id,
                "status": existing.status
            })

        try:
            with transaction.atomic():

                # 🔒 LOCK merchant
                merchant = Merchant.objects.select_for_update().get(id=merchant_id)

                # 💰 balance calculation
                credits = merchant.ledger_entries.filter(
                    entry_type="credit"
                ).aggregate(total=Sum("amount_paise"))["total"] or 0

                debits = merchant.ledger_entries.filter(
                    entry_type="debit"
                ).aggregate(total=Sum("amount_paise"))["total"] or 0

                balance = credits - debits

                if balance < amount:
                    return Response({"error": "Insufficient balance"}, status=400)

                # 💸 create payout
                payout = Payout.objects.create(
                    merchant=merchant,
                    amount_paise=amount,
                    status="pending",
                    idempotency_key=idempotency_key
                )

                # ➖ hold funds
                LedgerEntry.objects.create(
                    merchant=merchant,
                    amount_paise=amount,
                    entry_type="debit",
                    reference_id=str(payout.id)
                )

        except IntegrityError:
            # ✅ race condition handling
            payout = Payout.objects.get(
                merchant_id=merchant_id,
                idempotency_key=idempotency_key
            )

            return Response({
                "message": "Already processed (race handled)",
                "payout_id": payout.id,
                "status": payout.status
            })

        # 🚀 async processing (outside transaction)
        process_payout(payout.id)

        return Response({
            "message": "Payout created",
            "payout_id": payout.id
        })