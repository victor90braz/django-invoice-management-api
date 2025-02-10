from decimal import Decimal
from unittest.mock import patch
from django.test import TestCase
from Inmatic import settings
from InvoicesAccounting.app.enums.accounting_codes import AccountingCodes
from InvoicesAccounting.app.enums.invoice_states import InvoiceStates
from InvoicesAccounting.app.services.invoice_service import InvoiceService
from InvoicesAccounting.app.models.invoice_model import InvoiceModel


class InvoiceServiceTest(TestCase):

    def setUp(self):
        self.service = InvoiceService(base_url=settings.PAYMENT_API_BASE_URL)

    @patch("httpx.Client.get")
    def test_invoice_service_initialized_with_custom_base_url(self, mock_get):
        # Arrange
        custom_url = "http://custom-api-url.com"

        # Act
        custom_service = InvoiceService(base_url=custom_url)

        # Assert
        self.assertEqual(custom_service.base_url, custom_url)

    @patch("httpx.Client.get")
    def test_invoice_service_lists_all_invoices(self, mock_get):
        # Arrange: Mock API response with valid states and Decimal values for numeric fields
        invoices_data = [
            {
                "provider": "Provider A",
                "concept": "Concept A",
                "base_value": Decimal("100.00"),
                "vat": Decimal("21.00"),
                "total_value": Decimal("121.00"),
                "date": "2025-02-08",
                "state": InvoiceStates.PENDING.value  # Use enum value
            },
            {
                "provider": "Provider B",
                "concept": "Concept B",
                "base_value": Decimal("200.00"),
                "vat": Decimal("42.00"),
                "total_value": Decimal("242.00"),
                "date": "2025-02-11",
                "state": InvoiceStates.ACCOUNTED.value  # Use enum value
            },
        ]
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = invoices_data

        # Act: Call the API
        invoices = self.service.list_invoices()

        # Assert: Ensure the mock data and actual return data match
        self.assertEqual(invoices, invoices_data)

    @patch("httpx.Client.post")
    def test_invoice_service_creates_invoice(self, mock_post):
        # Arrange
        invoice = InvoiceModel.objects.create(
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

        # Act
        created_invoice = self.service.create_invoice(invoice)

        # Assert
        self.assertEqual(created_invoice["provider"], "Provider A")
        self.assertEqual(created_invoice["concept"], "Product Purchase")
        self.assertEqual(created_invoice["total_value"], 121.0)
        self.assertEqual(created_invoice["date"], "2025-02-08")
        self.assertEqual(created_invoice["state"], InvoiceStates.PENDING.value)

    @patch("httpx.Client.get")
    def test_invoice_service_finds_invoice_by_id(self, mock_get):
        # Arrange
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

        # Act
        retrieved_invoice = self.service.get_invoice(invoice_id)

        # Assert
        self.assertEqual(retrieved_invoice, invoice_data)

    @patch("httpx.Client.put")
    def test_invoice_service_updates_invoice(self, mock_put):
        # Arrange
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

        # Act
        updated_invoice = self.service.update_invoice(invoice_id, update_data)

        # Assert
        self.assertEqual(updated_invoice, updated_invoice_data)

    @patch("httpx.Client.delete")
    def test_invoice_service_deletes_invoice(self, mock_delete):
        # Arrange
        invoice_id = 1
        mock_delete.return_value.status_code = 204

        # Act
        response = self.service.delete_invoice(invoice_id)

        # Assert
        self.assertEqual(response, {"message": f"Invoice {invoice_id} deleted successfully"})

    @patch("httpx.Client.get")
    def test_invoice_service_filters_invoices(self, mock_get):
        # Arrange
        filter_params = {"provider": "Provider A"}
        filtered_invoices_data = [
            {"id": 1, "provider": "Provider A", "total_value": 100.0},
        ]
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = filtered_invoices_data

        # Act
        invoices = self.service.filter_invoices(**filter_params)

        # Assert
        self.assertEqual(invoices, filtered_invoices_data)

    @patch("httpx.Client.get")
    def test_invoice_service_generates_accounting_entries(self, mock_get):
        # Arrange
        invoice_id = 1
        accounting_entries_data = [
            {"code": AccountingCodes.PURCHASES, "description": "DEBE Compras", "amount": 100.0},
            {"code": AccountingCodes.VAT_SUPPORTED, "description": "DEBE IVA Soportado", "amount": 21.0},
            {"code": AccountingCodes.SUPPLIERS, "description": "HABER Proveedores", "amount": 121.0},
        ]
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = accounting_entries_data

        # Act
        entries = self.service.generate_accounting_entries(invoice_id)

        # Assert
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
