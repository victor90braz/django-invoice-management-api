from django.db import models

class AccountingCodes(models.TextChoices):
    PURCHASES = "6000", "Purchases (DEBIT)"
    VAT_SUPPORTED = "4720", "VAT Supported (DEBIT)"
    SUPPLIERS = "4000", "Suppliers (CREDIT)"
