from datetime import date
from django.core.exceptions import ValidationError
from django.test import TestCase
from InvoicesAccounting.enum.accounting_codes import AccountingCodes
from InvoicesAccounting.models import Invoice
from InvoicesAccounting.services.invoice_service import InvoiceService
from InvoicesAccounting.enum.invoice_states import InvoiceStates


class InvoiceServiceTest(TestCase):

    def test_creates_invoice(self):
        invoice_data = {
            "provider": "Provider A",
            "concept": "Product Purchase",
            "base_value": 100.0,
            "vat": 21.0,
            "total_value": 121.0,
            "date": date(2025, 2, 8),
            "state": InvoiceStates.PENDING.value,
        }

        created_invoice = InvoiceService().create(invoice_data)

        self.assertEqual(created_invoice["provider"], "Provider A")
        self.assertEqual(created_invoice["concept"], "Product Purchase")
        self.assertEqual(float(created_invoice["base_value"]), 100.0)
        self.assertEqual(float(created_invoice["vat"]), 21.0)
        self.assertEqual(float(created_invoice["total_value"]), 121.0)
        self.assertEqual(created_invoice["date"], "2025-02-08")
        self.assertEqual(created_invoice["state"], InvoiceStates.PENDING.value)
        self.assertTrue(Invoice.objects.filter(id=created_invoice["id"]).exists())

    def test_finds_invoice_by_id(self):
        invoice = Invoice.objects.create(
            provider="Provider A",
            concept="Product Purchase",
            base_value=100.0,
            vat=21.0,
            total_value=121.0,
            date=date(2025, 2, 8),
            state=InvoiceStates.PENDING.value,
        )

        invoice_data = InvoiceService().find_by_id(invoice.id)

        self.assertEqual(invoice_data["provider"], "Provider A")
        self.assertEqual(invoice_data["concept"], "Product Purchase")
        self.assertEqual(float(invoice_data["base_value"]), 100.0)
        self.assertEqual(float(invoice_data["vat"]), 21.0)
        self.assertEqual(float(invoice_data["total_value"]), 121.0)
        self.assertEqual(invoice_data["date"], "2025-02-08")
        self.assertEqual(invoice_data["state"], InvoiceStates.PENDING.value)

    def test_updates_invoice(self):
        invoice = Invoice.objects.create(
            provider="Provider A",
            concept="Product Purchase",
            base_value=100.0,
            vat=21.0,
            total_value=121.0,
            date=date(2025, 2, 8),
            state=InvoiceStates.PENDING.value,
        )

        updated_data = {
            "concept": "Updated Concept",
            "total_value": 130.0,
        }

        updated_invoice = InvoiceService().update(invoice.id, updated_data)

        self.assertEqual(updated_invoice["concept"], "Updated Concept")
        self.assertEqual(float(updated_invoice["total_value"]), 130.0)
        self.assertEqual(updated_invoice["provider"], "Provider A")
        self.assertEqual(float(updated_invoice["base_value"]), 100.0)
        self.assertEqual(float(updated_invoice["vat"]), 21.0)
        self.assertEqual(updated_invoice["date"], "2025-02-08")
        self.assertEqual(updated_invoice["state"], InvoiceStates.PENDING.value)

    def test_deletes_invoice(self):
        invoice = Invoice.objects.create(
            provider="Provider A",
            concept="Product Purchase",
            base_value=100.0,
            vat=21.0,
            total_value=121.0,
            date=date(2025, 2, 8),
            state=InvoiceStates.PENDING.value,
        )

        response = InvoiceService().delete(invoice.id)

        self.assertEqual(response, {"message": f"Invoice {invoice.id} deleted successfully"})
        self.assertFalse(Invoice.objects.filter(id=invoice.id).exists())

    def test_create_invoice_with_invalid_state(self):
        invalid_invoice_data = {
            "provider": "Provider B",
            "concept": "Invalid State",
            "base_value": 200.0,
            "vat": 42.0,
            "total_value": 242.0,
            "date": date(2025, 3, 1),
            "state": "InvalidState",
        }

        with self.assertRaises(ValidationError) as context:
            InvoiceService().create(invalid_invoice_data)

        self.assertEqual(str(context.exception), "['Invalid invoice state']")

    def test_generates_accounting_entries_for_paid_invoice(self):
        invoice = Invoice.objects.create(
            provider="Provider A",
            concept="Product Purchase",
            base_value=100.0,
            vat=21.0,
            total_value=121.0,
            date=date(2025, 2, 8),
            state=InvoiceStates.PAID.value,
        )

        accounting_entries = InvoiceService().generate_accounting_entries(invoice.id)

        expected_entries = {
            "DEBE": [
                {"account": AccountingCodes.PURCHASES.value, "amount": 100.0},
                {"account": AccountingCodes.VAT_SUPPORTED.value, "amount": 21.0},
            ],
            "HABER": [
                {"account": AccountingCodes.SUPPLIERS.value, "amount": 121.0},
            ],
        }

        self.assertEqual(accounting_entries, expected_entries)

    def test_raises_error_when_generating_accounting_entries_for_non_paid_invoice(self):
        invoice = Invoice.objects.create(
            provider="Provider A",
            concept="Product Purchase",
            base_value=100.0,
            vat=21.0,
            total_value=121.0,
            date=date(2025, 2, 8),
            state=InvoiceStates.PENDING.value,
        )

        with self.assertRaises(ValidationError) as context:
            InvoiceService().generate_accounting_entries(invoice.id)

        self.assertEqual(str(context.exception), "['Accounting entries can only be generated for invoices in the PAID state.']")

    def test_filters_invoices(self):
        Invoice.objects.create(
            provider="Provider A",
            concept="Product A",
            base_value=100.0,
            vat=21.0,
            total_value=121.0,
            date=date(2025, 2, 8),
            state=InvoiceStates.PENDING.value,
        )

        Invoice.objects.create(
            provider="Provider B",
            concept="Product B",
            base_value=200.0,
            vat=42.0,
            total_value=242.0,
            date=date(2025, 3, 1),
            state=InvoiceStates.PAID.value,
        )

        filtered_by_state = InvoiceService().find_all(state=InvoiceStates.PENDING.value)
        self.assertEqual(len(filtered_by_state), 1)

        filtered_by_date = InvoiceService().find_all(start_date=date(2025, 2, 1), end_date=date(2025, 2, 28))
        self.assertEqual(len(filtered_by_date), 1)
        self.assertEqual(filtered_by_date[0]["date"], "2025-02-08")
