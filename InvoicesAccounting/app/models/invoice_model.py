from django.db import models
from InvoicesAccounting.app.enums.invoice_states import InvoiceStates
from django.core.exceptions import ValidationError
from datetime import date 

class InvoiceModel(models.Model):
    provider = models.CharField(max_length=255)
    concept = models.TextField()
    base_value = models.DecimalField(max_digits=10, decimal_places=2)
    vat = models.DecimalField(max_digits=10, decimal_places=2)
    total_value = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(null=False, blank=False, default=date.today)  
    
    state = models.CharField(
        max_length=20,
        choices=InvoiceStates.choices,  
        default=InvoiceStates.DRAFT.value,  
    )

    def clean(self):
        
        super().clean()  

        errors = {}

        if self.base_value <= 0:
            errors["base_value"] = "Base value must be greater than zero."

        if self.vat < 0:
            errors["vat"] = "VAT cannot be negative."

        if self.total_value <= 0:
            errors["total_value"] = "Total value must be greater than zero."

        expected_total = self.base_value + self.vat
        if self.total_value != expected_total:
            errors["total_value"] = f"Total value must be {expected_total}."

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"Invoice {self.pk or 'New'} - {self.provider} ({self.state})"
