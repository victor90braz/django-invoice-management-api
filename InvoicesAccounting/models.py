from django.db import models
from InvoicesAccounting.enum.invoice_states import InvoiceStates  

class Invoice(models.Model):
    provider = models.CharField(max_length=255)
    concept = models.TextField()
    base_value = models.DecimalField(max_digits=10, decimal_places=2)
    vat = models.DecimalField(max_digits=10, decimal_places=2)
    total_value = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    state = models.CharField(
        max_length=20,
        choices=[(state.value, state.name.capitalize()) for state in InvoiceStates],  
        default=InvoiceStates.DRAFT.value,  
    )

    def __str__(self):
        return f"Invoice {self.id} - {self.provider} ({self.state})"
