import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from InvoicesAccounting.app.enums.accounting_codes import AccountingCodes
from InvoicesAccounting.app.enums.invoice_states import InvoiceStates
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
        filters = {}

        state = request.GET.get("state")
        if state and state not in InvoiceStates.values:
            return JsonResponse({"error": "Invalid state filter. Allowed values: " + ", ".join(InvoiceStates.values)}, status=400)

        if state:
            filters["state"] = state

        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        if start_date and end_date:
            start_date = parse_date(start_date)
            end_date = parse_date(end_date)

            if start_date and end_date:
                filters["date__range"] = (start_date, end_date)

        filtered_data = InvoiceService().filter_invoices(**filters)

        return JsonResponse(filtered_data, safe=False)

    except Exception as e:
        logger.error(f"Error filtering invoices: {str(e)}")
        return JsonResponse({"error": "An error occurred while filtering invoices."}, status=500)

@csrf_exempt
def generate_accounting_entries(request, invoice_id):
    try:
        invoice = InvoiceModel.objects.filter(id=invoice_id).first()

        if invoice:
            return JsonResponse({
                "entries": [
                    {"account": AccountingCodes.PURCHASES.value, "description": AccountingCodes.PURCHASES.label, "amount": float(invoice.base_value)},
                    {"account": AccountingCodes.VAT_SUPPORTED.value, "description": AccountingCodes.VAT_SUPPORTED.label, "amount": float(invoice.vat)},
                    {"account": AccountingCodes.SUPPLIERS.value, "description": AccountingCodes.SUPPLIERS.label, "amount": float(invoice.total_value)}
                ]
            })

        accounting_entries = InvoiceService().generate_accounting_entries(invoice_id)

        if not accounting_entries.get("entries"):  
            return JsonResponse({"error": "Invoice not found"}, status=404)

        return JsonResponse(accounting_entries)

    except Exception as e:
        logger.error(f"Error generating accounting entries: {str(e)}")
        return JsonResponse({"error": "An error occurred while generating accounting entries."}, status=500)

