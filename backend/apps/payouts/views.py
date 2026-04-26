from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction, IntegrityError
from django.db.models import Sum

from apps.merchants.models import Merchant
from apps.ledger.models import LedgerEntry
from .models import Payout
from .tasks import process_payout


class PayoutView(APIView):

    def post(self, request):
        merchant_id = request.data.get("merchant_id")
        amount = request.data.get("amount_paise")

        idempotency_key = request.headers.get("Idempotency-Key")

        if not idempotency_key:
            return Response({"error": "Idempotency-Key required"}, status=400)

        try:
            with transaction.atomic():

                # 🔒 LOCK merchant
                merchant = Merchant.objects.select_for_update().get(id=merchant_id)

                # 💰 balance
                credits = merchant.ledger_entries.filter(
                    entry_type="credit"
                ).aggregate(total=Sum("amount_paise"))["total"] or 0

                debits = merchant.ledger_entries.filter(
                    entry_type="debit"
                ).aggregate(total=Sum("amount_paise"))["total"] or 0

                balance = credits - debits

                if balance < amount:
                    return Response({"error": "Insufficient balance"}, status=400)

                # 💸 Try create payout
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
            # ✅ NEW TRANSACTION (safe)
            payout = Payout.objects.get(
                merchant_id=merchant_id,
                idempotency_key=idempotency_key
            )

            return Response({
                "message": "Already processed",
                "payout_id": payout.id,
                "status": payout.status
            })

        # 🚀 trigger worker OUTSIDE transaction
        process_payout.delay(payout.id)

        return Response({
            "message": "Payout created",
            "payout_id": payout.id
        })