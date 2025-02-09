from typing import List, Dict
from django.forms import model_to_dict
import httpx
from Inmatic import settings
from InvoicesAccounting.models import Invoice

class InvoiceService:
    BASE_URL = settings.PAYMENT_API_BASE_URL

    def __init__(self, base_url=None):
        self.base_url = base_url or self.BASE_URL
        if not self.base_url:
            raise ValueError("BASE_URL is not configured. Please check your settings.")
        self.client = httpx.Client(base_url=self.base_url, timeout=30)

    def list_invoices(self) -> List[Dict]:
        """
        Fetch all invoices from the system.

        Returns:
            list[dict]: A list of invoices.
        """
        response = self.client.get("/invoices")
        response.raise_for_status()
        return response.json()

    def create_invoice(self, data: Invoice) -> Dict:
        """
        Create a new invoice.

        Args:
            data (dict): The data to create a new invoice.

        Returns:
            dict: The newly created invoice.
        """
        response = self.client.post("/invoices", json=model_to_dict(data))
        response.raise_for_status()
        return response.json()

    def get_invoice(self, invoice_id: int) -> Dict:
        """
        Fetch an invoice by its ID.

        Args:
            invoice_id (int): The ID of the invoice.

        Returns:
            dict: The invoice details.
        """
        response = self.client.get(f"/invoice/{invoice_id}/")  
        response.raise_for_status()
        return response.json()


    def update_invoice(self, invoice_id: int, data: Dict) -> Dict:
        """
        Update an existing invoice.

        Args:
            invoice_id (int): The ID of the invoice.
            data (dict): The data to update the invoice.

        Returns:
            dict: The updated invoice.
        """
        response = self.client.put(f"/invoices/{invoice_id}", json=data)
        response.raise_for_status()
        return response.json()

    def delete_invoice(self, invoice_id: int) -> Dict:
        """
        Delete an invoice by its ID.

        Args:
            invoice_id (int): The ID of the invoice.

        Returns:
            dict: A message indicating successful deletion.
        """
        response = self.client.delete(f"/invoices/{invoice_id}")
        response.raise_for_status()
        return {"message": f"Invoice {invoice_id} deleted successfully"}

    def filter_invoices(self, **params) -> List[Dict]:
        """
        Filter invoices based on query parameters.

        Args:
            **params: Filter parameters.

        Returns:
            list[dict]: The filtered list of invoices.
        """
        response = self.client.get("/invoices", params=params)
        response.raise_for_status()
        return response.json()

    def generate_accounting_entries(self, invoice_id: int) -> Dict:
        """
        Generate accounting entries for a given invoice.

        Args:
            invoice_id (int): The ID of the invoice.

        Returns:
            dict: The generated accounting entries.
        """
        response = self.client.get(f"/invoices/{invoice_id}/accounting-entries")
        response.raise_for_status()        
        return response.json()
