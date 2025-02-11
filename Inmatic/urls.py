from django.urls import path
from InvoicesAccounting.resources.views.invoice_view import (
    list_invoices,
    get_invoice_detail,
    create_invoice,
    update_invoice,
    delete_invoice,
    filter_invoices,
    generate_accounting_entries,
)

urlpatterns = [
    # Get all invoices
    path("invoices/", list_invoices, name="invoice-list"),
    
    # Get an invoice detail by ID
    path("invoices/<int:invoice_id>/", get_invoice_detail, name="invoice-detail"),
    
    # Create a new invoice
    path("invoices/create/", create_invoice, name="invoice-create"),
    
    # Update an existing invoice by ID
    path("invoices/<int:invoice_id>/update/", update_invoice, name="invoice-update"),
    
    # Delete an existing invoice by ID
    path("invoices/<int:invoice_id>/delete/", delete_invoice, name="invoice-delete"),
    
    # Filter invoices by state and date
    path("invoices/filter/", filter_invoices, name="invoice-filter"),
    
    # Generate accounting entries for a specific invoice
    path("invoices/<int:invoice_id>/accounting-entries/", generate_accounting_entries, name="invoice-accounting-entries"),
]