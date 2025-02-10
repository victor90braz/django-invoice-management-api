from django.db import models

class InvoiceStates(models.TextChoices):
    DRAFT = "draft", "Draft"
    ACCOUNTED = "accounted", "Accounted"
    PAID = "paid", "Paid"
    CANCELED = "canceled", "Canceled"
    PENDING = "pending", "Pending"
