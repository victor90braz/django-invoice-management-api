from rest_framework.views import APIView
from rest_framework.response import Response
from InvoicesAccounting.services.invoice_service import InvoiceService

class InvoiceView(APIView):
    # Get all invoices or a specific one by ID
    def get(self, request, invoice_id=None):
        if invoice_id:
            data = InvoiceService().find_by_id(invoice_id)
        else:
            data = InvoiceService().find_all()
        return Response(data)

    # Create a new invoice
    def post(self, request):
        return Response(InvoiceService().create(request.data), status=201)

    # Update an existing invoice
    def put(self, request, invoice_id):
        return Response(InvoiceService().update(invoice_id, request.data))

    # Delete an invoice
    def delete(self, request, invoice_id):
        return Response(InvoiceService().delete(invoice_id))
