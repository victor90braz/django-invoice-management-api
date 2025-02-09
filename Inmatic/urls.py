from django.urls import path

from InvoicesAccounting.views.accounting_entries_view import AccountingEntriesView
from InvoicesAccounting.views.invoice_view import InvoiceView

urlpatterns = [
    path('invoices/', InvoiceView.as_view(), name='invoice-list'),
    path('invoices/<int:invoice_id>/', InvoiceView.as_view(), name='invoice-detail'),
    path('invoices/<int:invoice_id>/accounting-entries/', AccountingEntriesView.as_view(), name='invoice-accounting'),
]
