import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from Inmatic import settings
from InvoicesAccounting.app.services.invoice_service import InvoiceService
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
        return JsonResponse({"error": f"An error occurred while listing invoices: {str(e)}"}, status=500)

@csrf_exempt
def retrieve_invoice(request, invoice_id):
    """
    Retrieve a specific invoice by ID.
    """
    try:
        data = InvoiceService().get_invoice(invoice_id)
        if not data:
            return JsonResponse({"error": "Invoice not found"}, status=404)
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred while retrieving the invoice: {str(e)}"}, status=500)

@csrf_exempt
def create_invoice(request):
    """
    Create a new invoice.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    try:
        body = json.loads(request.body)
        
        required_fields = ["provider", "concept", "base_value", "vat", "total_value", "date", "state"]
        if not all(field in body for field in required_fields):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        created_invoice = InvoiceService().create_invoice(body)
        return JsonResponse(created_invoice, status=201)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred while creating the invoice: {str(e)}"}, status=500)

@csrf_exempt
def update_invoice(request, invoice_id):
    """
    Update an existing invoice.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    try:
        body = json.loads(request.body)
        
        required_fields = ["provider", "concept", "base_value", "vat", "total_value", "date", "state"]
        if not all(field in body for field in required_fields):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        updated_invoice = InvoiceService().update_invoice(invoice_id, body)
        if not updated_invoice:
            return JsonResponse({"error": "Invoice not found"}, status=404)
        return JsonResponse(updated_invoice)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred while updating the invoice: {str(e)}"}, status=500)

@csrf_exempt
def delete_invoice(request, invoice_id):
    """
    Delete an invoice by ID.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    try:
        result = InvoiceService().delete_invoice(invoice_id)
        if not result:
            return JsonResponse({"error": "Invoice not found"}, status=404)
        return JsonResponse({"message": "Invoice deleted successfully"})
    except Exception as e:
        return JsonResponse({"error": f"An error occurred while deleting the invoice: {str(e)}"}, status=500)

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
        return JsonResponse({"error": f"An error occurred while filtering invoices: {str(e)}"}, status=500)

@csrf_exempt
def generate_accounting_entries(request, invoice_id):
    """
    Generate accounting entries for a specific invoice.
    """
    try:
        accounting_data = InvoiceService().generate_accounting_entries(invoice_id)
        if not accounting_data:
            return JsonResponse({"error": "Invoice not found"}, status=404)
        return JsonResponse(accounting_data)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred while generating accounting entries: {str(e)}"}, status=500)
