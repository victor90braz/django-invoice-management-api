from unittest.mock import patch
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from InvoicesAccounting.app.enum.invoice_states import InvoiceStates
from InvoicesAccounting.models import Invoice
import json

class InvoiceViewTest(TestCase):

    def setUp(self):
        self.client = Client()

        # Arrange: Set up test user and log in
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")

        # Arrange: Set up initial data
        self.invoice = Invoice.objects.create(
            provider="Provider A",
            concept="Test Concept",
            base_value=100.0,
            vat=20.0,
            total_value=120.0,
            date="2025-02-10",
            state=InvoiceStates.PENDING.value,
        )

        # Arrange: Prepare a valid payload
        self.valid_payload = {
            "provider": "Provider B",
            "concept": "New Invoice",
            "base_value": 200.0,
            "vat": 40.0,
            "total_value": 240.0,
            "date": "2025-02-11",
            "state": InvoiceStates.PENDING.value,
        }

    @patch("InvoicesAccounting.resources.views.invoice_view.InvoiceService.list_invoices")
    def test_list_invoices(self, mock_list_invoices):
        # Arrange
        mock_list_invoices.return_value = [
            {"id": self.invoice.id, "provider": self.invoice.provider, "total_value": self.invoice.total_value}
        ]

        # Act
        response = self.client.get(reverse('invoices-list'))

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.invoice.provider)

    @patch("InvoicesAccounting.resources.views.invoice_view.InvoiceService.get_invoice")
    def test_get_invoice_by_id(self, mock_get_invoice):
        # Arrange
        mock_get_invoice.return_value = {
            "id": self.invoice.id,
            "provider": self.invoice.provider,
            "concept": self.invoice.concept,
            "total_value": self.invoice.total_value,
            "date": self.invoice.date,
            "state": self.invoice.state,
        }

        # Act
        response = self.client.get(reverse('invoice-get-id', args=[self.invoice.id]))

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.invoice.provider)

    @patch("InvoicesAccounting.resources.views.invoice_view.InvoiceService.create_invoice")
    def test_create_invoice_needs_authentication(self, mock_create_invoice):
        # Arrange
        mock_create_invoice.return_value = {**self.valid_payload, "id": 2}

        # Act
        response = self.client.post(
            reverse('invoice-create'),
            data=json.dumps(self.valid_payload),
            content_type="application/json"
        )

        # Assert
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["provider"], self.valid_payload["provider"])

    @patch("InvoicesAccounting.resources.views.invoice_view.InvoiceService.create_invoice")
    def test_create_invoice_without_user_identification(self, mock_create_invoice):
        # Arrange
        mock_create_invoice.return_value = {**self.valid_payload, "id": 2}
        self.client.logout()

        # Act
        response = self.client.post(
            reverse('invoice-create'),
            data=json.dumps(self.valid_payload),
            content_type="application/json"
        )

        # Assert
        self.assertEqual(response.status_code, 401)
        self.assertIn("Authentication required", response.json().get("error", ""))

    @patch("InvoicesAccounting.resources.views.invoice_view.InvoiceService.update_invoice")
    def test_update_invoice_needs_authentication(self, mock_update_invoice):
        # Arrange
        updated_data = {**self.valid_payload, "concept": "Updated Concept"}
        mock_update_invoice.return_value = updated_data

        # Act
        response = self.client.put(
            reverse('invoice-update', args=[self.invoice.id]),
            data=json.dumps(updated_data),
            content_type="application/json"
        )

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["concept"], "Updated Concept")

    @patch("InvoicesAccounting.resources.views.invoice_view.InvoiceService.delete_invoice")
    def test_delete_invoice_needs_authentication(self, mock_delete_invoice):
        # Arrange
        mock_delete_invoice.return_value = {"message": "Invoice deleted successfully"}

        # Act
        response = self.client.delete(reverse('invoice-delete', args=[self.invoice.id]))

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Invoice deleted successfully")

    @patch("InvoicesAccounting.resources.views.invoice_view.InvoiceService.get_invoice")
    def test_retrieve_invoice_ok_status(self, mock_get_invoice):
        # Arrange
        mock_get_invoice.return_value = {
            "id": self.invoice.id,
            "provider": self.invoice.provider,
            "concept": self.invoice.concept,
            "base_value": str(self.invoice.base_value),
            "vat": str(self.invoice.vat),
            "total_value": str(self.invoice.total_value),
            "date": str(self.invoice.date),
            "state": self.invoice.state,
        }

        # Act
        response = self.client.get(f"/invoice/{self.invoice.id}/")

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], self.invoice.id)
        self.assertEqual(response.json()["provider"], self.invoice.provider)

    @patch("InvoicesAccounting.resources.views.invoice_view.InvoiceService.get_invoice")
    def test_retrieve_invoice_not_found(self, mock_get_invoice):
        # Arrange
        mock_get_invoice.return_value = None

        # Act
        response = self.client.get(reverse('invoice-get-id', args=[999]))

        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"], "Invoice not found")

    def test_create_invoice_invalid_json_needs_authentication(self):
        # Arrange
        invalid_json = "invalid json"

        # Act
        response = self.client.post(
            reverse('invoice-create'),
            data=invalid_json,
            content_type="application/json"
        )

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Invalid JSON")

    def test_create_invoice_missing_required_fields_needs_authentication(self):
        # Arrange
        invalid_payload = {"provider": "Provider B"}

        # Act
        response = self.client.post(
            reverse('invoice-create'),
            data=json.dumps(invalid_payload),
            content_type="application/json"
        )

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    @patch("InvoicesAccounting.resources.views.invoice_view.InvoiceService.update_invoice")
    def test_update_invoice_not_found_needs_authentication(self, mock_update_invoice):
        # Arrange
        mock_update_invoice.return_value = None
        updated_data = {**self.valid_payload, "concept": "Updated Concept"}

        # Act
        response = self.client.put(
            reverse('invoice-update', args=[999]),
            data=json.dumps(updated_data),
            content_type="application/json"
        )

        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"], "Invoice not found")

    @patch("InvoicesAccounting.resources.views.invoice_view.InvoiceService.delete_invoice")
    def test_delete_invoice_not_found_needs_authentication(self, mock_delete_invoice):
        # Arrange
        mock_delete_invoice.return_value = False

        # Act
        response = self.client.delete(reverse('invoice-delete', args=[999]))

        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"], "Invoice not found")

    @patch("InvoicesAccounting.resources.views.invoice_view.InvoiceService.filter_invoices")
    def test_filter_invoices_with_invalid_filters(self, mock_filter_invoices):
        # Arrange
        mock_filter_invoices.side_effect = Exception("Invalid filters")

        # Act
        response = self.client.get(reverse('invoice-filter'), data={"invalid_filter": "value"})

        # Assert
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json())

    @patch("InvoicesAccounting.resources.views.invoice_view.InvoiceService.generate_accounting_entries")
    def test_generate_accounting_entries_not_found(self, mock_generate_accounting_entries):
        # Arrange
        mock_generate_accounting_entries.return_value = None

        # Act
        response = self.client.get(reverse('invoice-generate-accounting-entries', args=[999]))

        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"], "Invoice not found")

    @patch("InvoicesAccounting.resources.views.invoice_view.InvoiceService.list_invoices")
    def test_simulate_an_exception_500_in_list_invoices(self, mock_list_invoices):
        # Arrange: Simulate an exception in InvoiceService.list_invoices
        mock_list_invoices.side_effect = Exception("Test exception")

        # Act
        response = self.client.get(reverse('invoices-list'))

        # Assert
        self.assertEqual(response.status_code, 500)
        self.assertIn("An error occurred while listing invoices", response.json().get("error", ""))

    @patch("InvoicesAccounting.resources.views.invoice_view.InvoiceService.get_invoice")
    def test_simulate_an_exception_500_in_retrieve_invoice(self, mock_list_invoices):
        # Arrange: Simulate an exception in InvoiceService.retrieve_invoice
        mock_list_invoices.side_effect = Exception("Test exception")
        
        # Pass a valid invoice_id to the URL reverse lookup
        invoice_id = 1  # Or any valid invoice ID you want to test
        url = reverse('invoice-get-id', args=[invoice_id])

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, 500)
        self.assertIn("An error occurred while retrieving the invoice", response.json().get("error", ""))
