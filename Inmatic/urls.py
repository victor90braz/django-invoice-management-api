from django.urls import path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from InvoicesAccounting.resources.views.invoice_view import (
    list_invoices,
    get_invoice_detail,
    create_invoice,
    update_invoice,
    delete_invoice,
    filter_invoices,
    generate_accounting_entries,
)

# ✅ OpenAPI Schema Generation
schema_view = get_schema_view(
    openapi.Info(
        title="Invoices API",
        default_version='v1',
        description="API for managing invoices",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="victor.90braz@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
)

urlpatterns = [
    # ✅ Invoice-related endpoints
    path("invoices/", list_invoices, name="invoice-list"),
    path("invoices/<int:invoice_id>/", get_invoice_detail, name="invoice-detail"),
    path("invoices/create/", create_invoice, name="invoice-create"),
    path("invoices/<int:invoice_id>/update/", update_invoice, name="invoice-update"),
    path("invoices/<int:invoice_id>/delete/", delete_invoice, name="invoice-delete"),
    path("invoices/filter/", filter_invoices, name="invoice-filter"),
    path("invoices/<int:invoice_id>/accounting-entries/", generate_accounting_entries, name="invoice-accounting-entries"),
    
    # ✅ Swagger & OpenAPI
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
