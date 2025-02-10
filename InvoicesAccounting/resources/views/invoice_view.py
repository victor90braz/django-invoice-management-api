import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from InvoicesAccounting.app.services.invoice_service import InvoiceService
from InvoicesAccounting.app.http.requests.validate_invoice import ValidateInvoice

logger = logging.getLogger(__name__)

@csrf_exempt
def list_invoices(request):
    """
    List all invoices.
    """
    try:
        data = InvoiceService().list_invoices()
        return JsonResponse(data, safe=False)
    except Exception as e:
        logger.error(f"Error listing invoices: {str(e)}")
        return JsonResponse({"error": "An error occurred while listing invoices."}, status=500)

@csrf_exempt
def retrieve_invoice(request, invoice_id):
    """
    Retrieve a specific invoice by ID.
    """
    try:
        data = InvoiceService().get_invoice(invoice_id)
        return JsonResponse(data) if data else JsonResponse({"error": "Invoice not found"}, status=404)
    except Exception as e:
        logger.error(f"Error retrieving invoice: {str(e)}")
        return JsonResponse({"error": "An error occurred while retrieving the invoice."}, status=500)

@csrf_exempt
def create_invoice(request):
    """
    Create a new invoice.
    """
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
    """
    Update an existing invoice.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    try:
        data = json.loads(request.body)
        serializer = ValidateInvoice(data=data, partial=True)  # `partial=True` permite actualizaciones parciales
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
    """
    Delete an invoice by ID.
    """
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
    """
    Filter invoices based on query parameters.
    """
    try:
        filters = request.GET.dict()
        filtered_data = InvoiceService().filter_invoices(**filters)
        return JsonResponse(filtered_data, safe=False)
    except Exception as e:
        logger.error(f"Error filtering invoices: {str(e)}")
        return JsonResponse({"error": "An error occurred while filtering invoices."}, status=500)

@csrf_exempt
def generate_accounting_entries(request, invoice_id):
    """
    Generate accounting entries for a specific invoice.
    """
    try:
        accounting_data = InvoiceService().generate_accounting_entries(invoice_id)
        return JsonResponse(accounting_data) if accounting_data else JsonResponse({"error": "Invoice not found"}, status=404)
    except Exception as e:
        logger.error(f"Error generating accounting entries: {str(e)}")
        return JsonResponse({"error": "An error occurred while generating accounting entries."}, status=500)
