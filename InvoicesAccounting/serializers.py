from rest_framework import serializers
from InvoicesAccounting.models import Invoice

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'provider', 'concept', 'base_value', 'vat', 'total_value', 'date', 'state']
