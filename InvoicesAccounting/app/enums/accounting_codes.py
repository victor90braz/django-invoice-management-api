from django.db import models

class AccountingCodes(models.TextChoices):
    PURCHASES = "6000", "Purchases (DEBE Compras)"
    VAT_SUPPORTED = "4720", "VAT Supported (DEBE IVA Soportado)"
    SUPPLIERS = "4000", "Suppliers (HABER Proveedores)"
