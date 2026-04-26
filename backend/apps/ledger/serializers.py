from rest_framework import serializers

class BalanceSerializer(serializers.Serializer):
    merchant_id = serializers.IntegerField()
    balance_paise = serializers.IntegerField()