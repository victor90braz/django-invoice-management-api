from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from InvoicesAccounting.services.invoice_service import InvoiceService
from django.core.exceptions import ValidationError

class AccountingEntriesView(APIView):
    def get(self, request, invoice_id):
        try:
            entries = InvoiceService().generate_accounting_entries(invoice_id)
            return Response(entries, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
