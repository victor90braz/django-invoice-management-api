from datetime import date
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from InvoicesAccounting.enum.accounting_codes import AccountingCodes
from InvoicesAccounting.models import Invoice
from InvoicesAccounting.enum.invoice_states import InvoiceStates
from InvoicesAccounting.serializers import InvoiceSerializer

class InvoiceService:
    def create_invoice(self, data: dict):
        if "state" in data and data["state"] not in [state.value for state in InvoiceStates]:
            raise ValidationError("Invalid invoice state")

        invoice = Invoice.objects.create(
            provider=data["provider"],
            concept=data["concept"],
            base_value=data["base_value"],
            vat=data["vat"],
            total_value=data["total_value"],
            date=data["date"],
            state=data["state"],
        )
        return InvoiceSerializer(invoice).data

    def get_invoice(self, invoice_id: int):
        invoice = self._get_or_fail(Invoice, invoice_id)
        return InvoiceSerializer(invoice).data

    def update_invoice(self, invoice_id: int, data: dict):
        invoice = self._get_or_fail(Invoice, invoice_id)

        if "state" in data and data["state"] not in [state.value for state in InvoiceStates]:
            raise ValidationError("Invalid invoice state")

        for field, value in data.items():
            setattr(invoice, field, value)
        invoice.save()

        return InvoiceSerializer(invoice).data

    def delete_invoice(self, invoice_id: int):
        invoice = self._get_or_fail(Invoice, invoice_id)
        invoice.delete()
        return {"message": f"Invoice {invoice_id} deleted successfully"}

    def generate_accounting_entries(self, invoice_id: int):
        invoice = self._get_or_fail(Invoice, invoice_id)

        if invoice.state != InvoiceStates.PAID.value:
            raise ValidationError("Accounting entries can only be generated for invoices in the PAID state.")

        return {
            "DEBE": [
                {"account": AccountingCodes.PURCHASES.value, "amount": float(invoice.base_value)},
                {"account": AccountingCodes.VAT_SUPPORTED.value, "amount": float(invoice.vat)},
            ],
            "HABER": [
                {"account": AccountingCodes.SUPPLIERS.value, "amount": float(invoice.total_value)},
            ],
        }

    def get_all_invoices(self, state: str = None, start_date: date = None, end_date: date = None):
        queryset = Invoice.objects.all()

        if state:
            queryset = queryset.filter(state=state)

        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])

        return InvoiceSerializer(queryset, many=True).data

    def _get_or_fail(self, model, id: int):
        try:
            return model.objects.get(id=id)
        except ObjectDoesNotExist:
            raise ValidationError(f"{model.__name__} with id {id} does not exist")
