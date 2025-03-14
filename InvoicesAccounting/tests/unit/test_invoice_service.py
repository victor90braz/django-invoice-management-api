from decimal import Decimal
from unittest.mock import patch
from django.test import TestCase
from Inmatic import settings
from InvoicesAccounting.app.enums.accounting_codes import AccountingCodes
from InvoicesAccounting.app.enums.invoice_states import InvoiceStates
from InvoicesAccounting.app.services.invoice_service import InvoiceService

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
        # Arrange
        invoices_data = [
            {
                "provider": "Provider A",
                "concept": "Concept A",
                "base_value": "100.00",  
                "vat": "21.00",
                "total_value": "121.00",
                "date": "2025-02-08",
                "state": InvoiceStates.PENDING.value  
            },
            {
                "provider": "Provider B",
                "concept": "Concept B",
                "base_value": "200.00",
                "vat": "42.00",
                "total_value": "242.00",
                "date": "2025-02-11",
                "state": InvoiceStates.ACCOUNTED.value  
            },
        ]
        
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = invoices_data

        # Act
        response = self.service.list_invoices()

        # Assert
        self.assertEqual(len(response), len(invoices_data))  

        for index in range(len(response)):
            actual = response[index]
            expected = invoices_data[index]
            
            self.assertEqual(actual["provider"], expected["provider"])
            self.assertEqual(Decimal(actual["base_value"]), Decimal(expected["base_value"]))
            self.assertEqual(Decimal(actual["vat"]), Decimal(expected["vat"]))
            self.assertEqual(Decimal(actual["total_value"]), Decimal(expected["total_value"]))

    @patch("httpx.Client.post")
    def test_invoice_service_creates_invoice(self, mock_post):
        # Arrange
        invoice_data = {
            "provider": "Provider A",
            "concept": "Product Purchase",
            "base_value": Decimal("100.00"),
            "vat": Decimal("21.00"),
            "total_value": Decimal("121.00"),
            "date": "2025-02-08",
            "state": InvoiceStates.PENDING.value,
        }
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {**invoice_data, "id": 1}

        # Act
        created_invoice = self.service.create_invoice(invoice_data)

        # Assert
        self.assertEqual(created_invoice["provider"], "Provider A")
        self.assertEqual(created_invoice["concept"], "Product Purchase")
        self.assertEqual(created_invoice["total_value"], Decimal("121.00"))
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
            "base_value": Decimal("100.00"),
            "vat": Decimal("21.00"),
            "total_value": Decimal("121.00"),
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
            "total_value": Decimal("150.00"),
        }
        updated_invoice_data = {
            "id": invoice_id,
            "provider": "Provider A",
            "concept": "Updated Concept",
            "base_value": Decimal("100.00"),
            "vat": Decimal("21.00"),
            "total_value": Decimal("150.00"),
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
        filter_params = {
            "state": InvoiceStates.PENDING.value, 
            "start_date": "2025-02-01", 
            "end_date": "2025-02-10"
        }
        
        filtered_invoices_data = [
            {
                "id": 1,
                "provider": "Provider A",
                "concept": "Service A",
                "base_value": "100.00",
                "vat": "21.00",
                "total_value": "121.00",
                "date": "2025-02-05",
                "state": InvoiceStates.PENDING.value,
            },
            {
                "id": 2,
                "provider": "Provider B",
                "concept": "Service B",
                "base_value": "150.00",
                "vat": "31.50",
                "total_value": "181.50",
                "date": "2025-02-07",
                "state": InvoiceStates.PENDING.value,
            },
        ]

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = filtered_invoices_data

        # Act
        response = self.service.filter_invoices(**filter_params)

        # Assert
        self.assertEqual(len(response), len(filtered_invoices_data))

        for index, actual in enumerate(response):
            expected = filtered_invoices_data[index]

            self.assertEqual(actual["id"], expected["id"])
            self.assertEqual(actual["provider"], expected["provider"])
            self.assertEqual(actual["concept"], expected["concept"])
            self.assertEqual(actual["state"], expected["state"])
            self.assertEqual(Decimal(actual["base_value"]), Decimal(expected["base_value"]))
            self.assertEqual(Decimal(actual["vat"]), Decimal(expected["vat"]))
            self.assertEqual(Decimal(actual["total_value"]), Decimal(expected["total_value"]))
            self.assertEqual(actual["date"], expected["date"])

    @patch("httpx.Client.get")
    def test_invoice_service_generates_accounting_entries(self, mock_get):
        # Arrange
        invoice_id = 1
        accounting_entries_data = [
            {"account": AccountingCodes.PURCHASES.value, "description": AccountingCodes.PURCHASES.label, "amount": Decimal("100.00")},
            {"account": AccountingCodes.VAT_SUPPORTED.value, "description": AccountingCodes.VAT_SUPPORTED.label, "amount": Decimal("21.00")},
            {"account": AccountingCodes.SUPPLIERS.value, "description": AccountingCodes.SUPPLIERS.label, "amount": Decimal("121.00")},
        ]
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = accounting_entries_data 

        # Act
        response = self.service.generate_accounting_entries(invoice_id)

        # Assert
        self.assertIn("entries", response)
        self.assertEqual(len(response["entries"]), 3)

        # Validate first entry (Purchases)
        first_entry = response["entries"][0]
        self.assertEqual(first_entry["account"], AccountingCodes.PURCHASES.value)
        self.assertEqual(first_entry["description"], AccountingCodes.PURCHASES.label)
        self.assertEqual(first_entry["amount"], float(Decimal("100.00")))

        # Validate second entry (VAT Supported)
        second_entry = response["entries"][1]
        self.assertEqual(second_entry["account"], AccountingCodes.VAT_SUPPORTED.value)
        self.assertEqual(second_entry["description"], AccountingCodes.VAT_SUPPORTED.label)
        self.assertEqual(second_entry["amount"], float(Decimal("21.00")))

        # Validate third entry (Suppliers)
        third_entry = response["entries"][2]
        self.assertEqual(third_entry["account"], AccountingCodes.SUPPLIERS.value)
        self.assertEqual(third_entry["description"], AccountingCodes.SUPPLIERS.label)
        self.assertEqual(third_entry["amount"], float(Decimal("121.00")))

