from django.core.exceptions import ValidationError  
from rest_framework import serializers
from InvoicesAccounting.app.models.invoice_model import InvoiceModel

class ValidateInvoice(serializers.ModelSerializer):

    class Meta:
        model = InvoiceModel
        fields = [field.name for field in InvoiceModel._meta.fields] 

    def validate(self, data):

        if 'date' not in data or not data['date']:
            raise serializers.ValidationError({'date': 'This field is required.'})
        
        if 'vat' not in data or not data['vat']:
            raise serializers.ValidationError({'vat': 'This field is required.'})
        
        if 'base_value' not in data or not data['base_value']:
            raise serializers.ValidationError({'base_value': 'This field is required.'})
        
        if 'total_value' not in data or not data['total_value']:
            raise serializers.ValidationError({'total_value': 'This field is required.'})

        invoice = InvoiceModel(**data)
        
        try:
            invoice.clean()  
        except ValidationError as error:
            raise serializers.ValidationError(error.message_dict)

        return data
