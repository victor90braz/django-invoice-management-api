from django.db import models
from InvoicesAccounting.app.enums.invoice_states import InvoiceStates
from django.core.exceptions import ValidationError

class InvoiceModel(models.Model):
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

    def clean(self):
        """ Validación de reglas de negocio antes de guardar el modelo """
        if self.base_value <= 0:
            raise ValidationError({"base_value": "Base value must be greater than zero."})

        if self.vat < 0:
            raise ValidationError({"vat": "VAT cannot be negative."})

        if self.total_value <= 0:
            raise ValidationError({"total_value": "Total value must be greater than zero."})

        if self.total_value != self.base_value + self.vat:
            raise ValidationError({"total_value": "Total value must be the sum of base value and VAT."})

    def __str__(self):
        return f"Invoice {self.id} - {self.provider} ({self.state})"
