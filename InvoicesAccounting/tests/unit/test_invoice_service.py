from unittest.mock import patch
from django.test import TestCase
from Inmatic import settings
from InvoicesAccounting.app.enum.accounting_codes import AccountingCodes
from InvoicesAccounting.app.enum.invoice_states import InvoiceStates
from InvoicesAccounting.app.services.invoice_service import InvoiceService
from InvoicesAccounting.models import Invoice

class InvoiceServiceTest(TestCase):

    def setUp(self):
        self.service = InvoiceService(base_url=settings.PAYMENT_API_BASE_URL)

    @patch("httpx.Client.get")
    def test_init_with_custom_base_url(self, mock_get):
       
        custom_url = "http://custom-api-url.com"

        custom_service = InvoiceService(base_url=custom_url)

        self.assertEqual(custom_service.base_url, custom_url)

    @patch("httpx.Client.get")
    def test_lists_all_invoices(self, mock_get):
        invoices_data = [
            {"id": 1, "provider": "Provider A", "total_value": 100.0},
            {"id": 2, "provider": "Provider B", "total_value": 200.0},
        ]

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = invoices_data

        invoices = self.service.list_invoices()

        self.assertEqual(invoices, invoices_data)

    @patch("httpx.Client.post")
    def test_creates_invoice(self, mock_post):
        
        invoice = Invoice.objects.create(
            provider="Provider A",
            concept="Product Purchase",
            base_value=100.0,
            vat=21.0,
            total_value=121.0,
            date="2025-02-08",
            state=InvoiceStates.PENDING.value,
        )

        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {**invoice.__dict__, "id": 1}  

        created_invoice = self.service.create_invoice(invoice)

        self.assertEqual(created_invoice["provider"], "Provider A")
        self.assertEqual(created_invoice["concept"], "Product Purchase")
        self.assertEqual(created_invoice["total_value"], 121.0)
        self.assertEqual(created_invoice["date"], "2025-02-08")
        self.assertEqual(created_invoice["state"], InvoiceStates.PENDING.value)

    @patch("httpx.Client.get")
    def test_finds_invoice_by_id(self, mock_get):
        invoice_id = 1
        invoice_data = {
            "id": invoice_id,
            "provider": "Provider A",
            "concept": "Product Purchase",
            "base_value": 100.0,
            "vat": 21.0,
            "total_value": 121.0,
            "date": "2025-02-08",
            "state": InvoiceStates.PENDING.value,
        }

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = invoice_data

        retrieved_invoice = self.service.get_invoice(invoice_id)

        self.assertEqual(retrieved_invoice, invoice_data)

    @patch("httpx.Client.put")
    def test_updates_invoice(self, mock_put):
        invoice_id = 1
        update_data = {
            "concept": "Updated Concept",
            "total_value": 150.0,
        }
        updated_invoice_data = {
            "id": invoice_id,
            "provider": "Provider A",
            "concept": "Updated Concept",
            "base_value": 100.0,
            "vat": 21.0,
            "total_value": 150.0,
            "date": "2025-02-08",
            "state": InvoiceStates.PENDING.value,
        }

        mock_put.return_value.status_code = 200
        mock_put.return_value.json.return_value = updated_invoice_data

        updated_invoice = self.service.update_invoice(invoice_id, update_data)

        self.assertEqual(updated_invoice, updated_invoice_data)

    @patch("httpx.Client.delete")
    def test_deletes_invoice(self, mock_delete):
        invoice_id = 1
        mock_delete.return_value.status_code = 204

        response = self.service.delete_invoice(invoice_id)

        self.assertEqual(response, {"message": f"Invoice {invoice_id} deleted successfully"})

    @patch("httpx.Client.get")
    def test_filters_invoices(self, mock_get):
        filter_params = {"provider": "Provider A"}
        filtered_invoices_data = [
            {"id": 1, "provider": "Provider A", "total_value": 100.0},
        ]

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = filtered_invoices_data

        invoices = self.service.filter_invoices(**filter_params)

        self.assertEqual(invoices, filtered_invoices_data)

    @patch("httpx.Client.get")
    def test_generates_accounting_entries(self, mock_get):
        invoice_id = 1
        accounting_entries_data = [
            {"code": AccountingCodes.PURCHASES, "description": "DEBE Compras", "amount": 100.0},
            {"code": AccountingCodes.VAT_SUPPORTED, "description": "DEBE IVA Soportado", "amount": 21.0},
            {"code": AccountingCodes.SUPPLIERS, "description": "HABER Proveedores", "amount": 121.0},
        ]

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = accounting_entries_data

        entries = self.service.generate_accounting_entries(invoice_id)

        self.assertEqual(entries, accounting_entries_data)
        self.assertEqual(len(entries), 3)
        self.assertEqual(entries[0]["code"], AccountingCodes.PURCHASES)
        self.assertEqual(entries[0]["description"], "DEBE Compras")
        self.assertEqual(entries[0]["amount"], 100.0)
        self.assertEqual(entries[1]["code"], AccountingCodes.VAT_SUPPORTED)
        self.assertEqual(entries[1]["description"], "DEBE IVA Soportado")
        self.assertEqual(entries[1]["amount"], 21.0)
        self.assertEqual(entries[2]["code"], AccountingCodes.SUPPLIERS)
        self.assertEqual(entries[2]["description"], "HABER Proveedores")
        self.assertEqual(entries[2]["amount"], 121.0)

