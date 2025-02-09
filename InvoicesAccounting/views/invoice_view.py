from rest_framework.views import APIView
from rest_framework.response import Response
from InvoicesAccounting.services.invoice_service import InvoiceService

class InvoiceView(APIView):
    def get(self, request, invoice_id=None):
        if invoice_id:
            data = InvoiceService().get_invoice(invoice_id)
        else:
            data = InvoiceService().get_all_invoices()
        return Response(data)

    def post(self, request):
        return Response(InvoiceService().create_invoice(request.data), status=201)

    def put(self, request, invoice_id):
        return Response(InvoiceService().update_invoice(invoice_id, request.data))

    def delete(self, request, invoice_id):
        return Response(InvoiceService().delete_invoice(invoice_id))
