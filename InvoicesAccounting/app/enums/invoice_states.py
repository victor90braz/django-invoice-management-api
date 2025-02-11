from django.db import models

class InvoiceStates(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    ACCOUNTED = "ACCOUNTED", "Accounted"
    PAID = "PAID", "Paid"
    CANCELED = "CANCELED", "Canceled"
    PENDING = "PENDING", "Pending"
