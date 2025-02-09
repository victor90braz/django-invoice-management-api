from rest_framework.views import APIView
from InvoicesAccounting.services.invoice_service import InvoiceService

class InvoiceView(APIView):
    def get(self, request, invoice_id=None):
        return InvoiceService().get_invoice_by_id(invoice_id) if invoice_id else InvoiceService().filter_invoices()

    def post(self, request):
        return InvoiceService().create_invoice(request.data)

    def put(self, request, invoice_id):
        return InvoiceService().update_invoice(invoice_id, request.data)

    def delete(self, request, invoice_id):
        return InvoiceService().delete_invoice(invoice_id)
