from django.urls import path
from drf_yasg.views import get_schema_view
from .config.api_config import SWAGGER_SCHEMA_CONFIG 

from InvoicesAccounting.resources.views.invoice_view import (
    list_invoices,
    get_invoice_detail,
    create_invoice,
    update_invoice,
    delete_invoice,
    filter_invoices,
    generate_accounting_entries,
)

schema_view = get_schema_view(
    SWAGGER_SCHEMA_CONFIG,
    public=True,
)

urlpatterns = [
    path("invoices/", list_invoices, name="invoice-list"),
    path("invoices/<int:invoice_id>/", get_invoice_detail, name="invoice-detail"),
    path("invoices/create/", create_invoice, name="invoice-create"),
    path("invoices/<int:invoice_id>/update/", update_invoice, name="invoice-update"),
    path("invoices/<int:invoice_id>/delete/", delete_invoice, name="invoice-delete"),
    path("invoices/filter/", filter_invoices, name="invoice-filter"),
    path("invoices/<int:invoice_id>/accounting-entries/", generate_accounting_entries, name="invoice-accounting-entries"),
    
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]