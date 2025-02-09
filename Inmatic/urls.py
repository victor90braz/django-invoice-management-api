from django.urls import path
from InvoicesAccounting.views.invoice_view import InvoiceView

urlpatterns = [
    path("invoices/list/", InvoiceView.as_view(), name="invoice-list"),
    path("invoices/get/<int:invoice_id>/", InvoiceView.as_view(), name="invoice-get"),
    path("invoices/create/", InvoiceView.as_view(), name="invoice-create"),
    path("invoices/update/<int:invoice_id>/", InvoiceView.as_view(), name="invoice-update"),
    path("invoices/delete/<int:invoice_id>/", InvoiceView.as_view(), name="invoice-delete"),
    path("invoices/filter/", InvoiceView.as_view(), name="invoice-filter"),
]
