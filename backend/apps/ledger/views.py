from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum

from apps.merchants.models import Merchant
from apps.ledger.models import LedgerEntry
from .serializers import BalanceSerializer


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