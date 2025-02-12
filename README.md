## Setup Instructions

**Clone the Repository**  
```bash
git clone https://github.com/victor90braz/django-invoice-management-api.git
```

**Navigate to the Project Directory**  
```bash
cd Inmatic
```

**Python Installed**  
```bash
python --version
```

**Python Installed**  
```bash
pip --version
```

**Set Up the Virtual Environment**  
```bash
python -m venv venv
```

**Activate the Virtual Environment**  
- **Windows**:  
  ```bash
  venv\Scripts\activate
  ```  
- **Mac/Linux**:  
  ```bash
  source venv/bin/activate
  ```

**Create and Apply Migrations**  
```bash
python manage.py migrate
```

**Create a Superuser**  
```bash
python manage.py createsuperuser
```

**Run the Development Server**  
```bash
python manage.py runserver
```

**Access the Django Admin Panel**  
Visit `http://127.0.0.1:8000/admin` in your browser.

**Run Unit Tests**  
```bash
python manage.py test InvoicesAccounting.tests.unit
```

**Run Test Coverage**  
```bash
python -m coverage run manage.py test InvoicesAccounting.tests.unit
```  
Generate a report:  
```bash
python -m coverage report
```  
Generate an HTML report:  
```bash
python -m coverage html
```

---

## Features

- **Admin Panel**: Access the Django admin panel at `http://127.0.0.1:8000/admin`.
- **List Invoices**: Retrieve a list of invoices (`GET /invoices/`).
- **Invoice Details**: Retrieve details of a specific invoice (`GET /invoices/<int:invoice_id>/`).
- **Create Invoice**: Create a new invoice (`POST /invoices/create/`).
- **Update Invoice**: Update an existing invoice (`PUT /invoices/<int:invoice_id>/update/`).
- **Delete Invoice**: Delete an invoice (`DELETE /invoices/<int:invoice_id>/delete/`).
- **Filter Invoices**: Filter invoices based on query parameters (`GET /invoices/filter/`).
- **Generate Accounting Entries**: Generate accounting entries for an invoice (`GET /invoices/<int:invoice_id>/accounting-entries/`).
- **API Documentation**: View API documentation using Redoc at `http://127.0.0.1:8000/redoc/`.

---

## Validation and Serializer

### Validation in the View

When creating an invoice, the request data is validated using a serializer. If required fields like `date`, `base_value`, `vat`, or `total_value` are missing or invalid, a validation error is raised.

### Serializer Workflow

- The `ValidateInvoice` serializer validates incoming data. If the data is invalid, it returns errors.
- The model’s `clean()` method is called for additional validation, ensuring `base_value`, `vat`, and `total_value` are correct.

### Model's `clean()` Method

The `clean()` method in `InvoiceModel` performs the following checks:
- `base_value` must be greater than zero.
- `vat` must not be negative.
- `total_value` must match the sum of `base_value` and `vat`.