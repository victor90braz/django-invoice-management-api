from typing import List, Dict
import httpx
from Inmatic import settings
from InvoicesAccounting.app.models.invoice_model import InvoiceModel
from django.db import transaction

from InvoicesAccounting.app.validators.validate_invoice import ValidateInvoice


class InvoiceService:
    BASE_URL = settings.PAYMENT_API_BASE_URL

    def __init__(self, base_url=None):
        self.base_url = base_url or self.BASE_URL

        if not self.base_url:
            raise ValueError("BASE_URL is not configured. Please check your settings.")

        self.client = httpx.Client(base_url=self.base_url, timeout=30)

    def list_invoices(self) -> List[Dict]:
        response = self.client.get("invoices/")
        response.raise_for_status()

        invoices = response.json()

        serializer = ValidateInvoice(data=invoices, many=True)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            for invoice_data in serializer.validated_data:
                InvoiceModel.objects.update_or_create(
                    id=invoice_data.get("id"),
                    defaults=invoice_data,
                )

        return serializer.data

    def create_invoice(self, invoice: InvoiceModel) -> dict:
        serializer = ValidateInvoice(instance=invoice)

        response = self.client.post("invoices/", json=serializer.data)
        response.raise_for_status()

        return response.json()

    def get_invoice(self, invoice_id: int) -> Dict:
        response = self.client.get(f"invoices/{invoice_id}/")
        response.raise_for_status()

        return response.json()

    def update_invoice(self, invoice_id: int, data: Dict) -> Dict:
        response = self.client.put(f"invoices/{invoice_id}/", json=data)
        response.raise_for_status()

        return response.json()

    def delete_invoice(self, invoice_id: int) -> Dict:
        response = self.client.delete(f"invoices/{invoice_id}/")
        response.raise_for_status()

        return {"message": f"Invoice {invoice_id} deleted successfully"}

    def filter_invoices(self, **params) -> List[Dict]:
        response = self.client.get("invoices/filter/", params=params)
        response.raise_for_status()
        return response.json()

    def generate_accounting_entries(self, invoice_id: int) -> Dict:
        response = self.client.get(f"invoices/{invoice_id}/accounting-entries/")
        response.raise_for_status()

        external_entries = response.json()

        if isinstance(external_entries, list):
            entries = external_entries
        else:
            entries = external_entries.get("entries", []) 

        return {
            "entries": [
                {
                    "account": entry.get("account", ""),
                    "description": entry.get("description", ""),
                    "amount": float(entry.get("amount", 0))
                } for entry in entries
            ]
        }

