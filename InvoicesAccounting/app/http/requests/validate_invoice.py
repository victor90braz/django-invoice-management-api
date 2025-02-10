from rest_framework import serializers
from decimal import Decimal

from InvoicesAccounting.app.enums.invoice_states import InvoiceStates
from InvoicesAccounting.app.models.invoice_model import InvoiceModel

class ValidateInvoice(serializers.ModelSerializer):
    base_value = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    vat = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    total_value = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)

    class Meta:
        model = InvoiceModel
        fields = ['provider', 'concept', 'base_value', 'vat', 'total_value', 'date', 'state']

    # Validate invoice state
    def validate_state(self, value):
        valid_states = [state.value for state in InvoiceStates]
        if value not in valid_states:
            raise serializers.ValidationError(f"Invalid invoice state. Allowed values: {valid_states}")
        return value

    # Validate that base_value, vat, and total_value are positive numbers
    def validate(self, data):
        if data.get("base_value", 0) <= 0:
            raise serializers.ValidationError({"base_value": "Base value must be greater than zero."})

        if data.get("vat", 0) < 0:
            raise serializers.ValidationError({"vat": "VAT cannot be negative."})

        if data.get("total_value", 0) <= 0:
            raise serializers.ValidationError({"total_value": "Total value must be greater than zero."})

        return data