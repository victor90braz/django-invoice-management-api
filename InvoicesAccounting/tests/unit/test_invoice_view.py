from django.test import TestCase, Client
from django.urls import reverse
from datetime import date
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
            date=date(2025, 2, 10),
            state=InvoiceStates.PENDING.value
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

    def test_list_invoices(self):
        response = self.client.get(reverse('invoice-list'))
        self.assertEqual(response.status_code, 200)

    def test_get_invoice_by_id(self):
        response = self.client.get(reverse('invoice-get', args=[self.invoice.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.invoice.provider)

    def test_create_invoice(self):
        response = self.client.post(reverse('invoice-create'), data=self.valid_payload, content_type="application/json")
        self.assertEqual(response.status_code, 201)

    def test_update_invoice(self):
        response = self.client.put(
            reverse('invoice-update', args=[self.invoice.id]),
            data=self.valid_payload,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_invoice_by_id(self):
        response = self.client.delete(reverse('invoice-delete', args=[self.invoice.id]))
        self.assertEqual(response.status_code, 200)
