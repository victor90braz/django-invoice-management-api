from django.urls import path
from InvoicesAccounting.views.invoice_view import (
    list_invoices,
    retrieve_invoice,
    create_invoice,
    update_invoice,
    delete_invoice,
    filter_invoices,
    generate_accounting_entries,
)

urlpatterns = [
    path("invoices/list/", list_invoices, name="invoice-list"),
    path("invoice/<int:invoice_id>/", retrieve_invoice, name="invoice-get-id"),
    path("invoices/create/", create_invoice, name="invoice-create"),
    path("invoices/update/<int:invoice_id>/", update_invoice, name="invoice-update"),
    path("invoices/delete/<int:invoice_id>/", delete_invoice, name="invoice-delete"),
    path("invoices/filter/", filter_invoices, name="invoice-filter"),
    path("invoices/<int:invoice_id>/accounting-entries/", generate_accounting_entries, name="invoice-generate-accounting-entries"),
]

