from unittest.mock import patch
from django.test import TestCase, Client
from django.urls import reverse
from InvoicesAccounting.models import Invoice
from InvoicesAccounting.enum.invoice_states import InvoiceStates

class InvoiceViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.invoice = Invoice.objects.create(
            provider="Provider A",
            concept="Test Concept",
            base_value=100.0,
            vat=20.0,
            total_value=120.0,
            date="2025-02-10",
            state=InvoiceStates.PENDING.value,
        )
        self.valid_payload = {
            "provider": "Provider B",
            "concept": "New Invoice",
            "base_value": 200.0,
            "vat": 40.0,
            "total_value": 240.0,
            "date": "2025-02-11",
            "state": InvoiceStates.PENDING.value,
        }

    @patch("InvoicesAccounting.services.invoice_service.InvoiceService.list_invoices")
    def test_list_invoices(self, mock_list_invoices):
        mock_list_invoices.return_value = [
            {"id": self.invoice.id, "provider": self.invoice.provider, "total_value": self.invoice.total_value}
        ]
        response = self.client.get(reverse('invoice-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.invoice.provider)

    @patch("InvoicesAccounting.services.invoice_service.InvoiceService.get_invoice")
    def test_get_invoice_by_id(self, mock_get_invoice):
        mock_get_invoice.return_value = {
            "id": self.invoice.id,
            "provider": self.invoice.provider,
            "concept": self.invoice.concept,
            "total_value": self.invoice.total_value,
            "date": self.invoice.date,
            "state": self.invoice.state,
        }
        response = self.client.get(reverse('invoice-get-id', args=[self.invoice.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.invoice.provider)

    @patch("InvoicesAccounting.services.invoice_service.InvoiceService.create_invoice")
    def test_create_invoice(self, mock_create_invoice):
        mock_create_invoice.return_value = {**self.valid_payload, "id": 2}
        response = self.client.post(reverse('invoice-create'), data=self.valid_payload, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["provider"], self.valid_payload["provider"])

    @patch("InvoicesAccounting.services.invoice_service.InvoiceService.update_invoice")
    def test_update_invoice(self, mock_update_invoice):
        updated_data = {**self.valid_payload, "concept": "Updated Concept"}
        mock_update_invoice.return_value = updated_data
        response = self.client.put(
            reverse('invoice-update', args=[self.invoice.id]),
            data=updated_data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["concept"], "Updated Concept")

    @patch("InvoicesAccounting.services.invoice_service.InvoiceService.delete_invoice")
    def test_delete_invoice_by_id(self, mock_delete_invoice):
        mock_delete_invoice.return_value = {"message": "Invoice deleted successfully"}
        response = self.client.delete(reverse('invoice-delete', args=[self.invoice.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Invoice deleted successfully")

    @patch("InvoicesAccounting.services.invoice_service.InvoiceService.get_invoice")
    def test_it_status_ok(self, mock_get_invoice):

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

        response = self.client.get(f"/invoice/{self.invoice.id}/")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], self.invoice.id)
        self.assertEqual(response.json()["provider"], self.invoice.provider)

