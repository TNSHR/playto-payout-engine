from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum

from apps.merchants.models import Merchant
from apps.ledger.models import LedgerEntry
from .serializers import BalanceSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.merchants.models import Merchant
from apps.ledger.models import LedgerEntry


class SeedBalanceView(APIView):
    def post(self, request):
        m = Merchant.objects.first()

        if not m:
            m = Merchant.objects.create(name="Default Merchant")

        # only add if no balance exists
        if not m.ledger_entries.exists():
            LedgerEntry.objects.create(
                merchant=m,
                amount_paise=20000,
                entry_type="credit"
            )

        return Response({"message": "Seeded successfully"})


class BalanceView(APIView):
    def get(self, request, merchant_id):
        try:
            merchant = Merchant.objects.get(id=merchant_id)
        except Merchant.DoesNotExist:
            return Response({"error": "Merchant not found"}, status=404)

        credits = merchant.ledger_entries.filter(
            entry_type="credit"
        ).aggregate(total=Sum("amount_paise"))["total"] or 0

        debits = merchant.ledger_entries.filter(
            entry_type="debit"
        ).aggregate(total=Sum("amount_paise"))["total"] or 0

        balance = credits - debits

        data = {
            "merchant_id": merchant.id,
            "balance_paise": balance
        }

        serializer = BalanceSerializer(data)
        return Response(serializer.data)