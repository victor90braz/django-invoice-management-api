import json
import logging
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.dateparse import parse_date
from InvoicesAccounting.app.enums.accounting_codes import AccountingCodes
from InvoicesAccounting.app.enums.invoice_states import InvoiceStates
from InvoicesAccounting.app.models.invoice_model import InvoiceModel
from InvoicesAccounting.app.services.invoice_service import InvoiceService
from InvoicesAccounting.app.validators.validate_invoice import ValidateInvoice

logger = logging.getLogger(__name__)

# Swagger Parameters
invoice_id_param = openapi.Parameter(
    'invoice_id', in_=openapi.IN_PATH, description="Invoice ID", type=openapi.TYPE_INTEGER
)

state_param = openapi.Parameter(
    'state', in_=openapi.IN_QUERY, description="Filter by invoice state", type=openapi.TYPE_STRING
)

start_date_param = openapi.Parameter(
    'start_date', in_=openapi.IN_QUERY, description="Start date (YYYY-MM-DD)", type=openapi.TYPE_STRING
)

end_date_param = openapi.Parameter(
    'end_date', in_=openapi.IN_QUERY, description="End date (YYYY-MM-DD)", type=openapi.TYPE_STRING
)

@swagger_auto_schema(method='get', responses={200: "List of invoices"})
@api_view(['GET'])
@permission_classes([AllowAny])
def list_invoices(request):
    try:
        invoices = list(InvoiceModel.objects.all().values())

        if not invoices:
            invoices = InvoiceService().list_invoices()

        return JsonResponse(invoices, safe=False)

    except Exception as e:
        logger.error(f"Error listing invoices: {str(e)}")
        return JsonResponse({"error": "An error occurred while listing invoices."}, status=500)

@swagger_auto_schema(method='get', manual_parameters=[invoice_id_param], responses={200: "Invoice details"})
@api_view(['GET'])
@permission_classes([AllowAny])
def get_invoice_detail(request, invoice_id):
    try:
        data = InvoiceService().get_invoice(invoice_id)
        return JsonResponse(data) if data else JsonResponse({"error": "Invoice not found"}, status=404)

    except Exception as e:
        logger.error(f"Error retrieving invoice: {str(e)}")
        return JsonResponse({"error": "An error occurred while retrieving the invoice."}, status=500)

@swagger_auto_schema(method='post', request_body=ValidateInvoice, responses={201: "Invoice Created"})
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_invoice(request):
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

@swagger_auto_schema(method='put', manual_parameters=[invoice_id_param], request_body=ValidateInvoice, responses={200: "Invoice Updated"})
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_invoice(request, invoice_id):
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

@swagger_auto_schema(method='delete', manual_parameters=[invoice_id_param], responses={200: "Invoice Deleted"})
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_invoice(request, invoice_id):
    try:
        result = InvoiceService().delete_invoice(invoice_id)
        return JsonResponse({"message": "Invoice deleted successfully"}) if result else JsonResponse({"error": "Invoice not found"}, status=404)

    except Exception as e:
        logger.error(f"Error deleting invoice: {str(e)}")
        return JsonResponse({"error": "An error occurred while deleting the invoice."}, status=500)

@swagger_auto_schema(method='get', manual_parameters=[state_param, start_date_param, end_date_param], responses={200: "Filtered invoices"})
@api_view(['GET'])
@permission_classes([AllowAny])
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

@swagger_auto_schema(method='get', manual_parameters=[invoice_id_param], responses={200: "Accounting entries"})
@api_view(['GET'])
@permission_classes([AllowAny])
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
