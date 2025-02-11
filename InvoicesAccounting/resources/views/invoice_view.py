import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from InvoicesAccounting.app.enums.accounting_codes import AccountingCodes
from InvoicesAccounting.app.models.invoice_model import InvoiceModel
from InvoicesAccounting.app.services.invoice_service import InvoiceService
from InvoicesAccounting.app.validators.validate_invoice import ValidateInvoice

logger = logging.getLogger(__name__)

@csrf_exempt
def list_invoices(request):
    try:
        invoices = list(InvoiceModel.objects.all().values())

        if not invoices:
            invoices = InvoiceService().list_invoices()

        return JsonResponse(invoices, safe=False)

    except Exception as e:
        logger.error(f"Error listing invoices: {str(e)}")
        return JsonResponse({"error": "An error occurred while listing invoices."}, status=500)


@csrf_exempt
def get_invoice_detail(request, invoice_id):
    try:
        data = InvoiceService().get_invoice(invoice_id)
        return JsonResponse(data) if data else JsonResponse({"error": "Invoice not found"}, status=404)

    except Exception as e:
        logger.error(f"Error retrieving invoice: {str(e)}")
        return JsonResponse({"error": "An error occurred while retrieving the invoice."}, status=500)


@csrf_exempt
def create_invoice(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    try:
        data = json.loads(request.body)
        serializer = ValidateInvoice(data=data)

        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)

        created_invoice = InvoiceService().create_invoice(serializer.validated_data)
        return JsonResponse(created_invoice, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    except Exception as e:
        logger.error(f"Error creating invoice: {str(e)}")
        return JsonResponse({"error": "An error occurred while creating the invoice."}, status=500)


@csrf_exempt
def update_invoice(request, invoice_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    try:
        data = json.loads(request.body)
        serializer = ValidateInvoice(data=data, partial=True)

        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)

        updated_invoice = InvoiceService().update_invoice(invoice_id, serializer.validated_data)
        return JsonResponse(updated_invoice) if updated_invoice else JsonResponse({"error": "Invoice not found"}, status=404)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    except Exception as e:
        logger.error(f"Error updating invoice: {str(e)}")
        return JsonResponse({"error": "An error occurred while updating the invoice."}, status=500)


@csrf_exempt
def delete_invoice(request, invoice_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    try:
        result = InvoiceService().delete_invoice(invoice_id)
        return JsonResponse({"message": "Invoice deleted successfully"}) if result else JsonResponse({"error": "Invoice not found"}, status=404)

    except Exception as e:
        logger.error(f"Error deleting invoice: {str(e)}")
        return JsonResponse({"error": "An error occurred while deleting the invoice."}, status=500)


@csrf_exempt
def filter_invoices(request):
    try:
        filters = request.GET.dict()
        filtered_data = InvoiceService().filter_invoices(**filters)
        return JsonResponse(filtered_data, safe=False)

    except Exception as e:
        logger.error(f"Error filtering invoices: {str(e)}")
        return JsonResponse({"error": "An error occurred while filtering invoices."}, status=500)

@csrf_exempt
def generate_accounting_entries(request, invoice_id):
    try:
        invoice = InvoiceModel.objects.filter(id=invoice_id).first()

        accounting_entries = {"entries": []}  

        if invoice:
            accounting_entries["entries"] = [
                {"account": AccountingCodes.PURCHASES.value, "description": AccountingCodes.PURCHASES.label, "amount": float(invoice.base_value)},
                {"account": AccountingCodes.VAT_SUPPORTED.value, "description": AccountingCodes.VAT_SUPPORTED.label, "amount": float(invoice.vat)},
                {"account": AccountingCodes.SUPPLIERS.value, "description": AccountingCodes.SUPPLIERS.label, "amount": float(invoice.total_value)}
            ]
        else:
            external_entries = InvoiceService().generate_accounting_entries(invoice_id)

            if not external_entries or "error" in external_entries: 
                return JsonResponse({"error": "Invoice not found"}, status=404)

            accounting_entries["entries"] = external_entries  

        return JsonResponse(accounting_entries)

    except Exception as e:
        logger.error(f"Error generating accounting entries: {str(e)}")
        return JsonResponse({"error": "An error occurred while generating accounting entries."}, status=500)


