import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from Inmatic import settings
from InvoicesAccounting.services.invoice_service import InvoiceService

@csrf_exempt
def list_invoices(request):
    data = InvoiceService(settings.PAYMENT_API_BASE_URL).list_invoices()
    return JsonResponse(data, safe=False)

@csrf_exempt
def retrieve_invoice(request, invoice_id):
    data = InvoiceService().get_invoice(invoice_id)
    return JsonResponse(data)

@csrf_exempt
def create_invoice(request):
    try:
        body = json.loads(request.body)
        created_invoice = InvoiceService().create_invoice(body)
        return JsonResponse(created_invoice, status=201)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

@csrf_exempt
def update_invoice(request, invoice_id):
    try:
        body = json.loads(request.body)
        updated_invoice = InvoiceService().update_invoice(invoice_id, body)
        return JsonResponse(updated_invoice)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

@csrf_exempt
def delete_invoice(request, invoice_id):
    result = InvoiceService().delete_invoice(invoice_id)
    return JsonResponse({"message": "Invoice deleted successfully"} if result else {"error": "Deletion failed"}, status=200)

@csrf_exempt
def filter_invoices(request):
    filters = request.GET.dict()
    filtered_data = InvoiceService().filter_invoices(**filters)
    return JsonResponse(filtered_data, safe=False)

@csrf_exempt
def generate_accounting_entries(request, invoice_id):
    accounting_data = InvoiceService().generate_accounting_entries(invoice_id)
    return JsonResponse(accounting_data)
