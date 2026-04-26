from django.db import models

class LedgerEntry(models.Model):
    CREDIT = 'credit'
    DEBIT = 'debit'

    ENTRY_TYPE = [
        (CREDIT, 'Credit'),
        (DEBIT, 'Debit'),
    ]

    merchant = models.ForeignKey('merchants.Merchant', 
                                 on_delete=models.CASCADE,
                                 related_name = 'ledger_entries'
                                    )
    amount_paise = models.BigIntegerField()
    entry_type = models.CharField(max_length=10,choices=ENTRY_TYPE)
    reference_id = models.CharField(max_length=255,null=True, blank=True)
