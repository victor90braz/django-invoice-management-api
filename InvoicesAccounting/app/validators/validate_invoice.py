from rest_framework import serializers
from InvoicesAccounting.app.models.invoice_model import InvoiceModel

class ValidateInvoice(serializers.ModelSerializer):

    class Meta:
        model = InvoiceModel
        fields = [field.name for field in InvoiceModel._meta.fields] 

    def validate(self, data):
        invoice = InvoiceModel(**data)  
        invoice.clean() 
        return data
